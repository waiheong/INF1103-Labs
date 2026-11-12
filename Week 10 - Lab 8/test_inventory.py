import io
import tempfile
import typing
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from file_handler import load_inventory, save_inventory
from inventory import Inventory
from order import Order
from order_line import OrderLine
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier


def output_of(func, *args) -> str:
    """Run func and return everything it printed."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        func(*args)
    return buffer.getvalue()


class InventoryTestCase(unittest.TestCase):
    """Shared fixtures: one supplier and one product of each type."""

    def setUp(self):
        self.supplier = Supplier("SUP1", "FreshFarm Pte Ltd", "sales@freshfarm.sg")
        self.watermelon = PhysicalProduct("UUID1", "Watermelon", 8.50, 20, self.supplier, 3.5)
        self.ebook = DigitalProduct("UUID2", "Mango Recipe eBook", 12.90, 50, self.supplier, 25)
        self.products: list[Product] = [self.watermelon, self.ebook]


class TestProductTypes(InventoryTestCase):
    def test_product_and_interface_are_abstract(self):
        with self.assertRaises(TypeError):
            Product("UUID9", "Generic Fruit", 1.00, 1, self.supplier)
        with self.assertRaises(TypeError):
            CanBeShipped()

    def test_only_physical_products_can_be_shipped(self):
        self.assertIsInstance(self.watermelon, CanBeShipped)
        self.assertNotIsInstance(self.ebook, CanBeShipped)
        self.assertAlmostEqual(self.watermelon.calculate_shipping_cost(), 12.00)  # $5 + 3.5 kg x $2

    def test_invalid_values_are_rejected(self):
        with self.assertRaises(ValueError):
            PhysicalProduct("X", "Rotten Apple", 1, 1, self.supplier, -2)
        with self.assertRaises(ValueError):
            Supplier("SUP9", "No Email Fruits", "not-an-email")


class TestSupplierAssociation(InventoryTestCase):
    def test_products_share_one_supplier_reference(self):
        self.assertIs(self.watermelon.get_supplier(), self.supplier)
        self.assertIs(self.ebook.get_supplier(), self.supplier)
        self.assertNotIsInstance(self.supplier, Product)

    def test_product_still_shows_supplier_after_del(self):
        del self.supplier  # removes the name, not the object the products refer to
        for product in self.products:
            self.assertIn("Supplier: FreshFarm Pte Ltd", output_of(product.display_information))


class TestInventoryAggregation(InventoryTestCase):
    def test_product_moves_between_inventories_without_being_destroyed(self):
        inventory_a, inventory_b = Inventory(), Inventory()
        inventory_a.add_product(self.watermelon)

        removed = inventory_a.remove_product("UUID1")
        self.assertIs(removed, self.watermelon)
        self.assertEqual(inventory_a.get_products(), [])

        removed.update_stock(-5)
        inventory_b.add_product(removed)
        self.assertIs(inventory_b.find_product("uuid1"), self.watermelon)
        self.assertEqual(self.watermelon.get_stock(), 15)

    def test_missing_and_duplicate_products(self):
        inventory = Inventory()
        inventory.add_product(self.watermelon)
        self.assertIsNone(inventory.find_product("NOPE"))
        self.assertIsNone(inventory.remove_product("NOPE"))
        with self.assertRaises(ValueError):
            inventory.add_product(self.watermelon)


class TestOrderComposition(InventoryTestCase):
    def setUp(self):
        super().setUp()
        self.order = Order("ORD1")
        self.order.add_order_line(self.watermelon, 2)
        self.order.add_order_line(self.ebook, 1)

    def test_order_creates_lines_and_calculates_total(self):
        self.assertTrue(all(isinstance(line, OrderLine) for line in self.order.get_order_lines()))
        self.assertAlmostEqual(self.order.calculate_total(), 29.90)  # 2 x 8.50 + 12.90

    def test_lines_cannot_be_added_from_outside(self):
        self.order.get_order_lines().append(OrderLine(self.watermelon, 99))
        self.assertEqual(len(self.order.get_order_lines()), 2)

    def test_same_product_in_two_orders(self):
        other_order = Order("ORD2")
        other_order.add_order_line(self.watermelon, 1)
        line_1, line_2 = self.order.get_order_lines()[0], other_order.get_order_lines()[0]
        self.assertIsNot(line_1, line_2)                          # two order lines...
        self.assertIs(line_1.get_product(), line_2.get_product())  # ...one product

    def test_removing_a_line_leaves_the_product(self):
        self.assertTrue(self.order.remove_order_line("UUID1"))
        self.assertAlmostEqual(self.order.calculate_total(), 12.90)
        self.assertEqual(self.watermelon.get_stock(), 20)


class TestLiskovAndPolymorphism(InventoryTestCase):
    def test_one_loop_runs_each_subclass_version(self):
        inventory = Inventory()
        for product in self.products:
            inventory.add_product(product)

        results = [product.get_fulfilment_info() for product in inventory.get_products()]
        self.assertEqual(results, ["Requires physical shipping",
                                "Delivered digitally via download link"])
        output = output_of(inventory.display_all)
        self.assertIn("Type: Physical", output)
        self.assertIn("Type: Digital", output)

    def test_update_stock_means_the_same_for_both_types(self):
        for product in self.products:
            product.update_stock(5)
            product.update_stock(-3)
            with self.assertRaises(ValueError):
                product.update_stock(-1000)
        self.assertEqual([product.get_stock() for product in self.products], [22, 52])


class TestTypeHints(unittest.TestCase):
    def test_design_types_are_type_hinted(self):
        hints = typing.get_type_hints
        self.assertIs(hints(Product.__init__)["supplier"], Supplier)
        self.assertEqual(hints(Inventory.find_product)["return"], Product | None)
        self.assertEqual(hints(Inventory.get_products)["return"], list[Product])
        self.assertEqual(hints(Order.get_order_lines)["return"], list[OrderLine])
        self.assertIs(hints(OrderLine.calculate_subtotal)["return"], float)


class TestJsonPersistence(InventoryTestCase):
    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "inventory.json"
            original = Inventory()
            for product in self.products:
                original.add_product(product)
            output_of(save_inventory, original, [self.supplier], file)

            restored, suppliers = Inventory(), []
            output_of(load_inventory, restored, suppliers, file)

        watermelon, ebook = restored.find_product("UUID1"), restored.find_product("UUID2")
        self.assertIsInstance(watermelon, PhysicalProduct)
        self.assertEqual(watermelon.get_weight(), 3.5)
        self.assertIsInstance(ebook, DigitalProduct)
        self.assertEqual(ebook.get_download_size(), 25)
        self.assertIs(watermelon.get_supplier(), ebook.get_supplier())  # one shared Supplier again


if __name__ == "__main__":
    unittest.main()