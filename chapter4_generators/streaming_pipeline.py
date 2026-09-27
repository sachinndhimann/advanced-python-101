"""
Chapter 4 — memory comparison (list vs generator) and a chained,
lazy, streaming data-processing pipeline.
"""
import sys
import time


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


RECORD_COUNT = 2_000_000   # "10 million records" scaled down to keep the demo fast


# ---------------------------------------------------------------------------
section("Memory comparison: list vs generator")
# ---------------------------------------------------------------------------
def records_as_list(n):
    return [f"record-{i}" for i in range(n)]   # ALL n strings exist in memory at once

def records_as_generator(n):
    for i in range(n):
        yield f"record-{i}"                     # only ONE string exists at a time

start = time.perf_counter()
big_list = records_as_list(RECORD_COUNT)
list_build_time = time.perf_counter() - start
list_size = sys.getsizeof(big_list)  # size of the container itself (not the strings)
print(f"List of {RECORD_COUNT:,} records: container size = {list_size:,} bytes, "
      f"built in {list_build_time*1000:.1f} ms")
del big_list

start = time.perf_counter()
gen = records_as_generator(RECORD_COUNT)
gen_create_time = time.perf_counter() - start
gen_size = sys.getsizeof(gen)
print(f"Generator for {RECORD_COUNT:,} records: object size = {gen_size} bytes, "
      f"created in {gen_create_time*1000:.4f} ms")
print("Notice: the generator's creation cost is ~constant regardless of RECORD_COUNT,")
print("because no records are produced until you actually iterate.")


# ---------------------------------------------------------------------------
section("Processing one item at a time: generator never holds the full set")
# ---------------------------------------------------------------------------
def process_one_at_a_time(n):
    total_length = 0
    for record in records_as_generator(n):
        total_length += len(record)   # do the work, then FORGET the record
    return total_length

start = time.perf_counter()
result = process_one_at_a_time(RECORD_COUNT)
elapsed = time.perf_counter() - start
print(f"Processed {RECORD_COUNT:,} records via generator in {elapsed:.3f}s, "
      f"total_length={result:,}, peak memory stayed ~constant throughout.")


# ---------------------------------------------------------------------------
section("A streaming pipeline: chained generators, nothing materialized")
# ---------------------------------------------------------------------------
def read_lines(n):
    """Stage 1: 'read' raw records (simulating e.g. a file or DB cursor)."""
    for i in range(n):
        yield f"user_id={i},amount={(i % 10) - 5}"   # mix of negative and non-negative "amounts"

def parse_records(lines):
    """Stage 2: parse each line into a dict. Consumes `lines` lazily."""
    for line in lines:
        parts = dict(kv.split("=") for kv in line.split(","))
        parts["amount"] = int(parts["amount"])
        yield parts

def filter_valid(records):
    """Stage 3: drop invalid records (negative amounts), lazily."""
    for record in records:
        if record["amount"] >= 0:
            yield record

def enrich(records):
    """Stage 4: add a derived field, lazily."""
    for record in records:
        record["amount_doubled"] = record["amount"] * 2
        yield record

# Nothing runs yet -- this just builds a chain of lazy generators.
pipeline = enrich(filter_valid(parse_records(read_lines(10))))

print("Pipeline result (only valid, non-negative-amount records, enriched):")
for record in pipeline:
    print(f"  {record}")

print()
print("At no point did the full 10-record set exist as a materialized list --")
print("each record flows through all four stages before the next one is read.")


# ---------------------------------------------------------------------------
section("Same pipeline at scale: still constant memory")
# ---------------------------------------------------------------------------
large_pipeline = enrich(filter_valid(parse_records(read_lines(RECORD_COUNT))))
count = sum(1 for _ in large_pipeline)   # drain it without keeping any of it
print(f"Streamed {count:,} valid records through the full 4-stage pipeline "
      f"without ever holding more than one record in memory at a time.")
