import dspy
import json
from core.memory import CartMemory

with open("data/amazon_mock_products.json") as f:
    PRODUCTS = json.load(f)

cart = CartMemory()  

class CartManagerSignature(dspy.Signature):
    """Signature for managing the shopping cart"""
    action: str = dspy.InputField(desc="What cart operation the user wants: add/remove/view")
    query: str = dspy.InputField(desc="User's description of the item or request")
    response: str = dspy.OutputField(desc="Status of the cart or confirmation")

class CartManagerModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(CartManagerSignature)

    def forward(self, action, query):
        if action == "view":
            items = cart.list_items()
            if not items:
                return "🛒 Your cart is empty."
            return "\n".join(
                f"- {item['title']} (₹{item['price']})"
                for item in items
            )

        elif action == "add":
            # Find product by title (simplified matching)
            for p in PRODUCTS:
                if query.lower() in p["title"].lower():
                    cart.add_item(p)
                    return f"✅ Added '{p['title']}' to your cart."
            return "❌ Product not found to add."

        elif action == "remove":
            cart.remove_item(query)
            return f"🗑️ Removed '{query}' from your cart."

        else:
            return "❓ Unknown action."
