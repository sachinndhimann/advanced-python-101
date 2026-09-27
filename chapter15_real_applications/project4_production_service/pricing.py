"""
Project 4 — Strategy pattern (Ch.12 OCP, Ch.13) for discount calculation.
"""
from abc import ABC, abstractmethod
from domain import Order


class PricingStrategy(ABC):
    @abstractmethod
    def calculate_total(self, order: Order) -> float: ...


class StandardPricing(PricingStrategy):
    def calculate_total(self, order: Order) -> float:
        return order.subtotal


class PercentageDiscountPricing(PricingStrategy):
    def __init__(self, discount_rate: float):
        self.discount_rate = discount_rate

    def calculate_total(self, order: Order) -> float:
        return order.subtotal * (1 - self.discount_rate)
