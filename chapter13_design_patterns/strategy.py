"""
Chapter 13 — Strategy Pattern.
Problem: an algorithm/behavior needs to vary at runtime without a
growing if/elif chain baked into the class that uses it.
(This is the same mechanism as Chapter 12's Open/Closed example --
Strategy IS that pattern, named explicitly.)
"""
from abc import ABC, abstractmethod


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


section("Why the naive approach fails")
class ShippingCalculatorBad:
    def calculate(self, weight_kg: float, method: str) -> float:
        if method == "standard":
            return weight_kg * 2.0
        elif method == "express":
            return weight_kg * 5.0
        elif method == "overnight":
            return weight_kg * 10.0
        raise ValueError(method)

calc_bad = ShippingCalculatorBad()
print(f"  standard: ${calc_bad.calculate(3, 'standard'):.2f}")
print("Problem: every new shipping method means editing this class again.")


section("Strategy: inject the algorithm as an object")
class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, weight_kg: float) -> float: ...

class StandardShipping(ShippingStrategy):
    def calculate(self, weight_kg): return weight_kg * 2.0

class ExpressShipping(ShippingStrategy):
    def calculate(self, weight_kg): return weight_kg * 5.0

class OvernightShipping(ShippingStrategy):
    def calculate(self, weight_kg): return weight_kg * 10.0

class ShippingCalculator:
    def __init__(self, strategy: ShippingStrategy):
        self.strategy = strategy   # the varying behavior is INJECTED

    def calculate(self, weight_kg: float) -> float:
        return self.strategy.calculate(weight_kg)

calc = ShippingCalculator(ExpressShipping())
print(f"  express: ${calc.calculate(3):.2f}")

# Swap the strategy at RUNTIME without touching ShippingCalculator:
calc.strategy = OvernightShipping()
print(f"  swapped to overnight: ${calc.calculate(3):.2f}")


section("Trade-offs")
print("One class per algorithm variant adds file/class count. Worth it")
print("when variants are genuinely swappable at runtime or independently")
print("testable; overkill for 2 fixed, never-changing branches.")

section("Real-world use")
print("Python's sort(key=...) IS strategy (you inject the comparison")
print("logic). Compression libraries picking gzip/bzip2/lzma. Payment")
print("gateways swapping Stripe/PayPal/Razorpay behind one interface.")
