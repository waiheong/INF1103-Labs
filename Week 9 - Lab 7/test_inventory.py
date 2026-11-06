import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from product import Product
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from can_be_shipped import CanBeShipped
from inventory import Inventory
from file_handler import load_inventory, save_inventory

def captured_output(func, *args):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        func(*args)
    return buffer.getvalue()

class TestPhysicalProduct(unittest.TestCase):
    def setUp(self):
        self.watermelon = PhysicalProduct("UUID1", "Watermelon", 8.50, 5, 3.5)

    def test_stores_weight(self):
        self.assertEqual(self.watermelon.get_weight(), 3.5)

    # from Product and from PhysicalProduct
    def test_displays_parent_info_and_weight(self):
        output = captured_output(self.watermelon.display_information)
        self.assertIn("ID: UUID1 | Name: Watermelon | Price: $8.50 | Stock: 5", output)
        self.assertIn("Weight: 3.50 kg", output)

    def test_fulfilment_info(self):
        self.assertEqual(self.watermelon.get_fulfilment_info(), "Requires physical shipping")

    def test_shipping_cost_for_different_weights(self):
        self.assertAlmostEqual(PhysicalProduct("A", "Blueberry", 1, 1, 0).calculate_shipping_cost(), 5.00)
        self.assertAlmostEqual(PhysicalProduct("B", "Lemon", 1, 1, 0.25).calculate_shipping_cost(), 5.50)
        self.assertAlmostEqual(self.watermelon.calculate_shipping_cost(), 12.00)
        self.assertAlmostEqual(PhysicalProduct("C", "Jackfruit", 1, 1, 80).calculate_shipping_cost(), 165.00)

    def test_is_a_product_and_can_be_shipped(self):
        self.assertIsInstance(self.watermelon, Product)
        self.assertIsInstance(self.watermelon, CanBeShipped)

    def test_negative_weight_rejected(self):
        with self.assertRaises(ValueError):
            PhysicalProduct("X", "Rotten Apple", 1, 1, -2)

    def test_inherited_update_stock_still_works(self):
        self.watermelon.update_stock(-2)
        self.assertEqual(self.watermelon.get_stock(), 3)
        with self.assertRaises(ValueError):
            self.watermelon.update_stock(-10)


class TestDigitalProduct(unittest.TestCase):
    def setUp(self):
        self.ebook = DigitalProduct("UUID2", "Mango Recipe eBook", 12.90, 100, 25)

    def test_stores_download_size(self):
        self.assertEqual(self.ebook.get_download_size(), 25)

    def test_displays_parent_info_and_download_size(self):
        output = captured_output(self.ebook.display_information)
        self.assertIn("ID: UUID2 | Name: Mango Recipe eBook | Price: $12.90 | Stock: 100", output)
        self.assertIn("Download size: 25.00 MB", output)

    def test_fulfilment_info(self):
        self.assertEqual(self.ebook.get_fulfilment_info(), "Delivered digitally via download link")

    def test_not_required_to_ship(self):
        self.assertIsInstance(self.ebook, Product)
        self.assertNotIsInstance(self.ebook, CanBeShipped)
        self.assertFalse(hasattr(self.ebook, "calculate_shipping_cost"))

    def test_negative_download_size_rejected(self):
        with self.assertRaises(ValueError):
            DigitalProduct("X", "Broken Banana eBook", 1, 1, -1)


class TestAbstractClasses(unittest.TestCase):
    def test_product_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            Product("UUID9", "Generic Fruit", 10.00, 1)

    def test_can_be_shipped_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            CanBeShipped()

    def test_subclass_missing_abstract_method_cannot_be_instantiated(self):
        class Incomplete(Product):
            pass

        with self.assertRaises(TypeError):
            Incomplete("UUID9", "Plain Pear", 1, 1)


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.inventory = Inventory()
        self.inventory.add_product(PhysicalProduct("UUID1", "Apple", 1.20, 15, 0.2))
        self.inventory.add_product(DigitalProduct("UUID2", "Lemon Juice Video Guide", 9.90, 50, 850))

    def test_find_and_search_return_both_types(self):
        self.assertIsInstance(self.inventory.find_product("uuid1"), PhysicalProduct)
        self.assertIsInstance(self.inventory.find_product("UUID2"), DigitalProduct)
        self.assertEqual(len(self.inventory.search_product("lemon")), 1)
        self.assertEqual(self.inventory.search_product("dragonfruit"), [])

    def test_update_stock(self):
        self.inventory.update_stock("UUID1", -5)
        self.assertEqual(self.inventory.find_product("UUID1").get_stock(), 10)
        with self.assertRaises(ValueError):
            self.inventory.update_stock("UUID1", -100)
        with self.assertRaises(ValueError):
            self.inventory.update_stock("NOPE", 1)

    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):
            self.inventory.add_product(DigitalProduct("uuid1", "Papaya Smoothie eBook", 1, 1, 1))

    def test_generate_product_id(self):
        self.assertEqual(self.inventory.generate_product_id(), "UUID3")

    def test_display_all_shows_both_types(self):
        output = captured_output(self.inventory.display_all)
        self.assertIn("Weight: 0.20 kg", output)
        self.assertIn("Download size: 850.00 MB", output)


class TestJsonPersistence(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.file = Path(self.folder.name) / "inventory.json"

    def tearDown(self):
        self.folder.cleanup()

    def test_save_and_load_preserves_types(self):
        original = Inventory()
        original.add_product(PhysicalProduct("UUID1", "Watermelon", 8.50, 5, 3.5))
        original.add_product(DigitalProduct("UUID2", "Mango Recipe eBook", 12.90, 100, 25))
        captured_output(save_inventory, original, self.file)

        saved = json.loads(self.file.read_text())
        self.assertEqual([p["type"] for p in saved["products"]], ["physical", "digital"])

        restored = Inventory()
        captured_output(load_inventory, restored, self.file)

        watermelon = restored.find_product("UUID1")
        ebook = restored.find_product("UUID2")
        self.assertIsInstance(watermelon, PhysicalProduct)
        self.assertEqual(watermelon.get_weight(), 3.5)
        self.assertEqual(watermelon.get_price(), 8.50)
        self.assertIsInstance(ebook, DigitalProduct)
        self.assertEqual(ebook.get_download_size(), 25)
        self.assertEqual(ebook.get_stock(), 100)

    def test_lab6_file_without_type_loads_as_physical(self):
        self.file.write_text(json.dumps({
            "products": [{"id": "UUID1", "name": "Old Banana", "price": 10.0, "stock": 3}],
            "history": [],
        }))
        restored = Inventory()
        captured_output(load_inventory, restored, self.file)
        self.assertIsInstance(restored.find_product("UUID1"), PhysicalProduct)

    def test_bad_file_starts_empty(self):
        self.file.write_text(json.dumps({
            "products": [{"id": "UUID1", "name": "Mystery Fruit", "price": 1, "stock": 1, "type": "alien"}],
        }))
        restored = Inventory()
        output = captured_output(load_inventory, restored, self.file)
        self.assertIn("could not be read", output)
        self.assertIsNone(restored.find_product("UUID1"))


if __name__ == "__main__":
    unittest.main()