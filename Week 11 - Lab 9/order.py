from discount_strategy import DiscountStrategy, NoDiscount
from order_line import OrderLine
from product import Product

SEPARATOR = "-" * 64
 # order from customer
class Order:
    def __init__(self, order_id: str, discount: DiscountStrategy | None = None) -> None:
        self.__order_id: str = order_id
        self.__order_lines: list[OrderLine] = []
        self.__discount: DiscountStrategy = discount if discount is not None else NoDiscount()

    def get_order_id(self) -> str:
        return self.__order_id

    def get_discount(self) -> DiscountStrategy:
        return self.__discount

    def set_discount(self, discount: DiscountStrategy) -> None:
        self.__discount = discount

    def add_order_line(self, product: Product, quantity: int) -> None:
        self.__order_lines.append(OrderLine(product, quantity))

    def remove_order_line(self, product_id: str) -> bool:
        wanted = product_id.strip().lower()
        for line in self.__order_lines:
            if line.get_product().get_product_id().lower() == wanted:
                self.__order_lines.remove(line)
                return True
        return False

    def get_order_lines(self) -> list[OrderLine]:
        return list(self.__order_lines)

    def calculate_subtotal(self) -> float:
        return sum(line.calculate_subtotal() for line in self.__order_lines)

    def calculate_total(self) -> float:
        return self.__discount.apply(self.calculate_subtotal())

    def display_order(self) -> None:
        print(f"\nOrder {self.__order_id}")
        print(SEPARATOR)
        if not self.__order_lines:
            print("No items in this order.")
        for line in self.__order_lines:
            line.display_information()
        print(SEPARATOR)

        subtotal, total = self.calculate_subtotal(), self.calculate_total()
        if total != subtotal:
            print(f"{'Subtotal:':<54}${subtotal:>9.2f}")
            print(f"{f'Discount ({self.__discount.describe()}):':<53}-${subtotal - total:>9.2f}")
        print(f"{'Total:':<54}${total:>9.2f}")
