from product import Product
from can_be_shipped import CanBeShipped


class PhysicalProduct(Product, CanBeShipped):
    # in dollars per items
    BASE_SHIPPING_FEE = 5.00  
     # in dollars per KG
    RATE_PER_KG = 2.00         

    def __init__(self, product_id, name, price, stock, weight):
        super().__init__(product_id, name, price, stock)   

        weight = float(weight)
        if weight < 0:
            raise ValueError("Weight cannot be negative.")
        self.__weight = weight

    def get_weight(self):
        return self.__weight

    # overriding
    def display_information(self):
        super().display_information()   
        print(
            f"    Type: Physical | "
            f"Weight: {self.__weight:.2f} kg | "
            f"Shipping: ${self.calculate_shipping_cost():.2f} | "
            f"{self.get_fulfilment_info()}"
        )

    def to_dict(self):
        data = super().to_dict()       
        data["type"] = "physical"
        data["weight"] = self.__weight
        return data

    # for implementing the abstract method from Product
    def get_fulfilment_info(self):
        return "Requires physical shipping"

    # for implementing the CanBeShipped interface. base fee + $2/kg
    def calculate_shipping_cost(self):
        return self.BASE_SHIPPING_FEE + self.RATE_PER_KG * self.__weight
