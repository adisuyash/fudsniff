from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_analyzer import AIAnalyzer
from market_data import MarketData
from news_fetcher import NewsFetcher
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
ai_analyzer = AIAnalyzer()
market_data = MarketData()
news_fetcher = NewsFetcher()

@app.route('/api/analyze', methods=['POST'])
def analyze_news():
    """Analyze news text for trading signals"""
    try:
        data = request.get_json()
        news_text = data.get('news_text', '')
        
        if not news_text:
            return jsonify({'error': 'No news text provided'}), 400
        
        # Analyze with AI
        result = ai_analyzer.analyze_news(news_text)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trending', methods=['GET'])
def get_trending():
    """Get trending coins for context"""
    try:
        trending = market_data.get_trending_coins(10)
        return jsonify({'trending': trending})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/news', methods=['GET'])
def get_news():
    """Get latest crypto news"""
    try:
        limit = request.args.get('limit', 10, type=int)
        news = news_fetcher.get_crypto_news(limit)
        return jsonify({'news': news})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple news articles"""
    try:
        data = request.get_json()
        news_articles = data.get('articles', [])
        
        if not news_articles:
            return jsonify({'error': 'No articles provided'}), 400
        
        results = []
        for article in news_articles:
            result = ai_analyzer.analyze_news(article)
            results.append({
                'title': article,
                'analysis': result
            })
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_available': ai_analyzer.anthropic_client is not None or ai_analyzer.openai_client is not None
    })

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)