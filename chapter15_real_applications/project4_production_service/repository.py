"""
Project 4 — Repository pattern (Ch.1, Ch.12 DIP, Ch.13). The service
layer depends on this abstraction, never on a concrete storage detail.
"""
from abc import ABC, abstractmethod
from domain import Order, OrderNotFoundError


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order) -> None: ...
    @abstractmethod
    def get(self, order_id: int) -> Order: ...
    @abstractmethod
    def update(self, order: Order) -> None: ...


class InMemoryOrderRepository(OrderRepository):
    """The 'production' implementation for this demo. A real service
    would have a SqlOrderRepository here instead -- the OrderService
    below would need ZERO changes to use it."""
    def __init__(self):
        self._orders: dict[int, Order] = {}

    def add(self, order: Order) -> None:
        self._orders[order.id] = order

    def get(self, order_id: int) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError(f"No order with id {order_id}")
        return order

    def update(self, order: Order) -> None:
        if order.id not in self._orders:
            raise OrderNotFoundError(f"No order with id {order.id}")
        self._orders[order.id] = order
