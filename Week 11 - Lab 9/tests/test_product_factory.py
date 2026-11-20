import ast
import unittest

from digital_product import DigitalProduct
from physical_product import PhysicalProduct
from product import Product
from product_factory import ProductFactory
from tests.helpers import make_supplier, project_sources

# The only files allowed to call the concrete constructors directly.
ALLOWED_CREATORS = {"product_factory.py"}

class TestProductFactory(unittest.TestCase):
    def setUp(self):
        self.supplier = make_supplier()

    def test_creates_the_right_type_with_its_details(self):
        lamp = ProductFactory.create("physical", "P001", "Desk Lamp", 25.00, 10, self.supplier, weight=1.2)
        editor = ProductFactory.create("digital", "D001", "Photo Editor", 49.90, 100, self.supplier,
                                       download_size=850)
        self.assertIsInstance(lamp, PhysicalProduct)
        self.assertEqual(lamp.get_weight(), 1.2)
        self.assertIsInstance(editor, DigitalProduct)
        self.assertEqual(editor.get_download_size(), 850)
        for product in (lamp, editor):
            self.assertIsInstance(product, Product)
            self.assertIs(product.get_supplier(), self.supplier)

    def test_type_name_ignores_case_and_spaces(self):
        product = ProductFactory.create(" Physical ", "P001", "Desk Lamp", 25.00, 10, self.supplier)
        self.assertIsInstance(product, PhysicalProduct)

    def test_unknown_type_raises_clear_value_error(self):
        with self.assertRaises(ValueError) as caught:
            ProductFactory.create("service", "S001", "Installation", 30.00, 5, self.supplier)
        self.assertEqual(str(caught.exception), "Unknown product type: service")

    def test_program_creates_products_only_through_the_factory(self):
        for filename, tree in project_sources().items():
            if filename in ALLOWED_CREATORS:
                continue
            direct_calls = [
                node.lineno for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in ("PhysicalProduct", "DigitalProduct")
            ]
            self.assertEqual(direct_calls, [], f"{filename} creates products directly on lines {direct_calls}")


if __name__ == "__main__":
    unittest.main()
