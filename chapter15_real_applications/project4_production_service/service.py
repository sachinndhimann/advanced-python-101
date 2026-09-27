"""
Project 4 — OrderService: the high-level policy class. Depends only on
abstractions (Repository, PricingStrategy, Notifier), all injected via
the constructor (Ch.1/12/13 DI). Uses a context manager for a mock
transaction (Ch.14) and proper exception handling (Ch.5).
"""
import contextlib
import logging

from domain import Order, OrderItem, InvalidOrderError, NotificationFailedError
from repository import OrderRepository
from pricing import PricingStrategy
from notifications import Notifier

logger = logging.getLogger("order_service")


@contextlib.contextmanager
def order_transaction(order_id: int):
    """A mock transaction boundary (Ch.14 context manager). A real
    version would BEGIN/COMMIT/ROLLBACK against a real database."""
    logger.info(f"BEGIN transaction for order {order_id}")
    try:
        yield
        logger.info(f"COMMIT transaction for order {order_id}")
    except Exception:
        logger.error(f"ROLLBACK transaction for order {order_id}")
        raise


class OrderService:
    def __init__(self, repository: OrderRepository, pricing: PricingStrategy, notifier: Notifier):
        self._repo = repository
        self._pricing = pricing
        self._notifier = notifier

    def create_order(self, order_id: int, customer_email: str, items: list[OrderItem]) -> Order:
        if not items:
            raise InvalidOrderError("An order must have at least one item")
        order = Order(id=order_id, customer_email=customer_email, items=items)
        self._repo.add(order)
        logger.info(f"Order {order.id} created for {customer_email}")
        return order

    async def finalize_order(self, order_id: int) -> float:
        """Calculates the final total and notifies the customer. If
        notification fails, the order is still finalized (retryable
        failure, Ch.5) -- we log it rather than losing the whole order."""
        order = self._repo.get(order_id)
        with order_transaction(order.id):
            total = self._pricing.calculate_total(order)
            order.status = "finalized"
            self._repo.update(order)

        try:
            await self._notifier.notify(
                order.customer_email,
                f"Your order #{order.id} is confirmed. Total: ${total:.2f}",
            )
        except NotificationFailedError as e:
            logger.warning(f"Notification failed for order {order.id}, "
                           f"but the order itself is still finalized: {e}")

        return total
