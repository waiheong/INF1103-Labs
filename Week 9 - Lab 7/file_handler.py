import json
from pathlib import Path

from physical_product import PhysicalProduct
from digital_product import DigitalProduct

# loading of inventory data, and saving inventory data
INVENTORY_FILE = Path(__file__).parent / "inventory.json"

def create_product(item):
    product_type = item.get("type", "physical")
    common = (item["id"], item["name"], item["price"], item["stock"])

    if product_type == "physical":
        return PhysicalProduct(*common, item.get("weight", 0.0))
    if product_type == "digital":
        return DigitalProduct(*common, item["download_size"])

    raise ValueError(f"Unknown product type: {product_type}")

# read inventory.json and display if nth is inside, i will create a new json file
def load_inventory(inventory, file_path=INVENTORY_FILE):
    if not file_path.exists():
        print("inventory.json not found. Starting with empty inventory.")
        return

    print("inventory.json found.")
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        # build first, bad entry doesn't leave a half-loaded inventory
        products = [create_product(item) for item in data.get("products", [])]
        history = data.get("history", [])

        ids = [product.get_product_id().lower() for product in products]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate product IDs in file.")

    except (json.JSONDecodeError, AttributeError, KeyError, TypeError, ValueError):
        print("Error: inventory.json could not be read. Starting with empty inventory.")
        return

    for product in products:
        inventory.add_product(product, record=False)
    inventory.load_history(history)

    print("Inventory loaded successfully.")

# writing into inventory
def save_inventory(inventory, file_path=INVENTORY_FILE):
    with open(file_path, "w") as file:
        json.dump(inventory.to_dict(), file, indent=4)

    print("\nInventory saved successfully!")
