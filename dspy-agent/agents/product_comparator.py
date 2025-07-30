import json
import dspy

with open("data/amazon_mock_products.json", "r") as f:
    products = json.load(f)
    
class ProductComparatorSignature(dspy.Signature):
    product_1: str = dspy.InputField(desc="First product title or keyword")
    product_2: str = dspy.InputField(desc="Second product title or keyword")
    comparison: str = dspy.OutputField(desc="Key differences between both products")
    
class ProductComparatorModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generator = dspy.Predict(ProductComparatorSignature)

    def forward(self, product_1, product_2):
        # Simple matching by title substring
        def find_product(name):
            for p in products:
                if name.lower() in p["title"].lower():
                    return p
            return None

        p1 = find_product(product_1)
        p2 = find_product(product_2)

        if not p1 or not p2:
            return f"❌ Could not find one or both products: '{product_1}', '{product_2}'"

        # Format a prompt
        prompt = (
            f"Compare the following two products:\n\n"
            f"Product 1:\n"
            f"Title: {p1['title']}\n"
            f"Description: {p1['description']}\n"
            f"Price: ₹{p1['price']}\n"
            f"Rating: {p1['rating']}⭐\n\n"
            f"Product 2:\n"
            f"Title: {p2['title']}\n"
            f"Description: {p2['description']}\n"
            f"Price: ₹{p2['price']}\n"
            f"Rating: {p2['rating']}⭐\n\n"
            f"Explain the differences in plain language."
        )

        result = self.generator(product_1=product_1, product_2=product_2)
        return result.comparison