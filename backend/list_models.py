import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load GEMINI_API_KEY from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception("GEMINI_API_KEY not found in .env")

# Configure Gemini with your key
genai.configure(api_key=api_key)

# List and display models
models = genai.list_models()

print("📦 Available Gemini Models:\n")
for m in models:
    print(f"{m.name} - {', '.join(m.supported_generation_methods)}")
