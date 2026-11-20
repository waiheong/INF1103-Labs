import csv
import json
from pathlib import Path

from inventory import Inventory
from product import Product
from product_factory import ProductFactory
from supplier import Supplier

INVENTORY_FILE = Path(__file__).parent / "inventory.json"

UNKNOWN_SUPPLIER_ID = "SUP0"

CSV_COLUMNS = ["product_type", "product_id", "name", "price", "stock_quantity"]

_JSON_DATA_ERRORS = (json.JSONDecodeError, AttributeError, KeyError, TypeError, ValueError)

# JSON inventory 

def _create_supplier(data: dict) -> Supplier:
    return Supplier(data["id"], data["name"], data["contact_email"])

def _create_product(data: dict, suppliers_by_id: dict[str, Supplier]) -> Product:
    supplier = suppliers_by_id[data.get("supplier_id", UNKNOWN_SUPPLIER_ID)]
    return ProductFactory.create(
        data.get("type", "physical"), data["id"], data["name"], data["price"], data["stock"],
        supplier, weight=data.get("weight", 0.0), download_size=data.get("download_size", 0.0),
    )

def _has_duplicates(ids: list[str]) -> bool:
    lowered = [i.lower() for i in ids]
    return len(lowered) != len(set(lowered))

def _parse_inventory(data: dict) -> tuple[list[Supplier], list[Product], list[dict]]:
    suppliers = [_create_supplier(s) for s in data.get("suppliers", [])]
    suppliers_by_id = {s.get_supplier_id(): s for s in suppliers}

    product_data = data.get("products", [])
    if any("supplier_id" not in p for p in product_data) and UNKNOWN_SUPPLIER_ID not in suppliers_by_id:
        placeholder = Supplier(UNKNOWN_SUPPLIER_ID, "Unknown Supplier", "unknown@example.com")
        suppliers_by_id[UNKNOWN_SUPPLIER_ID] = placeholder
        suppliers.append(placeholder)

    # Products sharing a supplier_id end up sharing one Supplier object.
    products = [_create_product(p, suppliers_by_id) for p in product_data]

    if (_has_duplicates([p.get_product_id() for p in products])
            or _has_duplicates([s.get_supplier_id() for s in suppliers])):
        raise ValueError("Duplicate IDs in file.")
    return suppliers, products, data.get("history", [])

def load_inventory(inventory: Inventory, suppliers: list[Supplier],
                file_path: Path = INVENTORY_FILE) -> None:
    try:
        with open(file_path, "r") as file:
            loaded_suppliers, products, history = _parse_inventory(json.load(file))
    except FileNotFoundError:
        print("inventory.json not found. Starting with empty inventory.")
        return
    except _JSON_DATA_ERRORS:
        print("Error: inventory.json could not be read. Starting with empty inventory.")
        return

    suppliers.extend(loaded_suppliers)
    for product in products:
        inventory.add_product(product, record=False)
    inventory.load_history(history)
    print("Inventory loaded successfully.")


def save_inventory(inventory: Inventory, suppliers: list[Supplier],
                file_path: Path = INVENTORY_FILE) -> None:
    
    all_suppliers = {s.get_supplier_id(): s for s in suppliers}
    for product in inventory.get_products():
        supplier = product.get_supplier()
        all_suppliers.setdefault(supplier.get_supplier_id(), supplier)

    data = {"suppliers": [s.to_dict() for s in all_suppliers.values()], **inventory.to_dict()}
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    except OSError as error:  # e.g. folder is read-only or the disk is full
        print(f"\nError: could not save the inventory ({error.strerror}).")
        return

    print("\nInventory saved successfully!")


#  CSV import 
def _parse_csv_row(row: list[str]) -> tuple[str, str, str, float, int]:
    if len(row) != len(CSV_COLUMNS):
        raise ValueError(f"expected {len(CSV_COLUMNS)} values but found {len(row)}")

    product_type, product_id, name, price_text, stock_text = (value.strip() for value in row)
    try:
        price = float(price_text)
    except ValueError:
        raise ValueError(f"price '{price_text}' is not a number") from None
    try:
        stock = int(stock_text)
    except ValueError:
        raise ValueError(f"stock quantity '{stock_text}' is not a whole number") from None
    return product_type, product_id, name, price, stock


def load_products(path: str, inventory: Inventory, supplier: Supplier) -> None:
    try:
        file = open(path, newline="")
    except FileNotFoundError:
        print(f"Products file not found: {path}")
    else:
        loaded = 0
        with file:
            reader = csv.reader(file)
            next(reader, None)  
            for line_number, row in enumerate(reader, start=2):
                if not row:
                    continue  
                try:
                    product_type, product_id, name, price, stock = _parse_csv_row(row)
                    product = ProductFactory.create(product_type, product_id, name, price, stock, supplier)
                    inventory.add_product(product)
                except ValueError as error:
                    print(f"Skipped line {line_number}: {error}")
                else:
                    loaded += 1
        print(f"{loaded} products loaded.")
    finally:
        print("Load attempt finished.")
