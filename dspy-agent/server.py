from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.cart_manager import CartManagerModule
from agents.product_search import ProductSearchModule
from agents.product_comparator import ProductComparatorModule
from config import configure_gemini

# Configure DSPy
configure_gemini()

# Init modules
cart = CartManagerModule()
products = ["iPhone 13", "iPhone 14", "Samsung Galaxy S23", "Pixel 8"]
search = ProductSearchModule(products=products)
comparator = ProductComparatorModule()

app = FastAPI(title="🛒 DSPy AI Shopping Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class SearchRequest(BaseModel):
    query: str

class CompareRequest(BaseModel):
    product1: str
    product2: str

class CartRequest(BaseModel):
    action: str  # add/remove/view
    product: str = ""

@app.get("/")
def root():
    return {"message": "Welcome to your AI Shopping Assistant 🚀"}

@app.post("/search")
def search_product(req: SearchRequest):
    try:
        # Use forward()
        results = search.forward(req.query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare")
def compare_products(req: CompareRequest):
    try:
        # Use forward()
        comparison = comparator.forward(req.product1, req.product2)
        return {"comparison": comparison}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cart")
def manage_cart(req: CartRequest):
    try:
        # Use forward()
        cart_result = cart.forward(req.action, req.product)
        return {"cart": cart_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
