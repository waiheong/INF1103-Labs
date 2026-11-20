import ast
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from file_handler import load_inventory, load_products
from input_helpers import get_choice, get_int, get_positive_float, get_positive_int, get_text
from inventory import Inventory
from tests.helpers import make_supplier, output_of, project_sources

LAB_CSV = """product_type,product_id,name,price,stock_quantity
physical,P001,Desk Lamp,25.00,10
digital,D001,Photo Editor,49.90,100
service,S001,Installation,30.00,5
physical,P002,Office Chair,abc,3
physical,P003,Monitor Stand,39.50,7
"""


def answer(*replies: str):
    return patch("builtins.input", side_effect=list(replies))

class TestUserInput(unittest.TestCase):
    def test_get_positive_float_asks_again_until_valid(self):
        with answer("abc", "-5", "12.50"):
            output = output_of(lambda: self.assertEqual(get_positive_float("Price: "), 12.5))
        self.assertEqual(output.splitlines(), [
            "Please enter a valid number, e.g. 12.50",
            "Please enter a number greater than zero.",
        ])

    def test_other_helpers_also_ask_again(self):
        with answer("two", "0", "2"):
            self.assertEqual(output_of_value(get_positive_int, "Quantity: "), 2)
        with answer("ten", "-5"):
            self.assertEqual(output_of_value(get_int, "Change: "), -5)
        with answer("   ", "Kiwi"):
            self.assertEqual(output_of_value(get_text, "Name: "), "Kiwi")
        with answer("3", "2"):
            self.assertEqual(output_of_value(get_choice, "Type: ", ["1", "2"]), "2")


def output_of_value(func, *args):
    result = []
    output_of(lambda: result.append(func(*args)))
    return result[0]


class TestLoadProducts(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.folder.name) / "products.csv"
        self.inventory = Inventory()

    def tearDown(self):
        self.folder.cleanup()

    def test_bad_rows_are_reported_and_skipped(self):
        self.csv_path.write_text(LAB_CSV)
        output = output_of(load_products, str(self.csv_path), self.inventory, make_supplier())

        self.assertEqual(output.splitlines(), [
            "Skipped line 4: Unknown product type: service",
            "Skipped line 5: price 'abc' is not a number",
            "3 products loaded.",
            "Load attempt finished.",
        ])
        loaded_ids = [p.get_product_id() for p in self.inventory.get_products()]
        self.assertEqual(loaded_ids, ["P001", "D001", "P003"])

    def test_missing_file_is_handled_gracefully(self):
        output = output_of(load_products, str(self.csv_path), self.inventory, make_supplier())
        self.assertEqual(output.splitlines(), [
            f"Products file not found: {self.csv_path}",
            "Load attempt finished.",  # finally still runs; the else block does not
        ])
        self.assertEqual(self.inventory.get_products(), [])

    def test_duplicate_and_short_rows_are_skipped(self):
        self.csv_path.write_text(LAB_CSV + "physical,P001,Desk Lamp Copy,25.00,1\nphysical,P004\n")
        output = output_of(load_products, str(self.csv_path), self.inventory, make_supplier())
        self.assertIn("Skipped line 7: A product with ID P001 already exists.", output)
        self.assertIn("Skipped line 8: expected 5 values but found 2", output)
        self.assertIn("3 products loaded.", output)

    def test_missing_inventory_json_is_handled_gracefully(self):
        suppliers = []
        output = output_of(load_inventory, self.inventory, suppliers, self.csv_path.with_suffix(".json"))
        self.assertIn("not found", output)
        self.assertEqual((self.inventory.get_products(), suppliers), ([], []))


class TestSpecificExceptions(unittest.TestCase):
    def test_every_except_names_a_specific_exception(self):
        too_broad = {"Exception", "BaseException"}
        for filename, tree in project_sources().items():
            for handler in (n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)):
                self.assertIsNotNone(handler.type, f"bare 'except:' in {filename} line {handler.lineno}")
                names = {n.id for n in ast.walk(handler.type) if isinstance(n, ast.Name)}
                self.assertFalse(names & too_broad, f"broad except in {filename} line {handler.lineno}")


if __name__ == "__main__":
    unittest.main()
