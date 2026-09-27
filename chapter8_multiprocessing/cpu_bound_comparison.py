"""
Chapter 8 — multiprocessing for genuine CPU parallelism. Compares a
CPU-bound workload run sequentially, via ThreadPoolExecutor (to show
threads do NOT help here), and via ProcessPoolExecutor (which does).
"""
import os
import time
import pickle
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


def count_primes(start: int, end: int) -> int:
    """A genuinely CPU-bound function: no I/O, no sleeping, pure computation."""
    count = 0
    for n in range(max(start, 2), end):
        is_prime = True
        for d in range(2, int(n ** 0.5) + 1):
            if n % d == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
    return count


def run_and_time(label, fn):
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    print(f"  {label}: {elapsed:.2f}s, result={result}")
    return elapsed


if __name__ == "__main__":
    N = 200_000
    # Use at least 4 chunks even on a 1-core machine, so the demo still
    # shows PROCESSES BEING CREATED and work being distributed. The actual
    # SPEEDUP you see depends entirely on how many physical cores are
    # available -- on a 1-core sandbox/CI machine, expect near-zero
    # speedup (all chunks still execute one at a time, just in different
    # processes); on a real 4-8 core laptop, expect a real multi-x speedup.
    NUM_CHUNKS = max(4, os.cpu_count() or 4)
    chunk_size = N // NUM_CHUNKS
    chunks = [(i * chunk_size, (i + 1) * chunk_size) for i in range(NUM_CHUNKS)]

    print(f"Counting primes up to {N:,}, using {NUM_CHUNKS} chunks (cpu_count={os.cpu_count()})")
    if (os.cpu_count() or 1) < 2:
        print("NOTE: this machine reports only 1 CPU core, so ProcessPoolExecutor")
        print("      below will show little/no speedup here -- on a multi-core")
        print("      machine it will show a real, multi-x speedup instead.")

    # ---------------------------------------------------------------------
    section("1. Sequential (single process, single thread)")
    # ---------------------------------------------------------------------
    seq_time = run_and_time(
        "Sequential",
        lambda: sum(count_primes(s, e) for s, e in chunks),
    )

    # ---------------------------------------------------------------------
    section("2. ThreadPoolExecutor (CPU-bound work -- expect little/no speedup)")
    # ---------------------------------------------------------------------
    def run_threaded():
        with ThreadPoolExecutor(max_workers=NUM_CHUNKS) as pool:
            results = list(pool.map(lambda args: count_primes(*args), chunks))
        return sum(results)

    thread_time = run_and_time("ThreadPoolExecutor", run_threaded)

    # ---------------------------------------------------------------------
    section("3. ProcessPoolExecutor (true parallelism -- expect real speedup)")
    # ---------------------------------------------------------------------
    def run_multiprocess():
        with ProcessPoolExecutor(max_workers=NUM_CHUNKS) as pool:
            results = list(pool.map(count_primes_star, chunks))
        return sum(results)

    # ProcessPoolExecutor.map needs a plain top-level function (must be
    # picklable) -- a lambda won't survive being sent to a worker process.
    def count_primes_star(args):
        return count_primes(*args)

    process_time = run_and_time("ProcessPoolExecutor", run_multiprocess)

    # ---------------------------------------------------------------------
    section("Summary")
    # ---------------------------------------------------------------------
    print(f"  Sequential:            {seq_time:.2f}s  (baseline)")
    print(f"  Threads (CPU-bound):   {thread_time:.2f}s  (speedup: {seq_time/thread_time:.2f}x -- GIL blocks real parallelism)")
    print(f"  Processes (CPU-bound): {process_time:.2f}s  (speedup: {seq_time/process_time:.2f}x -- real parallel cores)")

    # ---------------------------------------------------------------------
    section("Pickling: what CAN and CANNOT cross a process boundary")
    # ---------------------------------------------------------------------
    picklable_data = {"a": 1, "b": [1, 2, 3]}
    print(f"  A dict pickles fine: {pickle.dumps(picklable_data)[:20]}...")

    unpicklable = lambda x: x * 2   # noqa: E731 -- intentional demo of the gotcha
    try:
        pickle.dumps(unpicklable)
    except (pickle.PicklingError, AttributeError) as e:
        print(f"  A lambda FAILS to pickle: {type(e).__name__}: {e}")
        print("  This is why ProcessPoolExecutor.map(lambda ...) breaks in real code --")
        print("  always pass a top-level, importable function to worker processes.")
