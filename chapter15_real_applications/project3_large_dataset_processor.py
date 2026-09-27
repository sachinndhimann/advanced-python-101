"""
Chapter 15, Project 3 — Large Dataset Processor.

Combines: Iterators (Ch.3), generators (Ch.4), multiprocessing (Ch.8),
streaming. Contrasts naive load-everything-first against a streaming +
process-pool approach.
"""
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

RECORD_COUNT = 500_000


# --- The "dataset": a generator, so it's never all in memory at once -----
def stream_dataset(n: int):
    """Simulates streaming records from a large source (a file, a DB
    cursor, an API paginator) -- one record exists at a time."""
    for i in range(n):
        yield i


def cpu_heavy_transform(n: int) -> int:
    """A deliberately CPU-bound 'transformation' (e.g. a hash, a scoring
    model, a validation rule) -- not I/O, so multiprocessing (not
    threads/asyncio) is the right tool, per Chapter 9's framework."""
    total = 0
    for i in range(50):
        total += (n * i) % 97
    return total


# --- Naive approach: materialize everything first -------------------------
def naive_process(n: int) -> int:
    all_records = list(stream_dataset(n))          # ALL n records in memory at once
    results = [cpu_heavy_transform(r) for r in all_records]
    return sum(results)


# --- Streaming + process pool: never materialize the full dataset ---------
def streaming_process(n: int, chunk_size: int = 50_000, map_chunksize: int = 500) -> int:
    """Reads records lazily and submits them to a process pool in large
    batches, so peak memory stays bounded regardless of how large `n`
    gets. `map_chunksize` batches multiple items per IPC message --
    without it, sending one item at a time makes serialization overhead
    dominate for cheap per-item work like this, which is itself a real,
    important lesson (see Chapter 8's 'when NOT to use multiprocessing')."""
    total = 0
    with ProcessPoolExecutor(max_workers=max(2, os.cpu_count() or 2)) as pool:
        chunk: list[int] = []
        for record in stream_dataset(n):     # never holds more than one chunk
            chunk.append(record)
            if len(chunk) >= chunk_size:
                total += sum(pool.map(cpu_heavy_transform, chunk, chunksize=map_chunksize))
                chunk = []
        if chunk:
            total += sum(pool.map(cpu_heavy_transform, chunk, chunksize=map_chunksize))
    return total


if __name__ == "__main__":
    print(f"Processing {RECORD_COUNT:,} records\n")

    print("=== Naive: load everything into a list first ===")
    start = time.perf_counter()
    naive_result = naive_process(RECORD_COUNT)
    naive_time = time.perf_counter() - start
    print(f"Result: {naive_result}, time: {naive_time:.2f}s "
          f"(peak memory held ALL {RECORD_COUNT:,} records + results at once)\n")

    print("=== Streaming + process pool ===")
    start = time.perf_counter()
    streaming_result = streaming_process(RECORD_COUNT)
    streaming_time = time.perf_counter() - start
    print(f"Result: {streaming_result}, time: {streaming_time:.2f}s "
          f"(peak memory bounded by ONE chunk at a time)\n")

    assert naive_result == streaming_result, "Both approaches must agree on the answer!"
    print(f"Results match: {naive_result == streaming_result}")
    print(f"\nOn a multi-core machine, streaming_process also benefits from real")
    print(f"parallelism (Ch.8) on top of its constant-memory advantage; on this")
    print(f"sandbox's {os.cpu_count()}-core environment, the memory benefit is the")
    print(f"main story since there's no second core to parallelize across.")
    print(f"\nNote: map_chunksize=500 above is doing real work -- try setting it to 1")
    print(f"and rerun: per-item IPC overhead dominates the (cheap) per-record compute,")
    print(f"making the 'streaming' version dramatically SLOWER than naive. This is")
    print(f"Chapter 8's 'multiprocessing can be worse for small workloads' lesson,")
    print(f"made concrete on a real dataset instead of a toy example.")
