from datetime import datetime

LINE = "-" * 60

class Inventory:
    def __init__(self):
        self.__products = []
        self.__history = []

    # add or find products
    def add_product(self, product, record=True):
        if self.find_product(product.get_product_id()) is not None:
            raise ValueError(f"A product with ID {product.get_product_id()} already exists.")

        self.__products.append(product)
        if record:
            self.__record_transaction(product, "ADD", product.get_stock())

    def find_product(self, product_id):
        product_id = product_id.strip().lower()
        for product in self.__products:
            if product.get_product_id().lower() == product_id:
                return product
        return None

    def search_product(self, keyword):
        keyword = keyword.strip().lower()
        return [
            product for product in self.__products
            if keyword == product.get_product_id().lower() or keyword in product.get_name().lower()
        ]

    # editing the stocl
    def update_stock(self, product_id, change):
        product = self.find_product(product_id)
        if product is None:
            raise ValueError("Product not found.")

        product.update_stock(change)         
        self.__record_transaction(product, "UPDATE", change)
        return product

    # displaying
    def display_products(self, products, title):
        print(f"\n{title}")
        print(LINE)
        if not products:
            print("No products to display.")
        else:
            for product in products:
                product.display_information()
        print(LINE)

    def display_all(self):
        self.display_products(self.__products, "Current Inventory")

    # UUID with auto increment UUID
    def generate_product_id(self):
        highest_id = 0
        for product in self.__products:
            product_id = product.get_product_id()
            if product_id.upper().startswith("UUID") and product_id[4:].isdigit():
                highest_id = max(highest_id, int(product_id[4:]))
        return f"UUID{highest_id + 1}"

    # history with date and time stamp
    def __record_transaction(self, product, action, change):
        self.__history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "product_id": product.get_product_id(),
            "action": action,
            "change": change,
            "stock_after": product.get_stock(),
        })

    def load_history(self, history):
        self.__history = list(history)

    # saving
    def to_dict(self):
        return {
            "products": [product.to_dict() for product in self.__products],
            "history": list(self.__history),
        }
