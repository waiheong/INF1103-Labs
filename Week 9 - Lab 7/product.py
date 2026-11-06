from abc import ABC, abstractmethod

class Product(ABC):

    def __init__(self, product_id, name, price, stock):
        name = str(name).strip()
        price = float(price)
        stock = int(stock)

        if not name:
            raise ValueError("Product name cannot be empty.")
        if price < 0 or stock < 0:
            raise ValueError("Price and stock cannot be negative.")

        # for private attributes 
        self.__product_id = str(product_id)
        self.__name = name
        self.__price = price
        self.__stock = stock

    # update to change stock using update_stock()
    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_stock(self):
        return self.__stock

    # for behaviour shared by every product type to check as product can never go below 0
    def update_stock(self, quantity):
        quantity = int(quantity)
        if self.__stock + quantity < 0:
            raise ValueError("Stock cannot go below zero.")
        self.__stock += quantity

    # for displaying the product
    def display_information(self):
        print(
            f"ID: {self.__product_id} | "
            f"Name: {self.__name} | "
            f"Price: ${self.__price:.2f} | "
            f"Stock: {self.__stock}"
        )

    def to_dict(self):
        return {
            "id": self.__product_id,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock,
        }

    # abstract behaviour: for telling the user how the product reaches the user
    @abstractmethod
    def get_fulfilment_info(self):
        pass
