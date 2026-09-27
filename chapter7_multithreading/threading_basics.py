"""
Chapter 7 — threading fundamentals: thread lifecycle, Lock (and a real
race condition), Event, Semaphore, Queue-based producer/consumer, and
ThreadPoolExecutor on an I/O-bound workload.
"""
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("Thread lifecycle: create, start, join")
# ---------------------------------------------------------------------------
def worker(name, delay):
    print(f"  [{name}] starting")
    time.sleep(delay)
    print(f"  [{name}] finished")

t = threading.Thread(target=worker, args=("worker-1", 0.1))
print(f"  Main thread: {threading.current_thread().name}")
t.start()          # begins running concurrently with main
print("  Main thread continues immediately, doesn't wait for t yet")
t.join()            # NOW block until t finishes
print("  Main thread resumes after join()")


# ---------------------------------------------------------------------------
section("Race condition WITHOUT a lock")
# ---------------------------------------------------------------------------
counter_unsafe = 0

def increment_unsafe(n):
    global counter_unsafe
    for _ in range(n):
        # This is NOT atomic: read counter, add 1, write counter --
        # another thread can interleave between the read and write.
        counter_unsafe += 1

threads = [threading.Thread(target=increment_unsafe, args=(100_000,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

expected = 4 * 100_000
print(f"  Expected: {expected}, Actual: {counter_unsafe} "
      f"{'(CORRECT this run, but not guaranteed!)' if counter_unsafe == expected else '(WRONG -- race condition!)'}")


# ---------------------------------------------------------------------------
section("Fixed WITH a Lock")
# ---------------------------------------------------------------------------
counter_safe = 0
lock = threading.Lock()

def increment_safe(n):
    global counter_safe
    for _ in range(n):
        with lock:                 # only one thread at a time past this point
            counter_safe += 1

threads = [threading.Thread(target=increment_safe, args=(100_000,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"  Expected: {expected}, Actual: {counter_safe} (always correct with the lock)")


# ---------------------------------------------------------------------------
section("Event: one thread signals, others wait")
# ---------------------------------------------------------------------------
ready_event = threading.Event()

def waiter(name):
    print(f"  [{name}] waiting for the event...")
    ready_event.wait()   # blocks until set() is called
    print(f"  [{name}] event received, proceeding")

waiters = [threading.Thread(target=waiter, args=(f"waiter-{i}",)) for i in range(2)]
for w in waiters:
    w.start()
time.sleep(0.1)
print("  [main] setting the event now")
ready_event.set()
for w in waiters:
    w.join()


# ---------------------------------------------------------------------------
section("Semaphore: limit concurrent access to N")
# ---------------------------------------------------------------------------
semaphore = threading.Semaphore(2)   # only 2 threads allowed in at once
active_count = []

def limited_task(name):
    with semaphore:
        active_count.append(name)
        print(f"  [{name}] entered (active: {list(active_count)})")
        time.sleep(0.05)
        active_count.remove(name)

sem_threads = [threading.Thread(target=limited_task, args=(f"task-{i}",)) for i in range(5)]
for t in sem_threads:
    t.start()
for t in sem_threads:
    t.join()
print("  (never more than 2 tasks were 'active' at once)")


# ---------------------------------------------------------------------------
section("Queue: thread-safe producer/consumer, no manual locking needed")
# ---------------------------------------------------------------------------
work_queue = queue.Queue()
results = []
results_lock = threading.Lock()

def producer():
    for i in range(5):
        work_queue.put(f"item-{i}")
    work_queue.put(None)   # sentinel: signals "no more work"

def consumer():
    while True:
        item = work_queue.get()
        if item is None:
            work_queue.put(None)   # let any OTHER consumers see the sentinel too
            break
        with results_lock:
            results.append(item.upper())

prod = threading.Thread(target=producer)
cons = threading.Thread(target=consumer)
prod.start()
cons.start()
prod.join()
cons.join()
print(f"  Consumed and processed: {results}")


# ---------------------------------------------------------------------------
section("ThreadPoolExecutor on an I/O-bound workload")
# ---------------------------------------------------------------------------
def fetch_mock_url(name, latency):
    time.sleep(latency)   # simulates network I/O -- GIL is released during this
    return f"{name} fetched in {latency}s"

urls = [("api_a", 0.2), ("api_b", 0.15), ("api_c", 0.25), ("api_d", 0.1)]

start = time.perf_counter()
sequential_results = [fetch_mock_url(name, latency) for name, latency in urls]
sequential_time = time.perf_counter() - start
print(f"  Sequential: {sequential_time:.2f}s")

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=4) as pool:
    futures = [pool.submit(fetch_mock_url, name, latency) for name, latency in urls]
    threaded_results = [f.result() for f in futures]
threaded_time = time.perf_counter() - start
print(f"  ThreadPoolExecutor(max_workers=4): {threaded_time:.2f}s")
print(f"  Speedup: {sequential_time / threaded_time:.1f}x "
      "(I/O-bound work benefits from threads DESPITE the GIL,")
print("  because the GIL is released during each sleep/I/O wait.)")
