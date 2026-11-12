from product import Product

# for product and quantity ordered
class OrderLine:

    def __init__(self, product: Product, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be at least 1.")

        self.__product: Product = product
        self.__quantity: int = quantity

    def get_product(self) -> Product:
        return self.__product

    def get_quantity(self) -> int:
        return self.__quantity

    def calculate_subtotal(self) -> float:
        return self.__product.get_price() * self.__quantity

    def display_information(self) -> None:
        print(
            f"{self.__product.get_product_id():<8} "
            f"{self.__product.get_name():<25} "
            f"{self.__quantity:>4} x ${self.__product.get_price():>8.2f} "
            f"= ${self.calculate_subtotal():>9.2f}"
        )
