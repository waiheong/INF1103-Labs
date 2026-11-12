from collections.abc import Callable

from digital_product import DigitalProduct
from file_handler import load_inventory, save_inventory
from inventory import Inventory
from order import Order
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier

SEPARATOR = "-" * 60

MENU_ITEMS = [
    ("1", "Display All Products"),
    ("2", "Add Product"),
    ("3", "Update Stock"),
    ("4", "Search Product"),
    ("5", "Remove Product"),
    ("6", "Add Supplier"),
    ("7", "Display Suppliers"),
    ("8", "Create Order"),
    ("9", "Save Inventory"),
    ("0", "Exit"),
]


def show_menu() -> None:
    print("\n----------- MENU -----------")
    for key, label in MENU_ITEMS:
        print(f"{key}. {label}")
    print("----------------------------")


# for uppliers 
def find_supplier(suppliers: list[Supplier], supplier_id: str) -> Supplier | None:
    wanted = supplier_id.strip().lower()
    return next((s for s in suppliers if s.get_supplier_id().lower() == wanted), None)

def next_supplier_id(suppliers: list[Supplier]) -> str:
    numbers = [
        int(s.get_supplier_id()[3:]) for s in suppliers
        if s.get_supplier_id().upper().startswith("SUP") and s.get_supplier_id()[3:].isdigit()
    ]
    return f"SUP{max(numbers, default=0) + 1}"

def display_suppliers(suppliers: list[Supplier]) -> None:
    print("\nSuppliers")
    print(SEPARATOR)
    if not suppliers:
        print("No suppliers yet.")
    for supplier in suppliers:
        supplier.display_information()
    print(SEPARATOR)

def add_supplier(suppliers: list[Supplier]) -> None:
    print("\nAdd New Supplier")
    supplier_id = next_supplier_id(suppliers)
    name = input("Supplier Name: ")
    contact_email = input("Contact Email: ")

    try:
        supplier = Supplier(supplier_id, name, contact_email)
    except ValueError as error:
        print(f"\nError: {error}")
        return

    suppliers.append(supplier)
    print(f"\nSupplier added successfully! (ID: {supplier_id})")


# for products
def add_product(inventory: Inventory, suppliers: list[Supplier]) -> None:
    print("\nAdd New Product")
    if not suppliers:
        print("\nError: Add a supplier first (option 6).")
        return

    print("1. Physical Product")
    print("2. Digital Product")
    product_type = input("Choose product type: ").strip()
    if product_type not in ("1", "2"):
        print("\nError: Choose 1 for physical or 2 for digital.")
        return

    name = input("Product Name: ").strip()
    if not name:
        print("\nError: Product name cannot be empty.")
        return

    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
        if product_type == "1":
            extra = float(input("Weight (kg): "))
        else:
            extra = float(input("Download Size (MB): "))
    except ValueError:
        print("\nError: Price, weight and download size must be numbers, "
            "and stock must be a whole number.")
        return

    display_suppliers(suppliers)
    supplier = find_supplier(suppliers, input("Supplier ID (e.g. SUP1): "))
    if supplier is None:
        print("\nError: Supplier not found.")
        return

    product_class = PhysicalProduct if product_type == "1" else DigitalProduct
    try:
        product = product_class(inventory.generate_product_id(), name, price, stock, supplier, extra)
        inventory.add_product(product)
    except ValueError as error:
        print(f"\nError: {error}")
        return

    print(f"\nProduct added successfully! (ID: {product.get_product_id()})")

def update_stock(inventory: Inventory) -> None:
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

def search_products(inventory: Inventory) -> None:
    print("\nSearch Product")
    matches = inventory.search_product(input("Enter Product ID or Name: "))
    if not matches:
        print("\nNo matching products found.")
        return
    inventory.display_products(matches, "Search Results")

def remove_product(inventory: Inventory) -> None:
    print("\nRemove Product")
    product: Product | None = inventory.remove_product(input("Product ID (e.g. UUID1): "))
    if product is None:
        print("\nError: Product not found.")
        return
    print(f"\n{product.get_name()} removed from the inventory.")

# for orders
def create_order(inventory: Inventory, orders: list[Order]) -> None:
    """Build an order line by line. Orders are kept for this session only."""
    order = Order(f"ORD{len(orders) + 1}")
    print(f"\nCreate Order {order.get_order_id()}")
    print("Enter a product ID and quantity for each item. Leave the product ID blank to finish.")

    while product_id := input("\nProduct ID: ").strip():
        product = inventory.find_product(product_id)
        if product is None:
            print("Error: Product not found.")
            continue

        try:
            quantity = int(input(f"Quantity of {product.get_name()}: "))
        except ValueError:
            print("Error: Enter a valid whole number.")
            continue

        if quantity > product.get_stock():
            print(f"Error: Only {product.get_stock()} in stock.")
            continue

        try:
            order.add_order_line(product, quantity)
        except ValueError as error:
            print(f"Error: {error}")
            continue
        print(f"Added {quantity} x {product.get_name()}.")

    if not order.get_order_lines():
        print("\nNo items added. Order cancelled.")
        return

    orders.append(order)
    order.display_order()

# main loop
def main() -> None:
    print("=" * 42)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 42)
    print()

    inventory = Inventory()
    suppliers: list[Supplier] = []
    orders: list[Order] = []
    load_inventory(inventory, suppliers)

    actions: dict[str, Callable[[], None]] = {
        "1": inventory.display_all,
        "2": lambda: add_product(inventory, suppliers),
        "3": lambda: update_stock(inventory),
        "4": lambda: search_products(inventory),
        "5": lambda: remove_product(inventory),
        "6": lambda: add_supplier(suppliers),
        "7": lambda: display_suppliers(suppliers),
        "8": lambda: create_order(inventory, orders),
        "9": lambda: save_inventory(inventory, suppliers),
    }

    while True:
        show_menu()
        choice = input("\nEnter option: ").strip()
        if choice == "0":
            print("\nExiting program. Goodbye!")
            break

        action = actions.get(choice)
        if action is None:
            print("\nInvalid option. Please try again.")
        else:
            action()

if __name__ == "__main__":
    main()
