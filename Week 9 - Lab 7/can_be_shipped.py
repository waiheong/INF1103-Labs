from abc import ABC, abstractmethod

# returning cost of shipping for the items.
class CanBeShipped(ABC):
    @abstractmethod
    def calculate_shipping_cost(self):
        pass
