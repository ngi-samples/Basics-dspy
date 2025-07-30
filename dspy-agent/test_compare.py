import os
import json
from dotenv import load_dotenv
import dspy
from agents.product_comparator import ProductComparatorModule

# ✅ Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise EnvironmentError("❌ GEMINI_API_KEY not found in .env file")

# ✅ Configure Gemini LLM via DSPy
dspy.settings.configure(
    lm=dspy.LM(model="gemini/gemini-2.5-flash", api_key=api_key)
)

# ✅ Initialize the comparator
print("✅ Gemini configured. Initializing ProductComparatorModule...\n")
comparator = ProductComparatorModule()

# ✅ Run test comparisons
tests = [
    ("OnePlus 9", "Apple iPhone 13"),
    ("MacBook Air M2", "HP Spectre x360"),
    ("Redmi Note 11", "Realme Narzo 50")
]

for p1, p2 in tests:
    print(f"🧪 Comparing: {p1} vs {p2}")
    result = comparator(product_1=p1, product_2=p2)
    print(result if isinstance(result, str) else result.comparison)
    print("\n" + "-" * 60 + "\n")
