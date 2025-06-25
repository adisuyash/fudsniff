# Extracted and simplified from Superior Agents
ANALYSIS_PROMPTS = {
    "system": """You are a professional crypto trader and analyst.
    Your goal is to analyze crypto news and provide clear BUY or SHORT recommendations.
    You must be decisive and provide a confidence score.""",
    
    "analysis": """Analyze this crypto news and provide a trading signal:

News: {news_text}

Consider:
1. Market sentiment (bullish/bearish)
2. Technical implications
3. Fundamental impact
4. Risk factors

Respond in this exact format:
SIGNAL: [BUY/SHORT]
CONFIDENCE: [0-100]%
REASONING: [Brief explanation in 1-2 sentences]
COIN: [Main coin mentioned or "GENERAL"]
""",
    
    "batch_analysis": """Analyze these multiple crypto news articles and provide overall market sentiment:

News Articles:
{news_batch}

Provide overall market direction and top 3 signals with confidence scores."""
}