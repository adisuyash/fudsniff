from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import time
import asyncio

# Custom modules
from ai_analyzer import AIAnalyzer
from market_data import MarketData
from news_fetcher import NewsFetcher
from telegram_service import TelegramMonitor

from backend.sa_adapter.teacher_agent import TeacherAgent

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize services
ai_analyzer = AIAnalyzer()
market_data = MarketData()
news_fetcher = NewsFetcher()
telegram_monitor = TelegramMonitor()
manual_signals = []  # Store manually analyzed signals
teacher_agent = TeacherAgent() # Teacher Agent from SA Framework

# ------------------------ ROOT & HEALTH ------------------------

@app.route('/')
def index():
    return jsonify({
        'message': 'Welcome to Fud Sniff API Server!',
        'endpoints': [
            '/api/analyze',
            '/api/batch-analyze',
            '/api/trending',
            '/api/news',
            '/api/health',
            '/api/telegram/*',
            '/api/manual/signals'
        ]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'ai_available': ai_analyzer is not None,
        'telegram_active': telegram_monitor.is_running
    })

# ------------------------ AI & MARKET ROUTES ------------------------

@app.route('/api/analyze', methods=['POST', 'GET'])
def analyze_news():
    if request.method == 'GET':
        return jsonify({'message': 'Use POST with JSON {"news_text": "..."}'}), 200

    try:
        data = request.get_json()
        news_text = data.get('news_text', '')
        if not news_text:
            return jsonify({'error': 'No news text provided'}), 400

        result = ai_analyzer.analyze_news(news_text)

        result_with_metadata = {
            **result,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "id": int(time.time() * 1000)
        }
        manual_signals.insert(0, result_with_metadata)

        return jsonify(result_with_metadata)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/manual/signals', methods=['GET'])
def get_manual_signals():
    try:
        return jsonify({'signals': manual_signals})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    try:
        data = request.get_json()
        news_articles = data.get('articles', [])
        if not news_articles:
            return jsonify({'error': 'No articles provided'}), 400

        results = [{'title': article, 'analysis': ai_analyzer.analyze_news(article)} for article in news_articles]
        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trending', methods=['GET'])
def get_trending():
    try:
        trending = market_data.get_trending_coins(10)
        return jsonify({'trending': trending})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        limit = request.args.get('limit', 10, type=int)
        news = news_fetcher.get_crypto_news(limit)
        return jsonify({'news': news})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------------ TELEGRAM BOT ROUTES ------------------------

@app.route('/api/telegram/start', methods=['POST'])
def start_telegram_monitoring():
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return jsonify({'status': 'error', 'message': 'TELEGRAM_BOT_TOKEN not found'}), 400

        telegram_monitor.start(bot_token)
        return jsonify({'status': 'started'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/telegram/stop', methods=['POST'])
def stop_telegram_monitoring():
    try:
        telegram_monitor.stop()
        return jsonify({'status': 'stopped'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/telegram/status', methods=['GET'])
def get_telegram_status():
    try:
        return jsonify(telegram_monitor.get_status())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/telegram/signals', methods=['GET'])
def get_telegram_signals():
    try:
        limit = request.args.get('limit', 20, type=int)
        return jsonify(telegram_monitor.get_recent_signals(limit))
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/telegram/stats', methods=['GET'])
def get_telegram_stats():
    try:
        return jsonify(telegram_monitor.get_signal_stats())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/telegram/restart', methods=['POST'])
def restart_telegram_monitoring():
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return jsonify({'status': 'error', 'message': 'TELEGRAM_BOT_TOKEN not found'}), 400

        if telegram_monitor.is_running:
            telegram_monitor.stop()
            time.sleep(2)

        telegram_monitor.start(bot_token)
        return jsonify({'status': 'restarted'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/telegram/check-bot', methods=['GET'])
def check_bot_status():
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return jsonify({'status': 'error', 'message': 'TELEGRAM_BOT_TOKEN not found'}), 400

        async def check():
            return await telegram_monitor.check_bot_availability(bot_token)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(check())
            return jsonify(result)
        finally:
            loop.close()

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ------------------------ ERROR HANDLERS ------------------------

@app.errorhandler(404)
def handle_404(error):
    return jsonify({
        'error': 'The requested endpoint was not found.',
        'hint': 'Check the URL or visit /api/health.',
        'status': 404
    }), 404

@app.errorhandler(500)
def handle_500(error):
    return jsonify({
        'error': 'Internal server error',
        'message': str(error),
        'status': 500
    }), 500

# -------------- RAG + SUPERIOR AGENTS INTEGRATION ------------
@app.route("/api/agent/analyze", methods=["POST"])
def analyze_with_agent():
    try:
        data = request.json
        content = data.get("content")
        if not content:
            return jsonify({"error": "Missing content"}), 400

        result = teacher_agent.think(content)

        enriched = {
            **result,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "id": int(time.time() * 1000)
        }

        return jsonify(enriched)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------ ENTRY POINT ------------------------

if __name__ == '__main__':
    print("\nℹ️ Flask server started. Use /api/telegram/start to activate the bot.")
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
