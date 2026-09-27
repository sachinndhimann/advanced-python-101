"""
Chapter 6 — asyncio fundamentals: coroutines, await, the event loop,
tasks, gather, async context managers, async generators.
"""
import asyncio
import time


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
async def demo_basic_coroutine():
    section("A basic coroutine")
    async def say_hello():
        print("  starting say_hello")
        await asyncio.sleep(0.1)   # simulates an I/O wait -- yields control
        print("  finished say_hello")
        return "hello"

    coro = say_hello()
    print(f"  Calling say_hello() returns a coroutine object, not a result: {coro}")
    result = await coro          # NOW it actually runs
    print(f"  Awaited result: {result}")


# ---------------------------------------------------------------------------
async def demo_sequential_vs_concurrent():
    section("Sequential awaiting vs concurrent tasks")

    async def fetch(name, delay):
        await asyncio.sleep(delay)
        return f"{name} done"

    # Sequential: each await fully completes before the next starts.
    start = time.perf_counter()
    r1 = await fetch("A", 0.2)
    r2 = await fetch("B", 0.2)
    sequential_time = time.perf_counter() - start
    print(f"  Sequential: {r1}, {r2} -- took {sequential_time:.2f}s (≈ sum of delays)")

    # Concurrent: both scheduled as Tasks, run interleaved on one thread.
    start = time.perf_counter()
    task_a = asyncio.create_task(fetch("A", 0.2))
    task_b = asyncio.create_task(fetch("B", 0.2))
    r1, r2 = await task_a, await task_b
    concurrent_time = time.perf_counter() - start
    print(f"  Concurrent: {r1}, {r2} -- took {concurrent_time:.2f}s (≈ max of delays)")


# ---------------------------------------------------------------------------
async def demo_gather():
    section("asyncio.gather(): run many, collect all results at once")

    async def fetch(name, delay):
        await asyncio.sleep(delay)
        return f"{name}:{delay}s"

    start = time.perf_counter()
    results = await asyncio.gather(
        fetch("api_a", 0.15),
        fetch("api_b", 0.10),
        fetch("api_c", 0.20),
    )
    elapsed = time.perf_counter() - start
    print(f"  gather() results: {results}")
    print(f"  Total time: {elapsed:.2f}s (bounded by the SLOWEST call, ~0.20s, not the sum ~0.45s)")


# ---------------------------------------------------------------------------
async def demo_async_context_manager():
    section("Async context managers: __aenter__ / __aexit__")

    class AsyncResource:
        async def __aenter__(self):
            print("  [async CM] acquiring resource (simulated async setup)")
            await asyncio.sleep(0.05)
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            print("  [async CM] releasing resource (simulated async teardown)")
            await asyncio.sleep(0.05)

        async def use(self):
            print("  [async CM] using the resource")

    async with AsyncResource() as resource:
        await resource.use()


# ---------------------------------------------------------------------------
async def demo_async_generator():
    section("Async generators: async def + yield")

    async def stream_events(n):
        for i in range(n):
            await asyncio.sleep(0.02)   # simulate waiting for the next event
            yield f"event-{i}"

    async for event in stream_events(3):
        print(f"  received {event}")


# ---------------------------------------------------------------------------
async def demo_unawaited_coroutine_warning():
    section("Common bug: forgetting to await a coroutine")

    async def fetch_data():
        await asyncio.sleep(0.01)
        return "data"

    result = fetch_data()   # BUG: missing `await` -- this is a coroutine object, not a result
    print(f"  Forgot to await: result is {result!r} (a coroutine, NOT the string 'data')")
    # Cleaning it up properly to avoid a real 'was never awaited' warning past this demo:
    await result


async def main():
    await demo_basic_coroutine()
    await demo_sequential_vs_concurrent()
    await demo_gather()
    await demo_async_context_manager()
    await demo_async_generator()
    await demo_unawaited_coroutine_warning()


if __name__ == "__main__":
    asyncio.run(main())
