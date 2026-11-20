from collections.abc import Callable

from discount_strategy import BulkDiscount, DiscountStrategy, NoDiscount, PercentageDiscount
from file_handler import load_inventory, load_products, save_inventory
from input_helpers import (get_choice, get_int, get_non_negative_float, get_non_negative_int,
                           get_positive_float, get_positive_int, get_text)
from inventory import Inventory
from order import Order
from product import Product
from product_factory import ProductFactory
from student_discount import StudentDiscount
from supplier import Supplier

SEPARATOR = "-" * 60
DEFAULT_PRODUCTS_FILE = "products.csv"

MENU_ITEMS = [
    ("1", "Display All Products"),
    ("2", "Add Product"),
    ("3", "Update Stock"),
    ("4", "Search Product"),
    ("5", "Remove Product"),
    ("6", "Add Supplier"),
    ("7", "Display Suppliers"),
    ("8", "Create Order"),
    ("9", "Import Products from CSV"),
    ("10", "Save Inventory"),
    ("0", "Exit"),
]

# Menu choice
PRODUCT_TYPES = {
    "1": ("physical", "weight", "Weight (kg): "),
    "2": ("digital", "download_size", "Download Size (MB): "),
}

# The store's promotions. Strategy objects hold no per-order state, so one
# instance can be shared by every order that uses it.
DISCOUNTS: dict[str, DiscountStrategy] = {
    "1": NoDiscount(),
    "2": PercentageDiscount(10),
    "3": BulkDiscount(200, 20),
    "4": StudentDiscount(),
}

def show_menu() -> None:
    print("\n----------- MENU -----------")
    for key, label in MENU_ITEMS:
        print(f"{key}. {label}")
    print("----------------------------")

# Suppliers 
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

def choose_supplier(suppliers: list[Supplier]) -> Supplier:
    display_suppliers(suppliers)
    while (supplier := find_supplier(suppliers, get_text("Supplier ID (e.g. SUP1): "))) is None:
        print("Supplier not found. Please enter one of the IDs above.")
    return supplier

def add_supplier(suppliers: list[Supplier]) -> None:
    print("\nAdd New Supplier")
    supplier_id = next_supplier_id(suppliers)
    name = get_text("Supplier Name: ")
    while True:
        try:
            supplier = Supplier(supplier_id, name, get_text("Contact Email: "))
            break
        except ValueError as error:
            print(f"Error: {error}")

    suppliers.append(supplier)
    print(f"\nSupplier added successfully! (ID: {supplier_id})")


# Products 
def add_product(inventory: Inventory, suppliers: list[Supplier]) -> None:
    print("\nAdd New Product")
    if not suppliers:
        print("\nError: Add a supplier first (option 6).")
        return

    print("1. Physical Product")
    print("2. Digital Product")
    product_type, detail_name, detail_prompt = PRODUCT_TYPES[get_choice("Choose product type: ", list(PRODUCT_TYPES))]

    name = get_text("Product Name: ")
    price = get_positive_float("Price: ")
    stock = get_non_negative_int("Stock Quantity: ")
    detail = {detail_name: get_non_negative_float(detail_prompt)}
    supplier = choose_supplier(suppliers)

    try:
        product = ProductFactory.create(product_type, inventory.generate_product_id(),
                                        name, price, stock, supplier, **detail)
        inventory.add_product(product)
    except ValueError as error:
        print(f"\nError: {error}")
        return

    print(f"\nProduct added successfully! (ID: {product.get_product_id()})")

def update_stock(inventory: Inventory) -> None:
    print("\nUpdate Stock")
    product = inventory.find_product(input("Product ID (e.g. UUID1): "))
    if product is None:
        print("\nError: Product not found.")
        return

    print(f"Current stock for {product.get_name()}: {product.get_stock()}")
    while True:
        change = get_int("Enter quantity change (e.g. +10 to add, -5 to remove): ")
        try:
            inventory.update_stock(product.get_product_id(), change)
            break
        except ValueError as error:  # stock would go below zero
            print(f"Error: {error} Please try again.")

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

def import_products(inventory: Inventory, suppliers: list[Supplier]) -> None:
    print("\nImport Products from CSV")
    if not suppliers:
        print("\nError: Add a supplier first (option 6).")
        return

    path = input(f"CSV file [{DEFAULT_PRODUCTS_FILE}]: ").strip() or DEFAULT_PRODUCTS_FILE
    print("The imported products will be linked to this supplier:")
    load_products(path, inventory, choose_supplier(suppliers))


# Orders 
def choose_discount() -> DiscountStrategy:
    print("\nDiscount")
    for key, discount in DISCOUNTS.items():
        print(f"{key}. {discount.describe()}")
    return DISCOUNTS[get_choice("Choose discount: ", list(DISCOUNTS))]

def create_order(inventory: Inventory, orders: list[Order]) -> None:
    """Build an order line by line, then pick a discount. Orders last for this session only."""
    order = Order(f"ORD{len(orders) + 1}")
    print(f"\nCreate Order {order.get_order_id()}")
    print("Enter a product ID and quantity for each item. Leave the product ID blank to finish.")

    while product_id := input("\nProduct ID: ").strip():
        product = inventory.find_product(product_id)
        if product is None:
            print("Product not found. Please try again.")
            continue

        while (quantity := get_positive_int(f"Quantity of {product.get_name()}: ")) > product.get_stock():
            print(f"Only {product.get_stock()} in stock. Please enter a smaller quantity.")

        order.add_order_line(product, quantity)
        print(f"Added {quantity} x {product.get_name()}.")

    if not order.get_order_lines():
        print("\nNo items added. Order cancelled.")
        return

    order.set_discount(choose_discount())
    orders.append(order)
    order.display_order()


# Main loop 
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
        "9": lambda: import_products(inventory, suppliers),
        "10": lambda: save_inventory(inventory, suppliers),
    }

    try:
        while True:
            show_menu()
            choice = input("\nEnter option: ").strip()
            if choice == "0":
                break

            action = actions.get(choice)
            if action is None:
                print("\nInvalid option. Please try again.")
            else:
                action()
    except (KeyboardInterrupt, EOFError):  # Ctrl+C, or input closed
        print("\n\nInput ended. Unsaved changes were not saved.")
    print("\nExiting program. Goodbye!")

if __name__ == "__main__":
    main()
