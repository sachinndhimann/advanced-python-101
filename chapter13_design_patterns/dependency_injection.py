"""
Chapter 13 — Dependency Injection Pattern.
Covered thoroughly in Chapters 1 and 12 (constructor injection). This
file adds a small DI CONTAINER for when manually wiring dependencies by
hand becomes repetitive across a larger app.
"""
from abc import ABC, abstractmethod


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


section("Recap: manual constructor injection (Chapters 1 & 12)")

class Notifier(ABC):
    @abstractmethod
    def send(self, msg: str) -> None: ...

class EmailNotifier(Notifier):
    def send(self, msg): print(f"  [Email] {msg}")

class OrderService:
    def __init__(self, notifier: Notifier):   # injected, not constructed inside
        self._notifier = notifier

    def place_order(self, item: str):
        self._notifier.send(f"Order placed: {item}")

service = OrderService(EmailNotifier())   # wired by hand, right here
service.place_order("Widget")
print("This is DI. Manually wiring is FINE for small apps -- the problem")
print("only appears once you have many classes with many dependencies.")


section("Why manual wiring gets repetitive at scale")

class Logger:
    def log(self, msg): print(f"  [Log] {msg}")

class Database:
    def query(self, q): return f"result for {q}"

class UserRepo:
    def __init__(self, db: Database, logger: Logger):
        self.db, self.logger = db, logger

class OrderRepo:
    def __init__(self, db: Database, logger: Logger):
        self.db, self.logger = db, logger

class AppBad:
    def __init__(self):
        # Every new class needing Database+Logger repeats this wiring by hand.
        db = Database()
        logger = Logger()
        self.user_repo = UserRepo(db, logger)
        self.order_repo = OrderRepo(db, logger)
        # ...and this grows linearly with every new repository/service added.

AppBad()
print("Problem: wiring logic is duplicated and grows with every new class")
print("that needs the same shared dependencies (db, logger).")


section("A minimal DI container: centralize the wiring")

class Container:
    """A tiny container: register how to build each type once, then
    resolve() builds (and reuses) instances as needed. Real frameworks
    (e.g. `dependency-injector`, FastAPI's Depends) formalize this with
    much more machinery -- same core idea."""
    def __init__(self):
        self._singletons = {}
        self._factories = {}

    def register_singleton(self, key, instance):
        self._singletons[key] = instance

    def register_factory(self, key, factory):
        self._factories[key] = factory

    def resolve(self, key):
        if key in self._singletons:
            return self._singletons[key]
        if key in self._factories:
            return self._factories[key](self)
        raise KeyError(f"Nothing registered for '{key}'")

container = Container()
container.register_singleton("db", Database())
container.register_singleton("logger", Logger())
container.register_factory("user_repo", lambda c: UserRepo(c.resolve("db"), c.resolve("logger")))
container.register_factory("order_repo", lambda c: OrderRepo(c.resolve("db"), c.resolve("logger")))

user_repo = container.resolve("user_repo")
order_repo = container.resolve("order_repo")
print(f"  user_repo.db is order_repo.db (same shared singleton): {user_repo.db is order_repo.db}")


section("Trade-offs")
print("A container adds indirection and a little 'magic' (harder to trace")
print("who constructs what by reading code alone). Worth it once you have")
print("many classes sharing dependencies across a larger app; pure overhead")
print("for a handful of classes you can wire by hand in one place.")

section("Real-world use")
print("FastAPI's Depends(), pytest fixtures, Spring (Java) DI containers,")
print("and most 'app factory' patterns in web frameworks.")
