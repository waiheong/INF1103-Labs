from discount_strategy import DiscountStrategy

# Takes 5% off for students
class StudentDiscount(DiscountStrategy):
    RATE: float = 5.0  # valuye in %

    def apply(self, total: float) -> float:
        return total * (1 - self.RATE / 100)

    def describe(self) -> str:
        return f"Student discount ({self.RATE:g}% off)"
