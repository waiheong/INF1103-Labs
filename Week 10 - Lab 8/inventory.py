from datetime import datetime

from product import Product

SEPARATOR = "-" * 60

# for managing the inventory of products and the history of stock changes
class Inventory:

    def __init__(self) -> None:
        self.__products: list[Product] = []
        self.__history: list[dict] = []

    def add_product(self, product: Product, record: bool = True) -> None:
        """Add an existing product. Pass record=False when restoring from file."""
        if self.find_product(product.get_product_id()) is not None:
            raise ValueError(f"A product with ID {product.get_product_id()} already exists.")

        self.__products.append(product)
        if record:
            self.__record_transaction(product, "ADD", product.get_stock())

    def find_product(self, product_id: str) -> Product | None:
        wanted = product_id.strip().lower()
        return next(
            (p for p in self.__products if p.get_product_id().lower() == wanted),
            None,
        )

    # for removing a product from the inventory, returning it if found
    def remove_product(self, product_id: str) -> Product | None:
        product = self.find_product(product_id)
        if product is None:
            return None

        self.__products.remove(product)
        self.__record_transaction(product, "REMOVE", 0)
        return product

    # Return a copy so callers cannot change the collection directly.
    def get_products(self) -> list[Product]:
        return list(self.__products)

# for matching the product by UUID
    def search_product(self, keyword: str) -> list[Product]:
        keyword = keyword.strip().lower()
        return [
            p for p in self.__products
            if keyword == p.get_product_id().lower() or keyword in p.get_name().lower()
        ]

    def update_stock(self, product_id: str, change: int) -> Product:
        product = self.find_product(product_id)
        if product is None:
            raise ValueError("Product not found.")

        product.update_stock(change)
        self.__record_transaction(product, "UPDATE", change)
        return product

    def display_products(self, products: list[Product], title: str) -> None:
        print(f"\n{title}")
        print(SEPARATOR)
        if not products:
            print("No products to display.")
        for product in products:
            product.display_information()
        print(SEPARATOR)

    def display_all(self) -> None:
        self.display_products(self.__products, "Current Inventory")

# for generating a new product UUID in sequence
    def generate_product_id(self) -> str:
        numbers = [
            int(p.get_product_id()[4:]) for p in self.__products
            if p.get_product_id().upper().startswith("UUID") and p.get_product_id()[4:].isdigit()
        ]
        return f"UUID{max(numbers, default=0) + 1}"

# for recording the history of stock changes, including adding and removing products
    def __record_transaction(self, product: Product, action: str, change: int) -> None:
        self.__history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "product_id": product.get_product_id(),
            "action": action,
            "change": change,
            "stock_after": product.get_stock(),
        })

    def load_history(self, history: list[dict]) -> None:
        self.__history = list(history)

    def to_dict(self) -> dict:
        return {
            "products": [p.to_dict() for p in self.__products],
            "history": list(self.__history),
        }
