import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import threading

from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, ContextTypes, filters

from ai_analyzer import AIAnalyzer
from market_data import MarketData
from token_detector import TokenDetector

# --- Signal Data Model ---

@dataclass
class TelegramSignal:
    id: str
    source_channel: str
    message_text: str
    signal_type: str
    confidence: float
    tokens_mentioned: List[str]
    timestamp: datetime
    user_mention: str = "Unknown"
    sentiment: Optional[str] = None
    reasoning: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "source_channel": self.source_channel,
            "message_text": self.message_text,
            "signal_type": self.signal_type,
            "confidence": self.confidence,
            "tokens_mentioned": self.tokens_mentioned,
            "timestamp": self.timestamp.isoformat(),
            "user_mention": self.user_mention,
            "sentiment": self.sentiment,
            "reasoning": self.reasoning
        }

# --- Flood Protection Settings ---

FLOOD_LIMIT = 5
FLOOD_WINDOW = 10
RATE_LIMIT = 10
RATE_WINDOW = 60
COOLDOWN_TIME = 0.5

# --- Telegram Monitor ---

class TelegramMonitor:
    def __init__(self):
        self.signals: List[TelegramSignal] = []
        self.ai = AIAnalyzer()
        self.market = MarketData()
        self.token_detector = TokenDetector()
        self.application: Optional[Application] = None
        self.is_running = False
        self._stop_event = threading.Event()
        self.logger = logging.getLogger("TelegramMonitor")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        if not msg or not msg.text:
            return

        chat_name = msg.chat.username or msg.chat.title or str(msg.chat.id)
        username = msg.from_user.username or f"User_{msg.from_user.id}"
        text = msg.text
        now = datetime.now()

        print(f"[🟢] Message from @{username} in {chat_name}: {text}")

        # Flood protection
        user_id = msg.from_user.id
        bot_data = context.bot_data
        bot_data.setdefault('user_messages', {}).setdefault(user_id, []).append(now)
        bot_data.setdefault('user_rate', {}).setdefault(user_id, []).append(now)

        bot_data['user_messages'][user_id] = [
            t for t in bot_data['user_messages'][user_id] if t > now - timedelta(seconds=FLOOD_WINDOW)
        ]
        bot_data['user_rate'][user_id] = [
            t for t in bot_data['user_rate'][user_id] if t > now - timedelta(seconds=RATE_WINDOW)
        ]

        if len(bot_data['user_messages'][user_id]) > FLOOD_LIMIT:
            self.logger.warning(f"Flood detected from {username}")
            return

        if len(bot_data['user_rate'][user_id]) > RATE_LIMIT:
            self.logger.warning(f"Rate limit hit for {username}")
            return

        # Token candidates
        token_candidates = self.token_detector.find_possible_tokens(text)

        # --- FIXED: Gemini LLM call ---
        try:
            llm_result = self.ai.analyze_news(text)
            print(f"[📊] LLM result: {llm_result}")
        except Exception as e:
            self.logger.error(f"LLM analysis failed: {e}")
            return

        coin = llm_result.get("coin")
        if coin == "UNKNOWN" and token_candidates:
            coin = token_candidates[0]['symbol'].upper()

        signal = TelegramSignal(
            id=f"{chat_name}_{int(time.time() * 1000)}",
            source_channel=chat_name,
            message_text=text,
            signal_type=llm_result.get("signal", "HOLD"),
            confidence=float(llm_result.get("confidence", 0)) / 100,
            tokens_mentioned=[coin] if coin else [],
            timestamp=now,
            user_mention=username,
            sentiment="positive" if llm_result.get("signal") == "BUY" else "negative" if llm_result.get("signal") == "SELL" else "neutral",
            reasoning=llm_result.get("reasoning")
        )

        self.signals.append(signal)
        if len(self.signals) > 100:
            self.signals = self.signals[-100:]

        print(f"[✅] Signal stored: {signal.to_dict()}")

        await asyncio.sleep(COOLDOWN_TIME)

    def start(self, token: str):
        if self.is_running:
            return {"status": "already_running"}
        self._stop_event.clear()

        def _run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def _start():
                app = Application.builder().token(token).build()
                app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
                self.application = app
                await app.initialize()
                await app.start()
                await app.updater.start_polling(drop_pending_updates=True)
                self.is_running = True
                print("[🚀] Telegram bot started and polling...")
                while not self._stop_event.is_set():
                    await asyncio.sleep(1)
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
                print("[🛑] Telegram bot stopped.")

            loop.run_until_complete(_start())

        threading.Thread(target=_run, daemon=True).start()
        return {"status": "started"}

    def stop(self):
        self._stop_event.set()
        self.is_running = False
        return {"status": "stopped"}

    def get_recent_signals(self, limit=20):
        return {
            "signals": [s.to_dict() for s in self.signals[-limit:]],
            "total_count": len(self.signals)
        }

    def get_status(self):
        return {
            "is_running": self.is_running,
            "total_signals": len(self.signals),
            "last_signal": self.signals[-1].to_dict() if self.signals else None
        }

    def get_signal_stats(self):
        stats = {
            "total": len(self.signals),
            "buy": 0,
            "sell": 0,
            "news": 0,
            "confidence_avg": 0.0,
            "by_type": {},
            "by_token": {},
        }

        if not self.signals:
            return stats

        total_conf = 0.0

        for s in self.signals:
            signal_type = s.signal_type.upper()
            stats["by_type"][signal_type] = stats["by_type"].get(signal_type, 0) + 1

            if signal_type == "BUY":
                stats["buy"] += 1
            elif signal_type in ["SELL", "SHORT"]:
                stats["sell"] += 1
            elif signal_type == "NEWS":
                stats["news"] += 1

            for token in s.tokens_mentioned:
                token = token.upper()
                stats["by_token"][token] = stats["by_token"].get(token, 0) + 1

            total_conf += s.confidence

        stats["confidence_avg"] = round(total_conf / len(self.signals), 2)
        return stats


telegram_monitor = TelegramMonitor()
