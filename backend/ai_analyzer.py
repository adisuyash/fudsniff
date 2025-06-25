import os
import anthropic
import openai
from dotenv import load_dotenv
from prompts import ANALYSIS_PROMPTS

load_dotenv()

class AIAnalyzer:
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        
        # Initialize available AI clients
        if os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic_client = anthropic.Anthropic(
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
    
    def analyze_news(self, news_text):
        """Analyze single news article for trading signal"""
        try:
            prompt = ANALYSIS_PROMPTS["analysis"].format(news_text=news_text)
            
            # Try Claude first, fallback to OpenAI
            if self.anthropic_client:
                response = self._call_claude(prompt)
            elif self.openai_client:
                response = self._call_openai(prompt)
            else:
                raise Exception("No AI API key configured")
            
            return self._parse_response(response)
            
        except Exception as e:
            return {
                "signal": "HOLD",
                "confidence": 0,
                "reasoning": f"Analysis failed: {str(e)}",
                "coin": "UNKNOWN",
                "success": False
            }
    
    def _call_claude(self, prompt):
        """Call Claude API"""
        message = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.1,
            system=ANALYSIS_PROMPTS["system"],
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    def _call_openai(self, prompt):
        """Call OpenAI API"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": ANALYSIS_PROMPTS["system"]},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        return response.choices[0].message.content
    
    def _parse_response(self, response):
        """Parse AI response into structured data"""
        try:
            lines = response.strip().split('\n')
            result = {
                "signal": "HOLD",
                "confidence": 0,
                "reasoning": "",
                "coin": "UNKNOWN",
                "success": True,
                "raw_response": response
            }
            
            for line in lines:
                if line.startswith('SIGNAL:'):
                    result["signal"] = line.split(':', 1)[1].strip()
                elif line.startswith('CONFIDENCE:'):
                    conf_str = line.split(':', 1)[1].strip().replace('%', '')
                    result["confidence"] = int(conf_str)
                elif line.startswith('REASONING:'):
                    result["reasoning"] = line.split(':', 1)[1].strip()
                elif line.startswith('COIN:'):
                    result["coin"] = line.split(':', 1)[1].strip()
            
            return result
            
        except Exception as e:
            return {
                "signal": "HOLD",
                "confidence": 0,
                "reasoning": f"Failed to parse response: {str(e)}",
                "coin": "UNKNOWN",
                "success": False,
                "raw_response": response
            }