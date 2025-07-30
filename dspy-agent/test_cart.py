# test_cart.py

from agents.cart_manager import CartManagerModule

agent = CartManagerModule()

print(agent(action="add", query="iPhone 13"))
print(agent(action="add", query="MacBook Air"))
print("\nCart Contents:\n")
print(agent(action="view", query=""))

print("\nRemoving iPhone...\n")
print(agent(action="remove", query="iPhone 13"))

print("\nUpdated Cart:\n")
print(agent(action="view", query=""))
