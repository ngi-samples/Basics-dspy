import dspy
import json

with open("data/amazon_mock_products.json", "r") as f:
    products = json.load(f)

class ProductSearchSignature(dspy.Signature):
    """Signature is like prescribing that input and output outline should be"""
    query: str = dspy.InputField(desc="What the user is looking for")
    response: str = dspy.OutputField(desc="Recommended products based on the query")
    
class ProductSearchModule(dspy.Module):
    """A Module in DSPy is a reusable component that encapsulates logic """
    def __init__(self, products):
        super().__init__()
        self.generator = dspy.Predict(ProductSearchSignature)
        """Here generator acts as a predictor of your signature (i.e .., Your Input and Output outline)"""
    def forward(self, query):
        # Format the product list for prompting
        product_text = "\n".join(
            f"{i+1}. {p['title']} - ₹{p['price']} - {p['rating']}⭐\n   {p['description']}"
            for i, p in enumerate(products[:20])  # include only top 20 to limit context
        )

        prompt = (
            f"You are an eCommerce assistant.\n"
            f"User query: {query}\n\n"
            f"Here is a list of available products:\n{product_text}\n\n"
            f"From the list above, recommend the most relevant 3 products."
        )

        result = self.generator(query=prompt)
        return result.response