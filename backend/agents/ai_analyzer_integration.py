import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import traceback
from dataclasses import asdict

# Import your existing modules
from rag_system import RAGManager, SelfImprovingAgent, SignalRecord, SignalOutcome
from prompts import get_analysis_prompt, get_sentiment_prompt

logger = logging.getLogger(__name__)

class EnhancedAIAnalyzer:
    """Enhanced AI Analyzer with RAG and self-improvement capabilities"""
    
    def __init__(self, gemini_client, rag_db_path: str = "fudsniff_rag.db"):
        self.gemini_client = gemini_client
        self.rag_manager = RAGManager(rag_db_path)
        self.self_improving_agent = SelfImprovingAgent(self.rag_manager)
        
        # Initialize prompt versions with error handling
        try:
            self.prompt_versions = {
                'analysis': get_analysis_prompt(),
                'sentiment': get_sentiment_prompt()
            }
        except Exception as e:
            logger.error(f"Error loading prompts: {str(e)}")
            # Fallback prompts
            self.prompt_versions = {
                'analysis': "Analyze the following crypto market data and provide a trading signal.",
                'sentiment': "Analyze the sentiment of the following news data."
            }
        
        # Performance tracking
        self.signal_tracking = {}
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the RAG system with proper error handling"""
        try:
            # Check if RAG system is properly initialized
            if not self.rag_manager.is_initialized():
                logger.info("Initializing RAG system...")
                self.rag_manager.initialize()
            
            # Verify self-improving agent is ready
            if not hasattr(self.self_improving_agent, 'current_prompts'):
                self.self_improving_agent.current_prompts = self.prompt_versions.copy()
                
            logger.info("Enhanced AI Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing system: {str(e)}")
            logger.error(traceback.format_exc())
    
    def analyze_with_context(self, news_data: List[Dict[str, Any]], 
                           market_data: Dict[str, Any], 
                           token_symbol: str) -> Dict[str, Any]:
        """Enhanced analysis with RAG context and self-improvement"""
        
        try:
            # Generate initial analysis
            initial_analysis = self._generate_initial_analysis(news_data, market_data, token_symbol)
            
            # Process with RAG context
            enhanced_signal = self.self_improving_agent.process_signal_with_context(initial_analysis)
            
            # Apply context-based adjustments
            final_analysis = self._apply_context_adjustments(initial_analysis, enhanced_signal)
            
            # Store for tracking
            signal_id = enhanced_signal.get('signal_id')
            if signal_id:
                self.signal_tracking[signal_id] = {
                    'timestamp': datetime.now(),
                    'token_symbol': token_symbol,
                    'initial_confidence': initial_analysis.get('confidence', 0.5),
                    'final_confidence': final_analysis.get('confidence', 0.5),
                    'context_adjustment': enhanced_signal.get('context_confidence_adjustment', 0.0)
                }
            
            return final_analysis
            
        except Exception as e:
            logger.error(f"Error in analyze_with_context: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Return fallback analysis
            return {
                'token_symbol': token_symbol,
                'signal_type': 'HOLD',
                'confidence': 0.3,
                'reasoning': f"Analysis failed due to system error: {str(e)}",
                'market_data': market_data,
                'news_summary': self._summarize_news(news_data),
                'analysis_timestamp': datetime.now().isoformat(),
                'error': True,
                'signal_id': hashlib.md5(f"{token_symbol}_{datetime.now().timestamp()}".encode()).hexdigest()
            }
    
    def _generate_initial_analysis(self, news_data: List[Dict[str, Any]], 
                                 market_data: Dict[str, Any], 
                                 token_symbol: str) -> Dict[str, Any]:
        """Generate initial analysis using your existing logic"""
        
        try:
            # Get current prompt (potentially improved)
            current_prompt = self.self_improving_agent.current_prompts.get('main', 
                                                                         self.prompt_versions['analysis'])
            
            # Prepare context for analysis
            context = {
                'news_data': news_data,
                'market_data': market_data,
                'token_symbol': token_symbol,
                'timestamp': datetime.now().isoformat()
            }
            
            # Generate analysis prompt
            analysis_prompt = self._build_analysis_prompt(context, current_prompt)
            
            # Call Gemini API
            response = self.gemini_client.generate_content(analysis_prompt)
            
            # Parse response
            analysis_result = self._parse_gemini_response(response.text)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(news_data, market_data, analysis_result)
            
            return {
                'token_symbol': token_symbol,
                'signal_type': analysis_result.get('signal', 'HOLD'),
                'confidence': analysis_result.get('confidence', 0.5),
                'reasoning': reasoning,
                'market_data': market_data,
                'news_summary': self._summarize_news(news_data),
                'analysis_timestamp': datetime.now().isoformat(),
                'raw_analysis': analysis_result
            }
            
        except Exception as e:
            logger.error(f"Error in _generate_initial_analysis: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'token_symbol': token_symbol,
                'signal_type': 'HOLD',
                'confidence': 0.3,
                'reasoning': f"Analysis failed: {str(e)}",
                'market_data': market_data,
                'news_summary': self._summarize_news(news_data),
                'analysis_timestamp': datetime.now().isoformat(),
                'error': True
            }
    
    def _build_analysis_prompt(self, context: Dict[str, Any], base_prompt: str) -> str:
        """Build analysis prompt with current context"""
        
        try:
            # Get recent performance for context
            recent_metrics = self.rag_manager.get_performance_metrics(7)
            
            # Build enhanced prompt
            enhanced_prompt = f"""{base_prompt}

CONTEXT:
Token: {context['token_symbol']}
Current Time: {context['timestamp']}

RECENT PERFORMANCE CONTEXT:
{json.dumps(recent_metrics, indent=2) if recent_metrics else 'No recent performance data'}

NEWS DATA:
{json.dumps(context['news_data'], indent=2) if context['news_data'] else 'No news data'}

MARKET DATA:
{json.dumps(context['market_data'], indent=2) if context['market_data'] else 'No market data'}

INSTRUCTIONS:
1. Analyze the news sentiment and market data
2. Consider the recent performance context
3. Generate a signal (BUY/SELL/HOLD) with confidence (0.0-1.0)
4. Provide clear reasoning for your decision
5. Be more conservative if recent performance is poor
6. If data is limited, default to HOLD with lower confidence

Response format:
{{
    "signal": "BUY/SELL/HOLD",
    "confidence": 0.0-1.0,
    "sentiment": "positive/negative/neutral",
    "key_factors": ["factor1", "factor2"],
    "risk_level": "low/medium/high"
}}
"""
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error building analysis prompt: {str(e)}")
            return f"{base_prompt}\n\nAnalyze token: {context['token_symbol']}"
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini API response with improved error handling"""
        
        if not response_text or not response_text.strip():
            logger.warning("Empty response from Gemini API")
            return self._get_default_analysis()
        
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                parsed_response = json.loads(json_str)
                
                # Validate required fields
                if self._validate_analysis_response(parsed_response):
                    return parsed_response
                else:
                    logger.warning("Invalid response format, using fallback parsing")
                    return self._fallback_parse(response_text)
            else:
                # No JSON found, use fallback parsing
                return self._fallback_parse(response_text)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return self._fallback_parse(response_text)
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return self._get_default_analysis()
    
    def _validate_analysis_response(self, response: Dict[str, Any]) -> bool:
        """Validate that analysis response has required fields"""
        
        required_fields = ['signal', 'confidence']
        
        for field in required_fields:
            if field not in response:
                return False
        
        # Validate signal type
        if response['signal'] not in ['BUY', 'SELL', 'HOLD']:
            return False
        
        # Validate confidence
        confidence = response['confidence']
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            return False
        
        return True
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis response"""
        return {
            'signal': 'HOLD',
            'confidence': 0.3,
            'sentiment': 'neutral',
            'key_factors': ['system_error'],
            'risk_level': 'high'
        }
    
    def _fallback_parse(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing for non-JSON responses"""
        
        if not response_text:
            return self._get_default_analysis()
        
        response_lower = response_text.lower()
        
        # Determine signal
        if 'buy' in response_lower or 'bullish' in response_lower:
            signal = 'BUY'
        elif 'sell' in response_lower or 'bearish' in response_lower:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        # Estimate confidence based on strength words
        confidence = 0.5
        if any(word in response_lower for word in ['strong', 'very', 'highly', 'extremely']):
            confidence = 0.8
        elif any(word in response_lower for word in ['weak', 'slightly', 'maybe', 'possibly']):
            confidence = 0.3
        
        # Determine sentiment
        if any(word in response_lower for word in ['positive', 'bullish', 'optimistic']):
            sentiment = 'positive'
        elif any(word in response_lower for word in ['negative', 'bearish', 'pessimistic']):
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'signal': signal,
            'confidence': confidence,
            'sentiment': sentiment,
            'key_factors': ['fallback_parsing'],
            'risk_level': 'medium'
        }
    
    def _generate_reasoning(self, news_data: List[Dict[str, Any]], 
                          market_data: Dict[str, Any], 
                          analysis_result: Dict[str, Any]) -> str:
        """Generate human-readable reasoning"""
        
        key_factors = analysis_result.get('key_factors', [])
        sentiment = analysis_result.get('sentiment', 'neutral')
        signal = analysis_result.get('signal', 'HOLD')
        
        reasoning_parts = []
        
        # Add sentiment analysis
        if sentiment == 'positive':
            reasoning_parts.append("Positive sentiment detected in news coverage")
        elif sentiment == 'negative':
            reasoning_parts.append("Negative sentiment detected in news coverage")
        else:
            reasoning_parts.append("Neutral sentiment in news coverage")
        
        # Add key factors
        if key_factors and key_factors != ['fallback_parsing']:
            reasoning_parts.append(f"Key factors: {', '.join(key_factors)}")
        
        # Add market context
        if market_data:
            price_change = market_data.get('price_change_24h', 0)
            try:
                price_change = float(price_change)
                if price_change > 5:
                    reasoning_parts.append(f"Strong positive price movement (+{price_change:.1f}%)")
                elif price_change < -5:
                    reasoning_parts.append(f"Strong negative price movement ({price_change:.1f}%)")
            except (ValueError, TypeError):
                pass
        
        # Add signal reasoning
        reasoning_parts.append(f"Generated {signal} signal based on combined analysis")
        
        return ". ".join(reasoning_parts)
    
    def _summarize_news(self, news_data: List[Dict[str, Any]]) -> str:
        """Create a summary of news items"""
        if not news_data:
            return "No news data available"
        
        try:
            summaries = []
            for item in news_data[:3]:  # Top 3 items
                title = item.get('title', 'Unknown')
                source = item.get('source', 'Unknown')
                summaries.append(f"{title} ({source})")
            
            return "; ".join(summaries)
            
        except Exception as e:
            logger.error(f"Error summarizing news: {str(e)}")
            return "Error processing news data"
    
    def _apply_context_adjustments(self, initial_analysis: Dict[str, Any], 
                                 enhanced_signal: Dict[str, Any]) -> Dict[str, Any]:
        """Apply context-based adjustments to the analysis"""
        
        final_analysis = initial_analysis.copy()
        
        # Apply confidence adjustment based on historical context
        context_adjustment = enhanced_signal.get('context_confidence_adjustment', 0.0)
        original_confidence = initial_analysis.get('confidence', 0.5)
        
        # Adjust confidence
        adjusted_confidence = max(0.0, min(1.0, original_confidence + context_adjustment))
        final_analysis['confidence'] = adjusted_confidence
        
        # Add context information
        final_analysis['historical_context'] = enhanced_signal.get('historical_context', [])
        final_analysis['context_adjustment'] = context_adjustment
        final_analysis['signal_id'] = enhanced_signal.get('signal_id', 
                                                        hashlib.md5(f"{initial_analysis['token_symbol']}_{datetime.now().timestamp()}".encode()).hexdigest())
        
        # Update reasoning with context
        if context_adjustment != 0:
            context_info = f"Historical context suggests {'increased' if context_adjustment > 0 else 'decreased'} confidence (±{abs(context_adjustment):.2f})"
            final_analysis['reasoning'] += f". {context_info}"
        
        return final_analysis
    
    def update_signal_outcome(self, signal_id: str, actual_outcome: str, 
                            performance_data: Optional[Dict[str, float]] = None) -> bool:
        """Update signal outcome for learning"""
        
        try:
            # Convert outcome to enum
            outcome_mapping = {
                'success': SignalOutcome.SUCCESS,
                'failure': SignalOutcome.FAILURE,
                'partial': SignalOutcome.PARTIAL,
                'pending': SignalOutcome.PENDING
            }
            
            outcome = outcome_mapping.get(actual_outcome.lower(), SignalOutcome.PENDING)
            
            # Update in RAG system
            self.self_improving_agent.update_signal_outcome(signal_id, outcome, performance_data)
            
            # Log for tracking
            if signal_id in self.signal_tracking:
                self.signal_tracking[signal_id]['outcome'] = actual_outcome
                self.signal_tracking[signal_id]['performance_data'] = performance_data
            
            logger.info(f"Updated signal {signal_id} outcome: {actual_outcome}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating signal outcome: {str(e)}")
            return False
    
    def get_system_insights(self) -> Dict[str, Any]:
        """Get insights about the system performance and improvements"""
        
        try:
            system_status = self.self_improving_agent.get_system_status()
            
            # Add recent signal tracking
            recent_signals = []
            for signal_id, tracking_info in list(self.signal_tracking.items())[-10:]:
                recent_signals.append({
                    'signal_id': signal_id,
                    'timestamp': tracking_info['timestamp'].isoformat(),
                    'token_symbol': tracking_info['token_symbol'],
                    'confidence_change': tracking_info['final_confidence'] - tracking_info['initial_confidence'],
                    'outcome': tracking_info.get('outcome', 'pending')
                })
            
            return {
                'system_status': system_status,
                'recent_signals': recent_signals,
                'total_improvements': len(self.rag_manager.improvement_actions),
                'rag_size': len(self.rag_manager.signal_records),
                'system_health': 'healthy' if system_status else 'degraded'
            }
            
        except Exception as e:
            logger.error(f"Error getting system insights: {str(e)}")
            return {
                'system_status': {},
                'recent_signals': [],
                'total_improvements': 0,
                'rag_size': 0,
                'system_health': 'error',
                'error': str(e)
            }
    
    def force_improvement_cycle(self) -> bool:
        """Manually trigger an improvement cycle"""
        
        try:
            # Create a dummy trigger signal for manual improvement
            dummy_signal = SignalRecord(
                signal_id="manual_trigger",
                timestamp=datetime.now(),
                token_symbol="MANUAL",
                signal_type="HOLD",
                confidence=0.5,
                reasoning="Manual improvement trigger",
                market_data={},
                outcome=SignalOutcome.FAILURE  # Trigger improvement
            )
            
            self.self_improving_agent.trigger_improvement_cycle(dummy_signal)
            logger.info("Manual improvement cycle triggered")
            return True
            
        except Exception as e:
            logger.error(f"Error triggering improvement cycle: {str(e)}")
            return False
    
    def get_enhanced_prompts(self) -> Dict[str, str]:
        """Get current enhanced prompts"""
        try:
            return self.self_improving_agent.current_prompts
        except Exception as e:
            logger.error(f"Error getting enhanced prompts: {str(e)}")
            return self.prompt_versions
    
    def export_learning_data(self) -> Dict[str, Any]:
        """Export learning data for analysis"""
        
        try:
            signals_data = []
            for signal in self.rag_manager.signal_records:
                signals_data.append(asdict(signal))
            
            improvements_data = []
            for improvement in self.rag_manager.improvement_actions:
                improvements_data.append(asdict(improvement))
            
            return {
                'signals': signals_data,
                'improvements': improvements_data,
                'export_timestamp': datetime.now().isoformat(),
                'total_signals': len(signals_data),
                'total_improvements': len(improvements_data)
            }
            
        except Exception as e:
            logger.error(f"Error exporting learning data: {str(e)}")
            return {
                'signals': [],
                'improvements': [],
                'export_timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_health_check(self) -> Dict[str, Any]:
        """Get system health check"""
        
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'rag_manager': False,
            'self_improving_agent': False,
            'gemini_client': False,
            'database': False,
            'overall_health': 'unhealthy'
        }
        
        try:
            # Check RAG manager
            if hasattr(self.rag_manager, 'signal_records'):
                health_status['rag_manager'] = True
            
            # Check self-improving agent
            if hasattr(self.self_improving_agent, 'current_prompts'):
                health_status['self_improving_agent'] = True
            
            # Check Gemini client
            if self.gemini_client:
                health_status['gemini_client'] = True
            
            # Check database
            if self.rag_manager.is_initialized():
                health_status['database'] = True
            
            # Overall health
            if all([health_status['rag_manager'], health_status['self_improving_agent'], 
                   health_status['gemini_client'], health_status['database']]):
                health_status['overall_health'] = 'healthy'
            elif any([health_status['rag_manager'], health_status['self_improving_agent'], 
                     health_status['gemini_client']]):
                health_status['overall_health'] = 'degraded'
            
        except Exception as e:
            health_status['error'] = str(e)
            logger.error(f"Error in health check: {str(e)}")
        
        return health_status

# Integration functions for your existing codebase
def create_enhanced_analyzer(gemini_client, rag_db_path: str = "fudsniff_rag.db"):
    """Factory function to create enhanced analyzer"""
    try:
        return EnhancedAIAnalyzer(gemini_client, rag_db_path)
    except Exception as e:
        logger.error(f"Error creating enhanced analyzer: {str(e)}")
        raise

def migrate_existing_signals(analyzer: EnhancedAIAnalyzer, 
                           historical_signals: List[Dict[str, Any]]) -> bool:
    """Migrate existing signals to the RAG system"""
    
    try:
        migrated_count = 0
        
        for signal_data in historical_signals:
            try:
                # Parse timestamp
                timestamp = signal_data.get('timestamp')
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                elif not isinstance(timestamp, datetime):
                    timestamp = datetime.now()
                
                # Create signal record
                signal_record = SignalRecord(
                    signal_id=signal_data.get('id', hashlib.md5(str(signal_data).encode()).hexdigest()),
                    timestamp=timestamp,
                    token_symbol=signal_data.get('token_symbol', 'UNKNOWN'),
                    signal_type=signal_data.get('signal_type', 'HOLD'),
                    confidence=float(signal_data.get('confidence', 0.5)),
                    reasoning=signal_data.get('reasoning', ''),
                    market_data=signal_data.get('market_data', {}),
                    outcome=SignalOutcome(signal_data.get('outcome', 'pending')),
                    performance_metrics=signal_data.get('performance_metrics')
                )
                
                analyzer.rag_manager.store_signal(signal_record)
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Error migrating signal {signal_data.get('id', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Migrated {migrated_count}/{len(historical_signals)} historical signals")
        return True
        
    except Exception as e:
        logger.error(f"Error in migration: {str(e)}")
        return False

# Example usage and integration patterns
def integrate_with_existing_app(gemini_client):
    """Example integration with your existing Flask app"""
    
    try:
        # Initialize enhanced analyzer
        enhanced_analyzer = create_enhanced_analyzer(gemini_client)
        
        # Function to replace existing analysis calls
        def analyze_token_with_rag(token_symbol: str, news_data: List[Dict], market_data: Dict):
            """Enhanced analysis function"""
            
            # Use enhanced analyzer instead of basic one
            analysis_result = enhanced_analyzer.analyze_with_context(
                news_data=news_data,
                market_data=market_data,
                token_symbol=token_symbol
            )
            
            return analysis_result
        
        # Endpoint functions for Flask integration
        def update_signal_outcome_endpoint(signal_id: str, outcome: str, performance: Dict):
            """Endpoint to update signal outcomes"""
            
            success = enhanced_analyzer.update_signal_outcome(signal_id, outcome, performance)
            return {'status': 'updated' if success else 'failed'}
        
        def get_system_insights_endpoint():
            """Endpoint to get system insights"""
            
            return enhanced_analyzer.get_system_insights()
        
        def get_health_check_endpoint():
            """Endpoint for health check"""
            
            return enhanced_analyzer.get_health_check()
        
        return {
            'analyzer': enhanced_analyzer,
            'analyze_function': analyze_token_with_rag,
            'update_outcome': update_signal_outcome_endpoint,
            'get_insights': get_system_insights_endpoint,
            'health_check': get_health_check_endpoint
        }
        
    except Exception as e:
        logger.error(f"Error in integration: {str(e)}")
        raise