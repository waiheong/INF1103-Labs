from can_be_shipped import CanBeShipped
from product import Product
from supplier import Supplier

# for physical products that can be shipped
class PhysicalProduct(Product, CanBeShipped):

    BASE_SHIPPING_FEE: float = 5.00   # dollars per item
    RATE_PER_KG: float = 2.00         # dollars per kilogram

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                supplier: Supplier, weight: float) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        if weight < 0:
            raise ValueError("Weight cannot be negative.")
        self.__weight: float = float(weight)

    def get_weight(self) -> float:
        return self.__weight

    def display_information(self) -> None:
        super().display_information()
        print(
            f"    Type: Physical | "
            f"Weight: {self.__weight:.2f} kg | "
            f"Shipping: ${self.calculate_shipping_cost():.2f} | "
            f"{self.get_fulfilment_info()}"
        )

    def to_dict(self) -> dict:
        return {**super().to_dict(), "type": "physical", "weight": self.__weight}

    def get_fulfilment_info(self) -> str:
        return "Requires physical shipping"

    def calculate_shipping_cost(self) -> float:
        return self.BASE_SHIPPING_FEE + self.RATE_PER_KG * self.__weight
