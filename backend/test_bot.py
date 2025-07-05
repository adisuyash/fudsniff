import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters, CommandHandler
from telegram.error import RetryAfter, TelegramError

# Bot token from BotFather - replace with your own token for production
# TEST BOT TOKEN - Replace with your actual token
BOT_TOKEN = "Your_Bot_Token"

# Enhanced Anti-flood protection settings - optimized for testing
FLOOD_LIMIT = 3  # Reduced for testing - max messages per user
FLOOD_TIME_WINDOW = 5  # Increased time window for testing
COOLDOWN_TIME = 0.3  # Reduced cooldown for faster testing
FLOOD_COOLDOWN = 10  # Seconds to wait when flood is detected

# User rate limiting settings
USER_RATE_LIMIT = 2  # Max messages per minute per user
RATE_LIMIT_WINDOW = 60  # Rate limit window in seconds

# Configure enhanced logging for testing
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Enhanced message handler with improved flood protection
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Enhanced message handler with comprehensive flood protection and rate limiting.
    
    Features:
    1. Message validation
    2. Multi-layer flood protection
    3. Rate limiting per user
    4. Graceful error handling
    5. Detailed logging for testing
    
    Parameters:
        update (Update): The incoming update from Telegram
        context (ContextTypes.DEFAULT_TYPE): The context for this update
    """
    msg = update.message
    if not msg or not msg.text:
        logger.warning("Received empty message or non-text message")
        return
    
    # Enhanced group message filtering - uncomment for group testing
    # if msg.chat.type in ["group", "supergroup"]:
    #     bot_username = context.bot.username
    #     if not (f"@{bot_username}" in msg.text or 
    #             (msg.reply_to_message and msg.reply_to_message.from_user.id == context.bot.id)):
    #         logger.info(f"Ignoring group message without mention from {msg.from_user.username}")
    #         return
        
    user_id = msg.from_user.id
    username = msg.from_user.username or f"User_{user_id}"
    now = datetime.now()
    
    # Initialize tracking systems
    if 'user_messages' not in context.bot_data:
        context.bot_data['user_messages'] = {}
    if 'user_rate_limits' not in context.bot_data:
        context.bot_data['user_rate_limits'] = {}
    if 'flood_cooldowns' not in context.bot_data:
        context.bot_data['flood_cooldowns'] = {}
        
    # Check if user is in flood cooldown
    flood_cooldowns = context.bot_data['flood_cooldowns']
    if user_id in flood_cooldowns:
        if now < flood_cooldowns[user_id]:
            remaining_time = (flood_cooldowns[user_id] - now).seconds
            logger.warning(f"User {username} still in flood cooldown ({remaining_time}s remaining)")
            return
        else:
            # Cooldown expired, remove from tracking
            del flood_cooldowns[user_id]
            logger.info(f"Flood cooldown expired for user {username}")
    
    # Initialize user message tracking
    user_messages = context.bot_data['user_messages']
    user_rate_limits = context.bot_data['user_rate_limits']
    
    if user_id not in user_messages:
        user_messages[user_id] = []
    if user_id not in user_rate_limits:
        user_rate_limits[user_id] = []
        
    # Record message timestamps
    user_messages[user_id].append(now)
    user_rate_limits[user_id].append(now)
    
    # Clean up old records
    flood_threshold = now - timedelta(seconds=FLOOD_TIME_WINDOW)
    rate_threshold = now - timedelta(seconds=RATE_LIMIT_WINDOW)
    
    user_messages[user_id] = [ts for ts in user_messages[user_id] if ts > flood_threshold]
    user_rate_limits[user_id] = [ts for ts in user_rate_limits[user_id] if ts > rate_threshold]
    
    # Enhanced flood protection
    if len(user_messages[user_id]) > FLOOD_LIMIT:
        logger.warning(f"FLOOD DETECTED: {username} ({user_id}) sent {len(user_messages[user_id])} messages in {FLOOD_TIME_WINDOW}s")
        
        # Set flood cooldown
        flood_cooldowns[user_id] = now + timedelta(seconds=FLOOD_COOLDOWN)
        
        # Clear message history to reset flood counter
        user_messages[user_id] = []
        
        # Send flood warning only in private chats
        if msg.chat.type == "private":
            try:
                await msg.reply_text(
                    f"🚫 Please slow down! Too many messages in a short time.\n"
                    f"Wait {FLOOD_COOLDOWN} seconds before sending more messages."
                )
            except Exception as e:
                logger.error(f"Failed to send flood warning to {username}: {e}")
        
        return
    
    # Rate limiting check
    if len(user_rate_limits[user_id]) > USER_RATE_LIMIT:
        logger.warning(f"RATE LIMIT: {username} exceeded {USER_RATE_LIMIT} messages per minute")
        
        if msg.chat.type == "private":
            try:
                await msg.reply_text(
                    f"⏰ Rate limit exceeded! Please wait before sending more messages.\n"
                    f"Limit: {USER_RATE_LIMIT} messages per minute"
                )
            except Exception as e:
                logger.error(f"Failed to send rate limit warning to {username}: {e}")
        
        return
    
    # Log received message with enhanced details
    logger.info(f"[RECEIVED] From {username} (ID: {user_id}) in {msg.chat.type}: {msg.text[:50]}...")
    
    # Enhanced message analysis (mock implementation for testing)
    try:
        # Simulate analysis processing time
        await asyncio.sleep(0.1)
        
        # Mock analysis results with more variety for testing
        import random
        signal_types = ["BUY", "SELL", "HOLD", "WATCH"]
        signal_type = random.choice(signal_types)
        confidence = round(random.uniform(0.6, 0.95), 2)
        
        # Extract potential tokens from message (simple keyword matching for testing)
        common_tokens = ["BTC", "ETH", "DOGE", "ADA", "SOL", "MATIC", "DOT", "LINK"]
        tokens_mentioned = [token for token in common_tokens if token.lower() in msg.text.lower()]
        
        if not tokens_mentioned:
            tokens_mentioned = ["N/A"]
        
        logger.info(
            f"[ANALYZED] User: {username} | Signal: {signal_type} | "
            f"Confidence: {confidence:.2f} | Tokens: {tokens_mentioned}"
        )
        
        # Cooldown to prevent rate limiting
        await asyncio.sleep(COOLDOWN_TIME)
        
        # Enhanced response with analysis details
        response_text = (
            f"✅ Signal Analysis Complete\n"
            f"📊 Signal: {signal_type}\n"
            f"🎯 Confidence: {confidence:.0%}\n"
            f"💎 Tokens: {', '.join(tokens_mentioned)}"
        )
        
        # Send response with comprehensive error handling
        try:
            await msg.reply_text(response_text)
            logger.info(f"[SENT] Response sent to {username}")
            
        except RetryAfter as e:
            # Handle Telegram's rate limiting
            logger.warning(f"Telegram rate limit hit. Retrying after {e.retry_after}s")
            await asyncio.sleep(e.retry_after)
            await msg.reply_text(response_text)
            logger.info(f"[SENT] Response sent to {username} after retry")
            
        except TelegramError as e:
            logger.error(f"Failed to send response to {username}: {e}")
            
    except Exception as e:
        logger.error(f"Error processing message from {username}: {e}")

# Enhanced start command handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Enhanced /start command handler with detailed bot information.
    """
    user = update.message.from_user
    username = user.username or f"User_{user.id}"
    
    logger.info(f"[START] Command received from {username}")
    
    welcome_text = (
        "🤖 **Signal Analyzer Bot - Test Version**\n\n"
        "🚀 **Features:**\n"
        "• Advanced flood protection\n"
        "• Rate limiting\n"
        "• Signal analysis\n"
        "• Real-time monitoring\n\n"
        "📝 **Usage:**\n"
        "Send me any message to analyze!\n\n"
        "⚠️ **Limits:**\n"
        f"• Max {FLOOD_LIMIT} messages per {FLOOD_TIME_WINDOW} seconds\n"
        f"• Max {USER_RATE_LIMIT} messages per minute\n\n"
        "Happy testing! 🎉"
    )
    
    try:
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        logger.info(f"[START] Welcome message sent to {username}")
    except Exception as e:
        logger.error(f"Failed to send start message to {username}: {e}")

# Status command for testing
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Status command to check bot health and user statistics.
    """
    user_id = update.message.from_user.id
    username = update.message.from_user.username or f"User_{user_id}"
    
    # Get user statistics
    user_messages = context.bot_data.get('user_messages', {}).get(user_id, [])
    user_rate_limits = context.bot_data.get('user_rate_limits', {}).get(user_id, [])
    
    flood_cooldowns = context.bot_data.get('flood_cooldowns', {})
    in_cooldown = user_id in flood_cooldowns
    
    now = datetime.now()
    recent_messages = len([ts for ts in user_messages if ts > now - timedelta(seconds=FLOOD_TIME_WINDOW)])
    recent_rate_messages = len([ts for ts in user_rate_limits if ts > now - timedelta(seconds=RATE_LIMIT_WINDOW)])
    
    status_text = (
        f"📊 **Bot Status for {username}**\n\n"
        f"🔥 Recent messages ({FLOOD_TIME_WINDOW}s): {recent_messages}/{FLOOD_LIMIT}\n"
        f"⏰ Messages this minute: {recent_rate_messages}/{USER_RATE_LIMIT}\n"
        f"🚫 In cooldown: {'Yes' if in_cooldown else 'No'}\n\n"
        f"⚙️ **Bot Settings:**\n"
        f"• Flood limit: {FLOOD_LIMIT} msgs/{FLOOD_TIME_WINDOW}s\n"
        f"• Rate limit: {USER_RATE_LIMIT} msgs/min\n"
        f"• Cooldown time: {FLOOD_COOLDOWN}s\n"
        f"• Response delay: {COOLDOWN_TIME}s"
    )
    
    try:
        await update.message.reply_text(status_text, parse_mode='Markdown')
        logger.info(f"[STATUS] Status sent to {username}")
    except Exception as e:
        logger.error(f"Failed to send status to {username}: {e}")

# Enhanced shutdown handler
async def shutdown_handler(app):
    """Graceful shutdown handler"""
    logger.info("🛑 Shutting down bot gracefully...")

# Main function with enhanced error handling and continuous running
def main():
    """
    Enhanced main function with comprehensive error handling and continuous operation.
    The bot will run indefinitely until manually stopped (Ctrl+C) or killed.
    """
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Bot token not configured! Please set your bot token.")
        return
    
    logger.info("🚀 Initializing Enhanced Test Bot...")
    
    while True:  # Restart loop for robustness
        try:
            # Create application with enhanced configuration
            app = Application.builder().token(BOT_TOKEN).build()
            
            # Register handlers
            app.add_handler(CommandHandler("start", start_command))
            app.add_handler(CommandHandler("status", status_command))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            
            # Start the bot
            logger.info("📡 Enhanced Test Bot started successfully!")
            logger.info(f"🛡️  Flood protection: {FLOOD_LIMIT} msgs/{FLOOD_TIME_WINDOW}s")
            logger.info(f"⏰ Rate limiting: {USER_RATE_LIMIT} msgs/min")
            logger.info("🔄 Polling started... (Press Ctrl+C to stop)")
            logger.info("✅ Bot is now running continuously!")
            
            # This will run indefinitely until interrupted
            app.run_polling(
                poll_interval=1.0,  # Check for updates every second
                timeout=10,         # Timeout for long polling
                bootstrap_retries=5,  # Retry connection failures
                read_timeout=30,    # Read timeout
                write_timeout=30,   # Write timeout
                connect_timeout=30, # Connection timeout
                drop_pending_updates=True,  # Ignore old updates on restart
            )
            
            # This line should never be reached unless the bot is stopped
            logger.info("🔄 Bot polling stopped")
            break
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user (Ctrl+C)")
            break
            
        except Exception as e:
            logger.error(f"❌ Bot crashed with error: {e}")
            logger.info("🔄 Restarting bot in 5 seconds...")
            
            # Wait before restarting
            import time
            time.sleep(5)
            
            # Continue the while loop to restart
            continue
    
    logger.info("👋 Bot shutdown complete")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 Final shutdown - Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        logger.info("🔄 You may need to restart the bot manually")