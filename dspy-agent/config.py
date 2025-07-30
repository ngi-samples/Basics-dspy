import dspy
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def configure_gemini():
    if not api_key:
        raise EnvironmentError("❌ GEMINI_API_KEY not found in .env file")
    dspy.settings.configure(
        lm=dspy.LM(model="gemini/gemini-2.5-flash", api_key=api_key)
    )
    print("✅ Gemini configured.")
