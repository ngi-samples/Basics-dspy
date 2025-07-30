from agents.cart_manager import CartManagerModule
from agents.product_search import ProductSearchModule
from agents.product_comparator import ProductComparatorModule
import dspy
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise EnvironmentError("❌ GEMINI_API_KEY not found in .env file")

# ✅ Configure Gemini LLM via DSPy
dspy.settings.configure(
    lm=dspy.LM(model="gemini/gemini-2.5-flash", api_key=api_key)
)

# ✅ Initialize the modules
print("✅ Gemini configured. Initializing modules...\n")

def main():
    cart = CartManagerModule()
    products = ["iPhone 13", "iPhone 14", "Samsung Galaxy S23", "Pixel 8"]
    search = ProductSearchModule(products=products)
    comparator = ProductComparatorModule()

    print("🛍️ Welcome to your AI Shopping Assistant!")
    while True:
        print("\nChoose an option:")
        print("1. Search Product")
        print("2. Compare Products")
        print("3. Add to Cart")
        print("4. Remove from Cart")
        print("5. View Cart")
        print("6. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            query = input("🔍 Search for: ")
            print(search(query))  # ✅ Replaced .forward()

        elif choice == "2":
            p1 = input("Enter first product: ")
            p2 = input("Enter second product: ")
            print(comparator(p1, p2))  # ✅ Replaced .forward()

        elif choice == "3":
            item = input("Enter product to add: ")
            print(cart("add", item))  # ✅ Replaced .forward()

        elif choice == "4":
            item = input("Enter product to remove: ")
            print(cart("remove", item))  # ✅ Replaced .forward()

        elif choice == "5":
            print("🧺 Your Cart:")
            print(cart("view", ""))  # ✅ Replaced .forward()

        elif choice == "6":
            print("👋 Exiting... Happy Shopping!")
            break

        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
