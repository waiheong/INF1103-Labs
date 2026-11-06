from product import Product

class DigitalProduct(Product):
    def __init__(self, product_id, name, price, stock, download_size):
        super().__init__(product_id, name, price, stock)  

        download_size = float(download_size)
        if download_size < 0:
            raise ValueError("Download size cannot be negative.")
        self.__download_size = download_size

    def get_download_size(self):
        return self.__download_size

    # overriding
    def display_information(self):
        super().display_information()   
        print(
            f"    Type: Digital | "
            f"Download size: {self.__download_size:.2f} MB | "
            f"{self.get_fulfilment_info()}"
        )

    # common fields come from Product
    def to_dict(self):
        data = super().to_dict()        
        data["type"] = "digital"
        data["download_size"] = self.__download_size
        return data

    # implementing the abstract method from Product
    def get_fulfilment_info(self):
        return "Delivered digitally via download link"
