# main file run this
# it will display menu, get user input and call appropriate Inventory methods

from product import Product
from inventory import Inventory
from file_handler import load_inventory, save_inventory

def show_menu():
    print("\n----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("----------------------------")

def add_product_menu(inventory):
    print("\nAdd New Product")
    product_id = inventory.generate_product_id()

    name = input("Product Name: ").strip()
    if not name:
        print("\nError: Product name cannot be empty.")
        return

    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
    except ValueError:
        print("\nError: Price must be a number and stock must be a whole number.")
        return

    try:
        product = Product(product_id, name, price, stock)   
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

    # create inventory object and load from file
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
