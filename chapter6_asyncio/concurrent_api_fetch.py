"""
Chapter 6 — fetching from multiple "APIs" concurrently. Uses
asyncio.sleep to simulate network latency so this demo is fully
self-contained (no real network calls, no external dependencies) while
still demonstrating the real timing benefit of async I/O.
"""
import asyncio
import random
import time


# Simulated latency per "API" -- pretend these are real HTTP calls.
MOCK_APIS = {
    "users_api": 0.30,
    "orders_api": 0.20,
    "inventory_api": 0.45,
    "pricing_api": 0.15,
    "shipping_api": 0.25,
}


async def fetch_from_api(name: str, simulated_latency: float) -> dict:
    """Stands in for `await http_client.get(url)`. In real code you'd use
    aiohttp/httpx here instead of asyncio.sleep."""
    await asyncio.sleep(simulated_latency)
    return {"api": name, "status": "ok", "latency": simulated_latency}


async def fetch_all_concurrently() -> list[dict]:
    tasks = [fetch_from_api(name, latency) for name, latency in MOCK_APIS.items()]
    return await asyncio.gather(*tasks)


async def fetch_all_sequentially() -> list[dict]:
    results = []
    for name, latency in MOCK_APIS.items():
        results.append(await fetch_from_api(name, latency))
    return results


async def main():
    print("=== Sequential fetching ===")
    start = time.perf_counter()
    seq_results = await fetch_all_sequentially()
    seq_time = time.perf_counter() - start
    for r in seq_results:
        print(f"  {r['api']}: {r['latency']}s")
    print(f"Total sequential time: {seq_time:.2f}s\n")

    print("=== Concurrent fetching (asyncio.gather) ===")
    start = time.perf_counter()
    conc_results = await fetch_all_concurrently()
    conc_time = time.perf_counter() - start
    for r in conc_results:
        print(f"  {r['api']}: {r['latency']}s")
    print(f"Total concurrent time: {conc_time:.2f}s\n")

    speedup = seq_time / conc_time
    print(f"Speedup: {speedup:.1f}x")
    print(f"Sequential time ≈ sum of all latencies ({sum(MOCK_APIS.values()):.2f}s).")
    print(f"Concurrent time ≈ the SLOWEST single call ({max(MOCK_APIS.values()):.2f}s).")
    print("This is the entire value proposition of async for I/O-bound workloads:")
    print("the CPU is idle during each wait anyway, so waiting on 5 things at once")
    print("costs barely more than waiting on the slowest one alone.")


if __name__ == "__main__":
    asyncio.run(main())
