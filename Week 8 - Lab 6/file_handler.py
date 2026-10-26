import json
from pathlib import Path
from product import Product

# loadinf of inventroy.son 
INVENTORY_FILE = Path(__file__).parent / "inventory.json"

def load_inventory(inventory, file_path=INVENTORY_FILE):
    if not file_path.exists():
        print("inventory.json not found. Starting with empty inventory.")
        return

    print("inventory.json found.")
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        products = [
            Product(item["id"], item["name"], item["price"], item["stock"])
            for item in data.get("products", [])
        ]
        history = data.get("history", [])

    except (json.JSONDecodeError, AttributeError, KeyError, TypeError, ValueError):
        print("Error: inventory.json could not be read. Starting with empty inventory.")
        return

    for product in products:
        inventory.add_product(product, record=False)
    inventory.load_history(history)

    print("Inventory loaded successfully.")

# write to the invertory.json file
def save_inventory(inventory, file_path=INVENTORY_FILE):
    with open(file_path, "w") as file:
        json.dump(inventory.to_dict(), file, indent=4)

    print("\nInventory saved successfully!")
