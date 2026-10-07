import json
from datetime import datetime
from pathlib import Path

# for inventory.json 
INVENTORY_FILE = Path(__file__).parent / "inventory.json"

# creating the ----------------------------- line
LINE = "-" * 60

# for inventory
def load_inventory():
    if INVENTORY_FILE.exists():
        print("inventory.json found.")
        try:
            with open(INVENTORY_FILE, "r") as file:
                data = json.load(file)
            inventory = {
                "products": data.get("products", []),
                "history": data.get("history", []),
            }
            print("Inventory loaded successfully.")
            return inventory
        except (json.JSONDecodeError, AttributeError):
            print("Error: No file found. Starting with empty inventory.")
    else:
        print("inventory.json not found. Starting with empty inventory.")

    return {"products": [], "history": []}

# for writing to inventory
def save_inventory(inventory):
    with open(INVENTORY_FILE, "w") as file:
        json.dump(inventory, file, indent=4)

    print("\nInventory saved successfully!")

# for auto incrementing the UUID
def get_next_product_id(inventory):
    highest_id = 0

    for product in inventory["products"]:
        product_id = str(product.get("id", ""))
        if product_id.upper().startswith("UUID"):
            number = product_id[4:]
            if number.isdigit():
                highest_id = max(highest_id, int(number))

    return f"UUID{highest_id + 1}"

# for finding the product by ID or by name
def find_product(inventory, product_id):
    for product in inventory["products"]:
        if product["id"].lower() == product_id.lower():
            return product
    return None

#history for all transactions
def record_transaction(inventory, product, action, change):
    inventory["history"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "product_id": product["id"],
        "action": action,
        "change": change,
        "stock_after": product["stock"],
    })

# for pirnting the product
def print_product(product):
    print(
        f"ID: {product['id']} | "
        f"Name: {product['name']} | "
        f"Price: ${product['price']:.2f} | "
        f"Stock: {product['stock']}"
    )

# for displaying all the products
def display_all(inventory):
    print("\nCurrent Inventory")
    print(LINE)

    if not inventory["products"]:
        print("No products in inventory.")
    else:
        for product in inventory["products"]:
            print_product(product)

    print(LINE)

# for adding a new product
def add_product(inventory):
    print("\nAdd New Product")
    product_id = get_next_product_id(inventory)

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

    if price < 0 or stock < 0:
        print("\nError: Price and stock cannot be negative.")
        return

    product = {"id": product_id, "name": name, "price": price, "stock": stock}
    inventory["products"].append(product)
    record_transaction(inventory, product, "ADD", stock)

    print("\nProduct added successfully!")

# for updating the product
def update_stock(inventory):
    print("\nUpdate Stock")
    product_id = input("Product ID (e.g. UUID1): ").strip()
    product = find_product(inventory, product_id)

    if product is None:
        print("\nError: Product not found.")
        return

    print(f"Current stock for {product['name']}: {product['stock']}")

    try:
        change = int(input("Enter quantity change (+/- to add/remove follow by a quantity (e.g., +10 or -5)): "))
    except ValueError:
        print("\nError: Enter a valid whole number.")
        return

    if product["stock"] + change < 0:
        print("\nError: Stock cannot go below zero.")
        return

    product["stock"] += change
    record_transaction(inventory, product, "UPDATE", change)

    print("\nStock updated successfully!")

# for search funciton
def search_product(inventory):
    print("\nSearch Product")
    keyword = input("Enter Product ID or Name: ").strip().lower()

    matches = [
        product for product in inventory["products"]
        if keyword == product["id"].lower() or keyword in product["name"].lower()
    ]

    if not matches:
        print("\nNo matching products found.")
        return

    print("\nSearch Results")
    print(LINE)
    for product in matches:
        print_product(product)
    print(LINE)


def show_menu():
    print("\n----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("----------------------------")


def main():
    print("=" * 42)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 42)
    print()

    inventory = load_inventory()

    while True:
        show_menu()
        choice = input("\nEnter option: ").strip()

        if choice == "1":
            display_all(inventory)
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
        elif choice == "5":
            save_inventory(inventory)
        elif choice == "6":
            print("\nExiting program. Goodbye!")
            break
        else:
            print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    main()