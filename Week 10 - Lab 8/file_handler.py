import json
from pathlib import Path

from digital_product import DigitalProduct
from inventory import Inventory
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier

INVENTORY_FILE = Path(__file__).parent / "inventory.json"

# loading the inventory files
UNKNOWN_SUPPLIER_ID = "SUP0"

_LOAD_ERRORS = (json.JSONDecodeError, AttributeError, KeyError, TypeError, ValueError)


def _create_supplier(data: dict) -> Supplier:
    return Supplier(data["id"], data["name"], data["contact_email"])


def _create_product(data: dict, suppliers_by_id: dict[str, Supplier]) -> Product:
    supplier = suppliers_by_id[data.get("supplier_id", UNKNOWN_SUPPLIER_ID)]
    common = (data["id"], data["name"], data["price"], data["stock"], supplier)

    product_type = data.get("type", "physical")
    if product_type == "physical":
        return PhysicalProduct(*common, data.get("weight", 0.0))
    if product_type == "digital":
        return DigitalProduct(*common, data["download_size"])
    raise ValueError(f"Unknown product type: {product_type}")


def _has_duplicates(ids: list[str]) -> bool:
    lowered = [i.lower() for i in ids]
    return len(lowered) != len(set(lowered))

# fill inventory and suppliers from the JSON file
def load_inventory(inventory: Inventory, suppliers: list[Supplier],
                file_path: Path = INVENTORY_FILE) -> None:

    if not file_path.exists():
        print("inventory.json not found. Starting with empty inventory.")
        return

    print("inventory.json found.")
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        loaded_suppliers = [_create_supplier(s) for s in data.get("suppliers", [])]
        suppliers_by_id = {s.get_supplier_id(): s for s in loaded_suppliers}

        product_data = data.get("products", [])
        if any("supplier_id" not in p for p in product_data) and UNKNOWN_SUPPLIER_ID not in suppliers_by_id:
            placeholder = Supplier(UNKNOWN_SUPPLIER_ID, "Unknown Supplier", "unknown@example.com")
            suppliers_by_id[UNKNOWN_SUPPLIER_ID] = placeholder
            loaded_suppliers.append(placeholder)

        # Products sharing a supplier_id end up sharing one Supplier object.
        products = [_create_product(p, suppliers_by_id) for p in product_data]
        history = data.get("history", [])

        if (_has_duplicates([p.get_product_id() for p in products])
                or _has_duplicates([s.get_supplier_id() for s in loaded_suppliers])):
            raise ValueError("Duplicate IDs in file.")
    except _LOAD_ERRORS:
        print("Error: inventory.json could not be read. Starting with empty inventory.")
        return

    suppliers.extend(loaded_suppliers)
    for product in products:
        inventory.add_product(product, record=False)
    inventory.load_history(history)
    print("Inventory loaded successfully.")

# for writing to suppliers, products and history to the JSON file
def save_inventory(inventory: Inventory, suppliers: list[Supplier],
                file_path: Path = INVENTORY_FILE) -> None:
    
    all_suppliers = {s.get_supplier_id(): s for s in suppliers}
    for product in inventory.get_products():
        supplier = product.get_supplier()
        all_suppliers.setdefault(supplier.get_supplier_id(), supplier)

    data = {"suppliers": [s.to_dict() for s in all_suppliers.values()], **inventory.to_dict()}
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

    print("\nInventory saved successfully!")
