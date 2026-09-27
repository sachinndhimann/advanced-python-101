"""
Chapter 12 — Dependency Inversion Principle.
High-level code should depend on abstractions, not concrete low-level
implementations. This is Chapter 1's Dependency Injection, framed as
a principle.
"""
from abc import ABC, abstractmethod


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("BAD: high-level class hardcodes a concrete low-level dependency")
# ---------------------------------------------------------------------------
class SqlDatabase:
    def save(self, record: str) -> None:
        print(f"  [SQL DB] saved: {record}")

class OrderServiceBad:
    """OrderServiceBad (high-level policy: 'how orders are processed')
    directly constructs and depends on SqlDatabase (low-level detail:
    'how data is stored'). Swapping storage, or testing without a real
    database, means EDITING this class."""
    def __init__(self):
        self.db = SqlDatabase()   # hardcoded concrete dependency

    def place_order(self, order: str) -> None:
        self.db.save(order)

service_bad = OrderServiceBad()
service_bad.place_order("Order #1")
print("\nProblem: OrderServiceBad can ONLY ever use SqlDatabase. Testing it")
print("requires a real (or mocked-via-patching) SqlDatabase -- there's no")
print("clean seam to substitute a fake one.")


# ---------------------------------------------------------------------------
section("GOOD: high-level class depends on an abstraction, injected in")
# ---------------------------------------------------------------------------
class Database(ABC):
    """The ABSTRACTION both high-level and low-level code depend on.
    Notice the DEPENDENCY DIRECTION is inverted versus naive OOP: instead
    of high-level code depending on low-level details, BOTH depend on
    this abstraction in the middle."""
    @abstractmethod
    def save(self, record: str) -> None: ...

class SqlDatabaseGood(Database):
    def save(self, record: str) -> None:
        print(f"  [SQL DB] saved: {record}")

class InMemoryDatabase(Database):
    """A completely different low-level detail -- same abstraction."""
    def __init__(self):
        self.records = []
    def save(self, record: str) -> None:
        self.records.append(record)
        print(f"  [In-memory] saved: {record}")

class OrderServiceGood:
    """Depends on Database (the abstraction), injected via the constructor.
    Doesn't know or care which concrete implementation it's given."""
    def __init__(self, db: Database):
        self.db = db

    def place_order(self, order: str) -> None:
        self.db.save(order)

print("\nWith a real-style database:")
service_real = OrderServiceGood(SqlDatabaseGood())
service_real.place_order("Order #2")

print("\nWith a fake, for testing -- ZERO changes to OrderServiceGood:")
fake_db = InMemoryDatabase()
service_test = OrderServiceGood(fake_db)
service_test.place_order("Order #3 (test)")
print(f"  Fake DB captured: {fake_db.records}")


# ---------------------------------------------------------------------------
section("When NOT to over-apply this")
# ---------------------------------------------------------------------------
print("If there will only EVER be one implementation (e.g. a tiny internal")
print("script that will never be tested in isolation or swapped), injecting")
print("an abstraction is ceremony with no payoff. DIP earns its cost when")
print("you genuinely need to swap implementations (real vs fake for tests,")
print("or one vendor vs another) -- which is extremely common in real")
print("production services, hence why this principle is so widely applied there.")
