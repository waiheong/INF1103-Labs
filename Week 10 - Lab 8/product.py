from abc import ABC, abstractmethod

from supplier import Supplier

# for products that can be sold
class Product(ABC):

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                supplier: Supplier) -> None:
        name = name.strip()
        if not name:
            raise ValueError("Product name cannot be empty.")
        if price < 0 or stock < 0:
            raise ValueError("Price and stock cannot be negative.")

        self.__product_id: str = product_id
        self.__name: str = name
        self.__price: float = float(price)
        self.__stock: int = int(stock)
        self.__supplier: Supplier = supplier

    def get_product_id(self) -> str:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    def get_supplier(self) -> Supplier:
        return self.__supplier

# for checking stock and updating it when products are sold or restocked and never be below zero
    def update_stock(self, quantity: int) -> None:
        if self.__stock + quantity < 0:
            raise ValueError("Stock cannot go below zero.")
        self.__stock += quantity

    def display_information(self) -> None:
        print(
            f"ID: {self.__product_id} | "
            f"Name: {self.__name} | "
            f"Price: ${self.__price:.2f} | "
            f"Stock: {self.__stock}"
        )
        print(
            f"    Supplier: {self.__supplier.get_name()} "
            f"({self.__supplier.get_contact_email()})"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.__product_id,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock,
            "supplier_id": self.__supplier.get_supplier_id(),
        }

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass
