"""
Project 4 — domain models and exceptions. Ch.1 dataclasses, Ch.5
exception hierarchy.
"""
from dataclasses import dataclass, field


@dataclass
class OrderItem:
    sku: str
    quantity: int
    unit_price: float


@dataclass
class Order:
    id: int
    customer_email: str
    items: list[OrderItem] = field(default_factory=list)
    status: str = "pending"

    @property
    def subtotal(self) -> float:
        return sum(item.quantity * item.unit_price for item in self.items)


class ServiceError(Exception):
    """Base for every error this service raises on purpose."""

class OrderNotFoundError(ServiceError):
    pass

class InvalidOrderError(ServiceError):
    pass

class NotificationFailedError(ServiceError):
    """Retryable: a notification failing shouldn't fail the whole order."""
