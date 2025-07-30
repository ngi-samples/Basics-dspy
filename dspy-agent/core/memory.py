class CartMemory:
    def __init__(self):
        self.cart = []

    def add_item(self, product):
        self.cart.append(product)

    def remove_item(self, product_title):
        self.cart = [p for p in self.cart if p['title'].lower() != product_title.lower()]

    def list_items(self):
        return self.cart

    def clear(self):
        self.cart = []
