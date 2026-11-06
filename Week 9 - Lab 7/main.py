from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from inventory import Inventory
from file_handler import load_inventory, save_inventory

# for display menu 
def show_menu():
    print("\n----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("----------------------------")

# getting user input and adding items to the correct inventory
def add_product_menu(inventory):
    print("\nAdd New Product")
    print("1. Physical Product")
    print("2. Digital Product")
    product_type = input("Choose product type: ").strip()
    if product_type not in ("1", "2"):
        print("\nError: Choose 1 for physical or 2 for digital.")
        return

    product_id = inventory.generate_product_id()

    name = input("Product Name: ").strip()
    if not name:
        print("\nError: Product name cannot be empty.")
        return

    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
        if product_type == "1":
            weight = float(input("Weight (kg): "))
        else:
            download_size = float(input("Download Size (MB): "))
    except ValueError:
        print("\nError: Price, weight and download size must be numbers, "
              "and stock must be a whole number.")
        return

    try:
        if product_type == "1":
            product = PhysicalProduct(product_id, name, price, stock, weight)
        else:
            product = DigitalProduct(product_id, name, price, stock, download_size)
        inventory.add_product(product)  
    except ValueError as error:
        print(f"\nError: {error}")
        return

    print(f"\nProduct added successfully! (ID: {product.get_product_id()})")

def update_stock_menu(inventory):
    print("\nUpdate Stock")
    product_id = input("Product ID (e.g. UUID1): ").strip()

    product = inventory.find_product(product_id)
    if product is None:
        print("\nError: Product not found.")
        return

    print(f"Current stock for {product.get_name()}: {product.get_stock()}")

    try:
        change = int(input("Enter quantity change (e.g. +10 to add, -5 to remove): "))
    except ValueError:
        print("\nError: Enter a valid whole number.")
        return

    try:
        inventory.update_stock(product_id, change)
    except ValueError as error:
        print(f"\nError: {error}")
        return

    print(f"\nStock updated successfully! New stock: {product.get_stock()}")


def search_product_menu(inventory):
    print("\nSearch Product")
    keyword = input("Enter Product ID or Name: ").strip()

    matches = inventory.search_product(keyword)
    if not matches:
        print("\nNo matching products found.")
        return

    inventory.display_products(matches, "Search Results")


def main():
    print("=" * 42)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 42)
    print()

    # for creating the main inventory object
    inventory = Inventory()        
    load_inventory(inventory)      

    while True:
        show_menu()
        choice = input("\nEnter option: ").strip()

        if choice == "1":
            inventory.display_all()
        elif choice == "2":
            add_product_menu(inventory)
        elif choice == "3":
            update_stock_menu(inventory)
        elif choice == "4":
            search_product_menu(inventory)
        elif choice == "5":
            save_inventory(inventory)
        elif choice == "6":
            print("\nExiting program. Goodbye!")
            break
        else:
            print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    main()
