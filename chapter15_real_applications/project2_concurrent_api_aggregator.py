"""
Chapter 15, Project 2 — Concurrent API Data Aggregator.

Combines: AsyncIO (Ch.6), error handling (Ch.5), logging (Ch.10), type
hints (Ch.11). Fetches from several mock APIs concurrently, tolerates
partial failure, and produces one combined report.
"""
import asyncio
import logging
import random
import time
from dataclasses import dataclass
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("aggregator")


@dataclass
class ApiResult:
    source: str
    data: Optional[dict]
    error: Optional[str]


class ApiError(Exception):
    """Domain error for a failed upstream call, distinct from bugs in our own code."""


# --- Mock "APIs": some succeed, one is deliberately made to fail ---------
async def fetch_users_api() -> dict:
    await asyncio.sleep(0.15)
    return {"users": 42}

async def fetch_orders_api() -> dict:
    await asyncio.sleep(0.10)
    return {"orders": 128}

async def fetch_inventory_api() -> dict:
    await asyncio.sleep(0.20)
    raise ApiError("inventory service returned 503")   # deliberately failing

async def fetch_pricing_api() -> dict:
    await asyncio.sleep(0.05)
    return {"avg_price": 24.99}


API_SOURCES = {
    "users": fetch_users_api,
    "orders": fetch_orders_api,
    "inventory": fetch_inventory_api,
    "pricing": fetch_pricing_api,
}


async def fetch_with_error_handling(name: str, fetch_fn) -> ApiResult:
    """Wraps each fetch so ONE failure doesn't take down the whole gather()."""
    try:
        data = await fetch_fn()
        logger.info(f"{name}: succeeded")
        return ApiResult(source=name, data=data, error=None)
    except ApiError as e:
        logger.error(f"{name}: failed - {e}")
        return ApiResult(source=name, data=None, error=str(e))


async def aggregate_concurrently() -> list[ApiResult]:
    tasks = [fetch_with_error_handling(name, fn) for name, fn in API_SOURCES.items()]
    return await asyncio.gather(*tasks)   # gather here never raises: each
                                          # coroutine catches its own error


async def aggregate_sequentially() -> list[ApiResult]:
    results = []
    for name, fn in API_SOURCES.items():
        results.append(await fetch_with_error_handling(name, fn))
    return results


def build_report(results: list[ApiResult]) -> str:
    lines = ["=== Aggregation Report ==="]
    succeeded = [r for r in results if r.error is None]
    failed = [r for r in results if r.error is not None]
    for r in succeeded:
        lines.append(f"  OK   {r.source}: {r.data}")
    for r in failed:
        lines.append(f"  FAIL {r.source}: {r.error}")
    lines.append(f"Summary: {len(succeeded)} succeeded, {len(failed)} failed "
                 f"out of {len(results)} sources.")
    return "\n".join(lines)


async def main():
    print("--- Sequential aggregation ---")
    start = time.perf_counter()
    seq_results = await aggregate_sequentially()
    seq_time = time.perf_counter() - start
    print(f"Sequential time: {seq_time:.2f}s\n")

    print("--- Concurrent aggregation ---")
    start = time.perf_counter()
    conc_results = await aggregate_concurrently()
    conc_time = time.perf_counter() - start
    print(f"Concurrent time: {conc_time:.2f}s\n")

    print(build_report(conc_results))
    print(f"\nSpeedup: {seq_time/conc_time:.1f}x -- and note the partial failure")
    print("(inventory) did NOT prevent the other 3 sources from succeeding.")


if __name__ == "__main__":
    asyncio.run(main())
