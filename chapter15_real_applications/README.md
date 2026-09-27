# Chapter 15 — Real Applications

Four progressively harder applications combining everything from
Chapters 1-14. Each is a standalone, runnable file (or small package).

## Project 1 — CLI Task Manager
**File:** `project1_cli_task_manager.py`
**Uses:** OOP (Ch.1), type hints (Ch.11), exceptions (Ch.5), logging
(Ch.10), dataclasses (Ch.1).
A command-line task manager with add/list/complete/delete, persisted to
a JSON file, with proper error handling and logging instead of bare
prints for anything that isn't direct user-facing output.

```bash
python3 project1_cli_task_manager.py add "Write chapter 15 docs"
python3 project1_cli_task_manager.py list
python3 project1_cli_task_manager.py complete 1
python3 project1_cli_task_manager.py delete 1
```

## Project 2 — Concurrent API Data Aggregator
**File:** `project2_concurrent_api_aggregator.py`
**Uses:** AsyncIO (Ch.6), error handling (Ch.5), logging (Ch.10), type
hints (Ch.11).
Fetches from several mock "APIs" concurrently, handles partial failures
(one API failing doesn't kill the whole aggregation), and produces one
combined report. Timed against a sequential baseline.

```bash
python3 project2_concurrent_api_aggregator.py
```

## Project 3 — Large Dataset Processor
**File:** `project3_large_dataset_processor.py`
**Uses:** Iterators (Ch.3), generators (Ch.4), multiprocessing (Ch.8),
streaming.
Streams a large synthetic dataset (never loading it all into memory),
applies a CPU-heavy transformation using a process pool, and reports
throughput — directly contrasting against a naive load-everything-first
approach.

```bash
python3 project3_large_dataset_processor.py
```

## Project 4 — Production-Style Python Service
**Directory:** `project4_production_service/`
**Uses:** OOP + SOLID (Ch.1,12), design patterns (Ch.13: Repository,
Strategy, DI), logging (Ch.10), AsyncIO (Ch.6), type hints (Ch.11),
exception handling (Ch.5), context managers (Ch.14), and a small test
suite (`unittest`, no external dependencies) demonstrating that
Dependency Injection makes this genuinely testable without a real
database or network.

```bash
python3 project4_production_service/main.py
python3 -m unittest project4_production_service/tests.py -v
```

## Run everything

```bash
python3 project1_cli_task_manager.py list
python3 project2_concurrent_api_aggregator.py
python3 project3_large_dataset_processor.py
python3 project4_production_service/main.py
python3 -m unittest discover -s project4_production_service -v
```

## Experiment

1. In Project 1, add a `priority` field to `Task` (a dataclass) and a
   `--priority` CLI flag, then sort `list` output by priority.
2. In Project 2, make one mock API always fail and confirm the
   aggregator still returns partial results for the others instead of
   crashing entirely — then check the log for exactly how the failure
   was recorded.
3. In Project 3, profile the naive (load-everything) path memory usage
   vs the streaming path on a much larger synthetic dataset size.
4. In Project 4, write ONE more test in `tests.py` using a different
   fake repository than the one provided, to feel directly how DI
   (Ch.1/12/13) is what makes this testable without a real database.
