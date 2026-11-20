import unittest

from order import Order
from product_factory import ProductFactory
from tests.helpers import make_supplier


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.supplier = make_supplier()

    def create(self, product_type: str = "physical", price: float = 10.0, stock: int = 5):
        return ProductFactory.create(product_type, "P001", "Desk Lamp", price, stock, self.supplier)

    def test_price_must_be_greater_than_zero(self):
        for price in (0, -5):
            with self.assertRaises(ValueError) as caught:
                self.create(price=price)
            self.assertEqual(str(caught.exception), "Price must be greater than zero.")

    def test_stock_quantity_cannot_be_negative(self):
        with self.assertRaises(ValueError) as caught:
            self.create(stock=-1)
        self.assertEqual(str(caught.exception), "Stock quantity cannot be negative.")
        self.assertEqual(self.create(stock=0).get_stock(), 0)  # zero is allowed

    def test_order_line_quantity_must_be_greater_than_zero(self):
        order = Order("ORD1")
        for quantity in (0, -3):
            with self.assertRaises(ValueError) as caught:
                order.add_order_line(self.create(), quantity)
            self.assertEqual(str(caught.exception), "Quantity must be greater than zero.")
        self.assertEqual(order.get_order_lines(), [])

    def test_both_product_types_keep_the_same_rules(self):
        # LSP: a subclass may not skip or loosen a rule its parent enforces.
        for product_type in ("physical", "digital"):
            with self.assertRaises(ValueError):
                self.create(product_type, price=0)
            with self.assertRaises(ValueError):
                self.create(product_type, stock=-1)
            product = self.create(product_type, stock=5)
            with self.assertRaises(ValueError):
                product.update_stock(-6)
            self.assertEqual(product.get_stock(), 5)

if __name__ == "__main__":
    unittest.main()
