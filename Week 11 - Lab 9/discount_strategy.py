from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    
    @abstractmethod
    def apply(self, total: float) -> float:
        """Return the total after the discount has been applied."""

    def describe(self) -> str:
        """Short human-readable name of the discount, used when displaying an order."""
        return type(self).__name__


class NoDiscount(DiscountStrategy):
    """Leaves the total unchanged. The default for a new order."""

    def apply(self, total: float) -> float:
        return total

    def describe(self) -> str:
        return "No discount"

class PercentageDiscount(DiscountStrategy):

    def __init__(self, percentage: float) -> None:
        if not 0 < percentage <= 100:
            raise ValueError("Percentage must be greater than 0 and at most 100.")
        self.__percentage: float = float(percentage)

    def apply(self, total: float) -> float:
        return total * (1 - self.__percentage / 100)

    def describe(self) -> str:
        return f"{self.__percentage:g}% off"


class BulkDiscount(DiscountStrategy):
  
    def __init__(self, threshold: float, amount: float) -> None:
        if threshold < 0:
            raise ValueError("Threshold cannot be negative.")
        if amount <= 0:
            raise ValueError("Discount amount must be greater than zero.")
        self.__threshold: float = float(threshold)
        self.__amount: float = float(amount)

    def apply(self, total: float) -> float:
        if total < self.__threshold:
            return total
        return max(total - self.__amount, 0.0)

    def describe(self) -> str:
        return f"${self.__amount:.2f} off orders of ${self.__threshold:.2f} or more"
