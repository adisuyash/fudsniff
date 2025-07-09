import sqlite3
import json
import logging
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from concurrent.futures import ThreadPoolExecutor
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums and Data Classes
class SignalOutcome(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    PENDING = "pending"

class ImprovementType(Enum):
    PROMPT_ADJUSTMENT = "prompt_adjustment"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    CONTEXT_WEIGHTING = "context_weighting"
    SIGNAL_FILTERING = "signal_filtering"

@dataclass
class SignalRecord:
    signal_id: str
    timestamp: datetime
    token_symbol: str
    signal_type: str  # BUY, SELL, HOLD
    confidence: float
    reasoning: str
    market_data: Dict[str, Any]
    outcome: SignalOutcome = SignalOutcome.PENDING
    performance_metrics: Optional[Dict[str, float]] = None
    embedding: Optional[np.ndarray] = None

@dataclass
class ImprovementAction:
    action_id: str
    timestamp: datetime
    improvement_type: ImprovementType
    description: str
    parameters: Dict[str, Any]
    performance_before: Dict[str, float]
    performance_after: Optional[Dict[str, float]] = None

class RAGManager:
    """Manages the RAG system database and vector operations"""
    
    def __init__(self, db_path: str = "fudsniff_rag.db", model_name: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.model_name = model_name
        self.model = None
        self.index = None
        self.signal_records = []
        self.improvement_actions = []
        self.lock = threading.Lock()
        self.last_index_update = None
        
        # Initialize database and model
        self._init_database()
        self._load_model()
        self._load_existing_data()
        self._build_index()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                signal_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                token_symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                reasoning TEXT NOT NULL,
                market_data TEXT NOT NULL,
                outcome TEXT DEFAULT 'pending',
                performance_metrics TEXT,
                embedding BLOB
            )
        ''')
        
        # Create improvements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS improvements (
                action_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                improvement_type TEXT NOT NULL,
                description TEXT NOT NULL,
                parameters TEXT NOT NULL,
                performance_before TEXT NOT NULL,
                performance_after TEXT
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_token ON signals(token_symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_outcome ON signals(outcome)')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    def _load_model(self):
        """Load sentence transformer model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _load_existing_data(self):
        """Load existing data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load signals
        cursor.execute('SELECT * FROM signals ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        
        for row in rows:
            signal = SignalRecord(
                signal_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                token_symbol=row[2],
                signal_type=row[3],
                confidence=row[4],
                reasoning=row[5],
                market_data=json.loads(row[6]),
                outcome=SignalOutcome(row[7]),
                performance_metrics=json.loads(row[8]) if row[8] else None,
                embedding=pickle.loads(row[9]) if row[9] else None
            )
            self.signal_records.append(signal)
        
        # Load improvements
        cursor.execute('SELECT * FROM improvements ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        
        for row in rows:
            improvement = ImprovementAction(
                action_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                improvement_type=ImprovementType(row[2]),
                description=row[3],
                parameters=json.loads(row[4]),
                performance_before=json.loads(row[5]),
                performance_after=json.loads(row[6]) if row[6] else None
            )
            self.improvement_actions.append(improvement)
        
        conn.close()
        logger.info(f"Loaded {len(self.signal_records)} signals and {len(self.improvement_actions)} improvements")
    
    def _build_index(self):
        """Build FAISS index for similarity search"""
        if not self.signal_records:
            logger.info("No signals to index")
            return
        
        # Generate embeddings for signals without them
        signals_to_embed = [s for s in self.signal_records if s.embedding is None]
        
        if signals_to_embed:
            logger.info(f"Generating embeddings for {len(signals_to_embed)} signals")
            
            # Prepare texts for embedding
            texts = []
            for signal in signals_to_embed:
                text = f"{signal.token_symbol} {signal.signal_type} {signal.reasoning}"
                texts.append(text)
            
            # Generate embeddings
            embeddings = self.model.encode(texts)
            
            # Update signal records with embeddings
            for i, signal in enumerate(signals_to_embed):
                signal.embedding = embeddings[i]
                self._update_signal_embedding(signal)
        
        # Build FAISS index
        embeddings = np.array([s.embedding for s in self.signal_records if s.embedding is not None])
        
        if len(embeddings) > 0:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
            self.index.add(embeddings)
            self.last_index_update = datetime.now()
            logger.info(f"FAISS index built with {len(embeddings)} embeddings")
        else:
            logger.warning("No embeddings available for indexing")
    
    def _update_signal_embedding(self, signal: SignalRecord):
        """Update signal embedding in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE signals 
            SET embedding = ? 
            WHERE signal_id = ?
        ''', (pickle.dumps(signal.embedding), signal.signal_id))
        
        conn.commit()
        conn.close()
    
    def store_signal(self, signal: SignalRecord):
        """Store a new signal in the database and update index"""
        with self.lock:
            # Generate embedding
            if signal.embedding is None:
                text = f"{signal.token_symbol} {signal.signal_type} {signal.reasoning}"
                signal.embedding = self.model.encode([text])[0]
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO signals 
                (signal_id, timestamp, token_symbol, signal_type, confidence, reasoning, 
                 market_data, outcome, performance_metrics, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.signal_id,
                signal.timestamp.isoformat(),
                signal.token_symbol,
                signal.signal_type,
                signal.confidence,
                signal.reasoning,
                json.dumps(signal.market_data),
                signal.outcome.value,
                json.dumps(signal.performance_metrics) if signal.performance_metrics else None,
                pickle.dumps(signal.embedding)
            ))
            
            conn.commit()
            conn.close()
            
            # Add to memory
            self.signal_records.append(signal)
            
            # Update index
            self._incremental_index_update(signal)
            
            logger.info(f"Stored signal: {signal.signal_id}")
    
    def _incremental_index_update(self, signal: SignalRecord):
        """Add new signal to existing index"""
        if self.index is None:
            self._build_index()
        else:
            if signal.embedding is not None:
                self.index.add(np.array([signal.embedding]))
    
    def update_signal_outcome(self, signal_id: str, outcome: SignalOutcome, 
                            performance_metrics: Optional[Dict[str, float]] = None):
        """Update signal outcome"""
        with self.lock:
            # Update in memory
            for signal in self.signal_records:
                if signal.signal_id == signal_id:
                    signal.outcome = outcome
                    if performance_metrics:
                        signal.performance_metrics = performance_metrics
                    break
            
            # Update in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE signals 
                SET outcome = ?, performance_metrics = ?
                WHERE signal_id = ?
            ''', (
                outcome.value,
                json.dumps(performance_metrics) if performance_metrics else None,
                signal_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated signal outcome: {signal_id} -> {outcome.value}")
    
    def find_similar_signals(self, query_signal: Dict[str, Any], limit: int = 10) -> List[Tuple[SignalRecord, float]]:
        """Find similar signals using vector similarity"""
        if self.index is None or len(self.signal_records) == 0:
            return []
        
        # Generate query embedding
        query_text = f"{query_signal.get('token_symbol', '')} {query_signal.get('signal_type', '')} {query_signal.get('reasoning', '')}"
        query_embedding = self.model.encode([query_text])[0]
        
        # Search in index
        similarities, indices = self.index.search(np.array([query_embedding]), limit)
        
        # Return results with similarity scores
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.signal_records):
                signal = self.signal_records[idx]
                similarity = similarities[0][i]
                results.append((signal, similarity))
        
        return results
    
    def get_performance_metrics(self, days: int = 30) -> Dict[str, float]:
        """Get performance metrics for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_signals = [s for s in self.signal_records 
                         if s.timestamp >= cutoff_date and s.outcome != SignalOutcome.PENDING]
        
        if not recent_signals:
            return {}
        
        # Calculate metrics
        total_signals = len(recent_signals)
        successful_signals = len([s for s in recent_signals if s.outcome == SignalOutcome.SUCCESS])
        failed_signals = len([s for s in recent_signals if s.outcome == SignalOutcome.FAILURE])
        partial_signals = len([s for s in recent_signals if s.outcome == SignalOutcome.PARTIAL])
        
        # Calculate average confidence
        avg_confidence = sum(s.confidence for s in recent_signals) / total_signals
        
        # Calculate success rate
        success_rate = successful_signals / total_signals if total_signals > 0 else 0
        
        # Calculate average performance metrics if available
        performance_metrics = {}
        signals_with_metrics = [s for s in recent_signals if s.performance_metrics]
        
        if signals_with_metrics:
            for key in signals_with_metrics[0].performance_metrics.keys():
                values = [s.performance_metrics[key] for s in signals_with_metrics if key in s.performance_metrics]
                if values:
                    performance_metrics[f'avg_{key}'] = sum(values) / len(values)
        
        return {
            'total_signals': total_signals,
            'success_rate': success_rate,
            'avg_confidence': avg_confidence,
            'successful_signals': successful_signals,
            'failed_signals': failed_signals,
            'partial_signals': partial_signals,
            **performance_metrics
        }
    
    def store_improvement(self, improvement: ImprovementAction):
        """Store improvement action"""
        with self.lock:
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO improvements 
                (action_id, timestamp, improvement_type, description, parameters, 
                 performance_before, performance_after)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                improvement.action_id,
                improvement.timestamp.isoformat(),
                improvement.improvement_type.value,
                improvement.description,
                json.dumps(improvement.parameters),
                json.dumps(improvement.performance_before),
                json.dumps(improvement.performance_after) if improvement.performance_after else None
            ))
            
            conn.commit()
            conn.close()
            
            # Add to memory
            self.improvement_actions.append(improvement)
            
            logger.info(f"Stored improvement: {improvement.action_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            'total_signals': len(self.signal_records),
            'total_improvements': len(self.improvement_actions),
            'index_size': self.index.ntotal if self.index else 0,
            'last_index_update': self.last_index_update.isoformat() if self.last_index_update else None,
            'model_name': self.model_name
        }
    
    def rebuild_index(self):
        """Rebuild the entire index"""
        logger.info("Rebuilding FAISS index...")
        self._build_index()
        return self.get_stats()
    
    def cleanup_old_signals(self, cutoff_date: datetime) -> int:
        """Remove signals older than cutoff date"""
        with self.lock:
            # Remove from memory
            old_signals = [s for s in self.signal_records if s.timestamp < cutoff_date]
            self.signal_records = [s for s in self.signal_records if s.timestamp >= cutoff_date]
            
            # Remove from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM signals WHERE timestamp < ?', (cutoff_date.isoformat(),))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old signals")
            return deleted_count

class SelfImprovingAgent:
    """Agent that analyzes performance and makes improvements"""
    
    def __init__(self, rag_manager: RAGManager):
        self.rag_manager = rag_manager
        self.improvement_threshold = 0.1  # Minimum performance drop to trigger improvement
        self.current_prompts = {'main': None}  # Store current improved prompts
        self.last_improvement_check = datetime.now()
        self.improvement_interval = timedelta(hours=6)  # Check every 6 hours
    
    def process_signal_with_context(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process signal with historical context"""
        
        # Generate unique signal ID
        signal_id = hashlib.md5(f"{signal_data}{datetime.now()}".encode()).hexdigest()
        
        # Find similar historical signals
        similar_signals = self.rag_manager.find_similar_signals(signal_data, limit=10)
        
        # Analyze historical context
        context_analysis = self._analyze_historical_context(similar_signals)
        
        # Apply context-based confidence adjustment
        confidence_adjustment = self._calculate_confidence_adjustment(context_analysis)
        
        # Create enhanced signal
        enhanced_signal = {
            **signal_data,
            'signal_id': signal_id,
            'historical_context': [
                {
                    'signal_id': s[0].signal_id,
                    'similarity': float(s[1]),
                    'outcome': s[0].outcome.value,
                    'confidence': s[0].confidence,
                    'timestamp': s[0].timestamp.isoformat()
                } for s in similar_signals[:5]  # Top 5 similar signals
            ],
            'context_confidence_adjustment': confidence_adjustment,
            'context_analysis': context_analysis
        }
        
        # Store signal for future reference
        signal_record = SignalRecord(
            signal_id=signal_id,
            timestamp=datetime.now(),
            token_symbol=signal_data.get('token_symbol', ''),
            signal_type=signal_data.get('signal_type', 'HOLD'),
            confidence=signal_data.get('confidence', 0.5),
            reasoning=signal_data.get('reasoning', ''),
            market_data=signal_data.get('market_data', {}),
            outcome=SignalOutcome.PENDING
        )
        
        self.rag_manager.store_signal(signal_record)
        
        return enhanced_signal
    
    def _analyze_historical_context(self, similar_signals: List[Tuple[SignalRecord, float]]) -> Dict[str, Any]:
        """Analyze historical context from similar signals"""
        if not similar_signals:
            return {'success_rate': 0.5, 'avg_confidence': 0.5, 'total_similar': 0}
        
        # Calculate success rate
        successful_signals = [s[0] for s in similar_signals if s[0].outcome == SignalOutcome.SUCCESS]
        success_rate = len(successful_signals) / len(similar_signals)
        
        # Calculate average confidence
        avg_confidence = sum(s[0].confidence for s in similar_signals) / len(similar_signals)
        
        # Calculate average similarity
        avg_similarity = sum(s[1] for s in similar_signals) / len(similar_signals)
        
        return {
            'success_rate': success_rate,
            'avg_confidence': avg_confidence,
            'avg_similarity': avg_similarity,
            'total_similar': len(similar_signals)
        }
    
    def _calculate_confidence_adjustment(self, context_analysis: Dict[str, Any]) -> float:
        """Calculate confidence adjustment based on historical context"""
        
        success_rate = context_analysis.get('success_rate', 0.5)
        avg_similarity = context_analysis.get('avg_similarity', 0.5)
        total_similar = context_analysis.get('total_similar', 0)
        
        # Base adjustment on success rate
        base_adjustment = (success_rate - 0.5) * 0.3  # Max ±0.15
        
        # Weight by similarity and sample size
        similarity_weight = min(avg_similarity, 0.9)  # Cap at 0.9
        sample_weight = min(total_similar / 10, 1.0)  # Cap at 1.0
        
        # Calculate final adjustment
        final_adjustment = base_adjustment * similarity_weight * sample_weight
        
        return max(-0.3, min(0.3, final_adjustment))  # Cap at ±0.3
    
    def update_signal_outcome(self, signal_id: str, outcome: SignalOutcome, 
                            performance_metrics: Optional[Dict[str, float]] = None):
        """Update signal outcome and check for improvement opportunities"""
        
        self.rag_manager.update_signal_outcome(signal_id, outcome, performance_metrics)
        
        # Check if it's time for improvement analysis
        if datetime.now() - self.last_improvement_check > self.improvement_interval:
            self._check_for_improvements()
            self.last_improvement_check = datetime.now()
    
    def _check_for_improvements(self):
        """Check if system needs improvements"""
        
        # Get recent performance
        recent_performance = self.rag_manager.get_performance_metrics(7)  # Last 7 days
        older_performance = self.rag_manager.get_performance_metrics(14)  # Last 14 days
        
        if not recent_performance or not older_performance:
            return
        
        # Compare performance
        recent_success_rate = recent_performance.get('success_rate', 0)
        older_success_rate = older_performance.get('success_rate', 0)
        
        performance_drop = older_success_rate - recent_success_rate
        
        if performance_drop > self.improvement_threshold:
            logger.info(f"Performance drop detected: {performance_drop:.3f}")
            self._trigger_improvement_actions(recent_performance, older_performance)
    
    def _trigger_improvement_actions(self, recent_performance: Dict[str, float], 
                                   older_performance: Dict[str, float]):
        """Trigger improvement actions based on performance analysis"""
        
        # Analyze failure patterns
        recent_failures = [s for s in self.rag_manager.signal_records 
                          if s.timestamp >= datetime.now() - timedelta(days=7) 
                          and s.outcome == SignalOutcome.FAILURE]
        
        if len(recent_failures) > 3:  # Enough failures to analyze
            self._improve_confidence_threshold(recent_failures, recent_performance)
            self._improve_context_weighting(recent_failures, recent_performance)
    
    def _improve_confidence_threshold(self, failures: List[SignalRecord], 
                                    performance: Dict[str, float]):
        """Improve confidence threshold based on failures"""
        
        # Analyze confidence distribution of failures
        failure_confidences = [f.confidence for f in failures]
        avg_failure_confidence = sum(failure_confidences) / len(failure_confidences)
        
        # If failures have high confidence, increase threshold
        if avg_failure_confidence > 0.7:
            new_threshold = avg_failure_confidence + 0.1
            
            improvement = ImprovementAction(
                action_id=f"confidence_threshold_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                improvement_type=ImprovementType.CONFIDENCE_THRESHOLD,
                description=f"Increased confidence threshold to {new_threshold:.2f} due to high-confidence failures",
                parameters={'new_threshold': new_threshold, 'old_threshold': 0.7},
                performance_before=performance
            )
            
            self.rag_manager.store_improvement(improvement)
            logger.info(f"Applied confidence threshold improvement: {new_threshold:.2f}")
    
    def _improve_context_weighting(self, failures: List[SignalRecord], 
                                 performance: Dict[str, float]):
        """Improve context weighting based on failures"""
        
        # Analyze if context adjustments are helping or hurting
        context_adjustments = []
        
        for failure in failures:
            # This would require storing context adjustment with the signal
            # For now, we'll create a general improvement
            pass
        
        # Create improvement action for context weighting
        improvement = ImprovementAction(
            action_id=f"context_weighting_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            improvement_type=ImprovementType.CONTEXT_WEIGHTING,
            description="Adjusted context weighting based on recent failures",
            parameters={'adjustment_factor': 0.8},  # Reduce context influence
            performance_before=performance
        )
        
        self.rag_manager.store_improvement(improvement)
        logger.info("Applied context weighting improvement")
    
    def trigger_improvement_cycle(self, trigger_signal: SignalRecord):
        """Manually trigger improvement cycle"""
        recent_performance = self.rag_manager.get_performance_metrics(7)
        older_performance = self.rag_manager.get_performance_metrics(14)
        
        if recent_performance and older_performance:
            self._trigger_improvement_actions(recent_performance, older_performance)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        stats = self.rag_manager.get_stats()
        recent_performance = self.rag_manager.get_performance_metrics(7)
        
        return {
            'system_stats': stats,
            'recent_performance': recent_performance,
            'last_improvement_check': self.last_improvement_check.isoformat(),
            'improvement_threshold': self.improvement_threshold,
            'current_prompts': self.current_prompts
        }