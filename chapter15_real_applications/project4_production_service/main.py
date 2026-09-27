"""
Project 4 — wires everything together via Dependency Injection and runs
an end-to-end demo (Ch.6 asyncio entry point).
"""
import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))   # allow running as a script

from domain import OrderItem
from repository import InMemoryOrderRepository
from pricing import PercentageDiscountPricing
from notifications import AsyncEmailNotifier
from service import OrderService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


async def main():
    # All wiring happens HERE, in one place -- OrderService itself never
    # constructs any of its dependencies (Ch.1/12/13 Dependency Inversion).
    repo = InMemoryOrderRepository()
    pricing = PercentageDiscountPricing(discount_rate=0.1)
    notifier = AsyncEmailNotifier()
    service = OrderService(repository=repo, pricing=pricing, notifier=notifier)

    order = service.create_order(
        order_id=1,
        customer_email="sachin@example.com",
        items=[
            OrderItem(sku="SKU-1", quantity=2, unit_price=25.0),
            OrderItem(sku="SKU-2", quantity=1, unit_price=50.0),
        ],
    )
    print(f"Created order #{order.id}, subtotal=${order.subtotal:.2f}")

    total = await service.finalize_order(order.id)
    print(f"Finalized order #{order.id}, total after discount=${total:.2f}")

    print("\n--- Demonstrating a notification failure doesn't lose the order ---")
    order2 = service.create_order(
        order_id=2,
        customer_email="not-a-valid-email",   # will fail AsyncEmailNotifier's check
        items=[OrderItem(sku="SKU-3", quantity=1, unit_price=10.0)],
    )
    total2 = await service.finalize_order(order2.id)
    saved_order2 = repo.get(order2.id)
    print(f"Order #{order2.id} status after failed notification: '{saved_order2.status}' "
          f"(still finalized, total=${total2:.2f})")


if __name__ == "__main__":
    asyncio.run(main())
