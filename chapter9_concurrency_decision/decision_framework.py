"""
Chapter 9 — an executable concurrency decision framework, applied to
eight realistic scenarios.
"""
from dataclasses import dataclass


@dataclass
class Workload:
    description: str
    io_bound: bool
    concurrent_unit_count: int   # rough number of independent units of work
    is_simple_or_oneoff: bool = False


def recommend_approach(w: Workload) -> str:
    """A direct executable version of the Chapter 9 decision tree."""
    if w.is_simple_or_oneoff and w.concurrent_unit_count <= 1:
        return "Sequential — trivial workload, concurrency overhead isn't worth it"

    if w.io_bound:
        if w.concurrent_unit_count >= 20:
            return "AsyncIO — many concurrent I/O waits, lowest per-unit overhead"
        else:
            return "Threads (or AsyncIO) — a handful of I/O waits, either works fine"
    else:
        # CPU-bound
        if w.concurrent_unit_count <= 1:
            return "Sequential — CPU-bound but nothing to parallelize"
        return "Processes — CPU-bound and parallelizable; only real speedup option"


SCENARIOS = [
    Workload(
        "1. Downloading 500 product images from a CDN before generating a report",
        io_bound=True, concurrent_unit_count=500,
    ),
    Workload(
        "2. Resizing 500 already-downloaded images to thumbnails",
        io_bound=False, concurrent_unit_count=500,
    ),
    Workload(
        "3. A CLI tool that reads one config file and prints a summary",
        io_bound=True, concurrent_unit_count=1, is_simple_or_oneoff=True,
    ),
    Workload(
        "4. A web scraper hitting 50 different news sites once each",
        io_bound=True, concurrent_unit_count=50,
    ),
    Workload(
        "5. Computing SHA-256 hashes of 10,000 large video files on disk",
        io_bound=False, concurrent_unit_count=10_000,
        # Note: hashing is CPU-bound once the file is in memory; the disk
        # READ portion is I/O-bound. In practice this is often a hybrid:
        # threads to read concurrently, processes to hash concurrently.
        # Treated here as CPU-bound because hashing dominates for large files.
    ),
    Workload(
        "6. A chat server handling 5,000 simultaneous open WebSocket connections",
        io_bound=True, concurrent_unit_count=5000,
    ),
    Workload(
        "7. A script that calls one external API once, waits, and exits",
        io_bound=True, concurrent_unit_count=1, is_simple_or_oneoff=True,
    ),
    Workload(
        "8. Running inference for 8 independent ML model instances, each pinned to one CPU core",
        io_bound=False, concurrent_unit_count=8,
    ),
]


if __name__ == "__main__":
    print("=== Concurrency recommendations for 8 realistic scenarios ===\n")
    for scenario in SCENARIOS:
        recommendation = recommend_approach(scenario)
        print(f"{scenario.description}")
        print(f"   -> {recommendation}\n")

    print("=== Try your own ===")
    print("Add a Workload(...) for a real scenario from your own work and")
    print("call recommend_approach(...) on it to check your reasoning.")

    example = Workload(
        "Example: fetching document templates from 3 microservices before rendering a document",
        io_bound=True, concurrent_unit_count=3,
    )
    print(f"\n{example.description}\n   -> {recommend_approach(example)}")
