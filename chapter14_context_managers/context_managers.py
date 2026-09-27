"""
Chapter 14 — context managers from first principles: __enter__/__exit__,
contextlib.contextmanager, and real use cases (mock DB connection, real
file handling, a lock, and a mock transaction with commit/rollback).
"""
import contextlib
import os
import threading
import time


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("A hand-written context manager class")
# ---------------------------------------------------------------------------
class ManagedResource:
    def __enter__(self):
        print("  [ManagedResource] __enter__: acquiring")
        return self   # this is what `as X` binds to

    def use(self):
        print("  [ManagedResource] using the resource")

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"  [ManagedResource] __exit__: releasing (exc_type={exc_type})")
        return False   # False/None: do NOT suppress any exception

with ManagedResource() as resource:
    resource.use()

print("\nSame thing, but the body raises an exception -- __exit__ still runs:")
try:
    with ManagedResource() as resource:
        resource.use()
        raise ValueError("something went wrong inside the with-block")
except ValueError as e:
    print(f"  Exception propagated as expected AFTER cleanup ran: {e}")


# ---------------------------------------------------------------------------
section("contextlib.contextmanager: the generator-based shortcut")
# ---------------------------------------------------------------------------
@contextlib.contextmanager
def managed_resource_generator():
    print("  [gen CM] acquiring (everything before yield = __enter__)")
    try:
        yield "the resource"   # this is what `as X` binds to
    finally:
        print("  [gen CM] releasing (everything after yield, in finally = __exit__)")

with managed_resource_generator() as r:
    print(f"  using: {r}")


# ---------------------------------------------------------------------------
section("Use case 1: a mock database connection")
# ---------------------------------------------------------------------------
class MockDbConnection:
    def __enter__(self):
        print("  [DB] connection opened")
        return self

    def query(self, sql):
        print(f"  [DB] executing: {sql}")
        return "mock result"

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("  [DB] connection closed (always, even on error)")
        return False

with MockDbConnection() as db:
    db.query("SELECT * FROM tasks")


# ---------------------------------------------------------------------------
section("Use case 2: real file handling (the built-in, canonical example)")
# ---------------------------------------------------------------------------
temp_path = os.path.join(os.path.dirname(__file__), "_demo_temp.txt")
with open(temp_path, "w") as f:
    f.write("hello from a context manager")
# The file is GUARANTEED closed here, even if write() had raised.
with open(temp_path, "r") as f:
    print(f"  Read back: {f.read()!r}")
os.remove(temp_path)


# ---------------------------------------------------------------------------
section("Use case 3: a lock, using contextlib for clean acquire/release")
# ---------------------------------------------------------------------------
shared_lock = threading.Lock()

@contextlib.contextmanager
def timed_lock(lock, label):
    print(f"  [{label}] acquiring lock")
    lock.acquire()
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        lock.release()
        print(f"  [{label}] released lock after {elapsed*1000:.1f} ms")

with timed_lock(shared_lock, "critical-section"):
    print("  [critical-section] doing protected work")


# ---------------------------------------------------------------------------
section("Use case 4: a mock transaction with commit/rollback")
# ---------------------------------------------------------------------------
class MockTransaction:
    def __init__(self):
        self.committed = False

    def __enter__(self):
        print("  [Transaction] BEGIN")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print("  [Transaction] COMMIT (no exception occurred)")
            self.committed = True
        else:
            print(f"  [Transaction] ROLLBACK (due to {exc_type.__name__}: {exc_val})")
        return False   # don't suppress -- let the caller still see the error

print("Successful transaction:")
with MockTransaction() as txn:
    print("  [Transaction] doing work")
print(f"  committed = {txn.committed}")

print("\nFailed transaction (exception inside the block):")
try:
    with MockTransaction() as txn:
        print("  [Transaction] doing work")
        raise RuntimeError("simulated failure mid-transaction")
except RuntimeError:
    print(f"  committed = {txn.committed} (rolled back, exception still propagated)")


# ---------------------------------------------------------------------------
section("Nesting: __exit__ order is the REVERSE of __enter__ order")
# ---------------------------------------------------------------------------
class Named:
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        print(f"  __enter__ {self.name}")
        return self
    def __exit__(self, *args):
        print(f"  __exit__ {self.name}")
        return False

with Named("outer"), Named("inner"):
    print("  body running")
