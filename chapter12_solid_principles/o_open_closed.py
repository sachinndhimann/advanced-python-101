"""
Chapter 12 — Open/Closed Principle.
Open for extension, closed for modification.
"""
from abc import ABC, abstractmethod


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("BAD: adding a new case means editing existing, tested code")
# ---------------------------------------------------------------------------
def calculate_discount_bad(order_total: float, discount_type: str) -> float:
    if discount_type == "percentage":
        return order_total * 0.9
    elif discount_type == "flat":
        return order_total - 10
    # Adding "loyalty_tier" here means editing THIS function again --
    # risking a typo breaking "percentage" or "flat", which already work.
    else:
        raise ValueError(f"Unknown discount type: {discount_type}")

print(f"percentage: {calculate_discount_bad(100, 'percentage')}")
print(f"flat: {calculate_discount_bad(100, 'flat')}")
print("Problem: every new discount type means editing this SAME function,")
print("risking regressions in the branches that already work.")


# ---------------------------------------------------------------------------
section("GOOD: new discount types are ADDED, not edited in")
# ---------------------------------------------------------------------------
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, order_total: float) -> float: ...

class PercentageDiscount(DiscountStrategy):
    def __init__(self, rate: float):
        self.rate = rate
    def apply(self, order_total: float) -> float:
        return order_total * (1 - self.rate)

class FlatDiscount(DiscountStrategy):
    def __init__(self, amount: float):
        self.amount = amount
    def apply(self, order_total: float) -> float:
        return order_total - self.amount

def calculate_discount_good(order_total: float, strategy: DiscountStrategy) -> float:
    return strategy.apply(order_total)   # never changes, regardless of new strategies

print(f"percentage: {calculate_discount_good(100, PercentageDiscount(0.1))}")
print(f"flat: {calculate_discount_good(100, FlatDiscount(10))}")

# Adding a new discount type: a NEW class, zero changes to existing code.
class LoyaltyTierDiscount(DiscountStrategy):
    def __init__(self, tier: str):
        self.tier = tier
    def apply(self, order_total: float) -> float:
        rates = {"gold": 0.2, "silver": 0.1, "bronze": 0.05}
        return order_total * (1 - rates.get(self.tier, 0))

print(f"loyalty (gold): {calculate_discount_good(100, LoyaltyTierDiscount('gold'))}")
print("\nNotice: calculate_discount_good() and every existing Strategy class")
print("were NEVER touched to add loyalty tiers -- purely additive.")


# ---------------------------------------------------------------------------
section("When NOT to over-apply this")
# ---------------------------------------------------------------------------
print("If you're CERTAIN there will only ever be exactly 2 discount types")
print("(e.g. a fixed regulatory requirement), an if/elif is simpler and")
print("the strategy-class ceremony is unneeded abstraction for a case that")
print("will never actually need extending.")
