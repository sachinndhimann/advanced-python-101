"""
Project 4 — a small unittest suite. Notice NONE of these tests touch a
real database or real network -- entirely because OrderService depends
on ABSTRACTIONS (Ch.12 DIP) that are injected (Ch.1/13 DI), so fakes
slot in with zero changes to OrderService itself.
"""
import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from domain import OrderItem, InvalidOrderError, OrderNotFoundError
from repository import InMemoryOrderRepository
from pricing import StandardPricing, PercentageDiscountPricing
from notifications import RecordingFakeNotifier
from service import OrderService


class TestOrderService(unittest.TestCase):
    def setUp(self):
        # Fresh fakes for every test -- no shared state, no real I/O.
        self.repo = InMemoryOrderRepository()
        self.notifier = RecordingFakeNotifier()
        self.service = OrderService(
            repository=self.repo,
            pricing=StandardPricing(),
            notifier=self.notifier,
        )

    def test_create_order_requires_items(self):
        with self.assertRaises(InvalidOrderError):
            self.service.create_order(1, "a@example.com", items=[])

    def test_create_order_success(self):
        order = self.service.create_order(
            1, "a@example.com", [OrderItem("SKU-1", 2, 10.0)]
        )
        self.assertEqual(order.subtotal, 20.0)
        self.assertEqual(self.repo.get(1).id, 1)

    def test_finalize_order_applies_pricing_strategy(self):
        service = OrderService(
            repository=self.repo,
            pricing=PercentageDiscountPricing(0.5),   # 50% off, injected directly
            notifier=self.notifier,
        )
        service.create_order(1, "a@example.com", [OrderItem("SKU-1", 1, 100.0)])
        total = asyncio.run(service.finalize_order(1))
        self.assertEqual(total, 50.0)

    def test_finalize_order_notifies_customer(self):
        self.service.create_order(1, "a@example.com", [OrderItem("SKU-1", 1, 10.0)])
        asyncio.run(self.service.finalize_order(1))
        self.assertEqual(len(self.notifier.sent), 1)
        self.assertEqual(self.notifier.sent[0][0], "a@example.com")

    def test_finalize_nonexistent_order_raises(self):
        with self.assertRaises(OrderNotFoundError):
            asyncio.run(self.service.finalize_order(999))

    def test_finalize_survives_notification_failure(self):
        self.service.create_order(1, "not-a-valid-email", [OrderItem("SKU-1", 1, 10.0)])
        # Even with a notifier that WOULD fail on this email in production,
        # RecordingFakeNotifier never raises -- so instead we verify the
        # REAL failure-tolerance behavior at the service level using the
        # real AsyncEmailNotifier, injected just for this one test.
        from notifications import AsyncEmailNotifier
        service = OrderService(
            repository=self.repo,
            pricing=StandardPricing(),
            notifier=AsyncEmailNotifier(),
        )
        total = asyncio.run(service.finalize_order(1))   # should NOT raise
        self.assertEqual(total, 10.0)
        self.assertEqual(self.repo.get(1).status, "finalized")


if __name__ == "__main__":
    unittest.main()
