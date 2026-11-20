import ast
import inspect
import textwrap
import unittest

from discount_strategy import BulkDiscount, DiscountStrategy, NoDiscount, PercentageDiscount
from order import Order
from product_factory import ProductFactory
from student_discount import StudentDiscount
from tests.helpers import make_supplier


def order_totalling_250(discount: DiscountStrategy | None = None) -> Order:
    lamp = ProductFactory.create("physical", "P001", "Desk Lamp", 25.00, 50, make_supplier(), weight=1.2)
    order = Order("ORD1", discount)
    order.add_order_line(lamp, 10)  # 10 x $25.00 = $250.00
    return order


class TestStrategies(unittest.TestCase):
    def test_each_strategy_applies_its_own_rule(self):
        self.assertEqual(NoDiscount().apply(250), 250)
        self.assertAlmostEqual(PercentageDiscount(10).apply(250), 225)
        self.assertAlmostEqual(BulkDiscount(200, 20).apply(250), 230)
        self.assertAlmostEqual(BulkDiscount(200, 20).apply(199.99), 199.99)  # below threshold
        self.assertAlmostEqual(BulkDiscount(200, 20).apply(200), 180)        # threshold included
        self.assertAlmostEqual(StudentDiscount().apply(250), 237.5)

    def test_base_class_cannot_be_used_directly(self):
        with self.assertRaises(TypeError):
            DiscountStrategy()

    def test_invalid_strategy_settings_are_rejected(self):
        for bad in (lambda: PercentageDiscount(0), lambda: PercentageDiscount(150),
                    lambda: BulkDiscount(-1, 20), lambda: BulkDiscount(200, 0)):
            with self.assertRaises(ValueError):
                bad()


class TestOrderUsesStrategy(unittest.TestCase):
    def test_new_order_defaults_to_no_discount(self):
        order = order_totalling_250()
        self.assertIsInstance(order.get_discount(), NoDiscount)
        self.assertAlmostEqual(order.calculate_total(), 250)

    def test_set_discount_changes_strategy_on_existing_order(self):
        order = order_totalling_250(BulkDiscount(200, 20))
        self.assertAlmostEqual(order.calculate_total(), 230)
        order.set_discount(PercentageDiscount(10))
        self.assertAlmostEqual(order.calculate_total(), 225)
        self.assertAlmostEqual(order.calculate_subtotal(), 250)  # lines unchanged

    def test_new_strategy_works_without_changing_order(self):
        class HalfPrice(DiscountStrategy):  # brand-new rule, defined only here
            def apply(self, total: float) -> float:
                return total / 2

        self.assertAlmostEqual(order_totalling_250(HalfPrice()).calculate_total(), 125)
        self.assertAlmostEqual(order_totalling_250(StudentDiscount()).calculate_total(), 237.5)

    def test_orders_can_share_one_strategy_object(self):
        shared = PercentageDiscount(10)
        first, second = order_totalling_250(shared), order_totalling_250(shared)
        self.assertIs(first.get_discount(), second.get_discount())

    def test_order_has_no_discount_if_elif_logic(self):
        source = textwrap.dedent(inspect.getsource(Order.calculate_total))
        self.assertFalse(any(isinstance(node, ast.If) for node in ast.walk(ast.parse(source))))
        order_source = inspect.getsource(Order)
        for discount_name in ("percentage", "bulk", "student"):
            self.assertNotIn(f'"{discount_name}"', order_source.lower())


if __name__ == "__main__":
    unittest.main()
