import os
from dotenv import load_dotenv
import google.generativeai as genai
from prompts import ANALYSIS_PROMPTS

load_dotenv()

class AIAnalyzer:
    def __init__(self):
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_key:
            raise Exception("GEMINI_API_KEY not found in environment")

        genai.configure(api_key=self.gemini_key)

        try:
            self.model = genai.GenerativeModel("models/gemini-2.5-flash")
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini model: {e}")

    def analyze_news(self, news_text: str) -> dict:
        """Analyze a single news article for trading signal."""
        try:
            prompt = ANALYSIS_PROMPTS["analysis"].format(news_text=news_text)
            full_prompt = f"{ANALYSIS_PROMPTS['system']}\n\n{prompt}"
            response_text = self._call_gemini(full_prompt)
            return self._parse_response(response_text)
        except Exception as e:
            return {
                "signal": "HOLD",
                "confidence": 0,
                "reasoning": f"Analysis failed: {str(e)}",
                "coin": "UNKNOWN",
                "success": False,
                "raw_response": ""
            }

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini Flash model and return raw text response."""
        try:
            response = self.model.generate_content(prompt)
            return getattr(response, "text", "").strip()
        except Exception as e:
            raise Exception(f"Gemini API call failed: {e}")

    def _parse_response(self, response: str) -> dict:
        """Parse AI response into structured trading signal."""
        try:
            result = {
                "signal": "HOLD",
                "confidence": 0,
                "reasoning": "",
                "coin": "UNKNOWN",
                "success": True,
                "raw_response": response
            }

            for line in response.strip().split('\n'):
                line = line.strip()
                if line.startswith('SIGNAL:'):
                    result["signal"] = line.split(':', 1)[1].strip()
                elif line.startswith('CONFIDENCE:'):
                    conf_str = line.split(':', 1)[1].strip().replace('%', '')
                    result["confidence"] = int(conf_str) if conf_str.isdigit() else 0
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
