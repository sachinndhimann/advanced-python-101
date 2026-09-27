"""
Chapter 1 — isolated demonstrations of each OOP concept.
Run this file directly; each section prints its own labeled output.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("Instance vs class attributes (and the mutable-default trap)")
# ---------------------------------------------------------------------------
class Counter:
    total_created = 0          # class attribute: shared

    def __init__(self):
        self.id = Counter.total_created   # instance attribute: per-object
        Counter.total_created += 1

c1, c2 = Counter(), Counter()
print(f"c1.id={c1.id}, c2.id={c2.id}, Counter.total_created={Counter.total_created}")

class BuggyTask:
    tags = []                   # DANGER: shared mutable class attribute
    def add_tag(self, tag):
        self.tags.append(tag)   # mutates the SHARED list

bt1, bt2 = BuggyTask(), BuggyTask()
bt1.add_tag("urgent")
print(f"Bug demonstrated: bt2.tags = {bt2.tags}  (leaked from bt1!)")

class FixedTask:
    def __init__(self):
        self.tags = []           # instance attribute: per-object, fixed
    def add_tag(self, tag):
        self.tags.append(tag)

ft1, ft2 = FixedTask(), FixedTask()
ft1.add_tag("urgent")
print(f"Fixed: ft2.tags = {ft2.tags}  (empty, as expected)")


# ---------------------------------------------------------------------------
section("Instance / class / static methods")
# ---------------------------------------------------------------------------
class Task:
    all_tasks = []

    def __init__(self, title):
        self.title = title
        self.done = False
        Task.all_tasks.append(self)

    def mark_done(self):                     # instance method
        self.done = True

    @classmethod
    def from_dict(cls, data):                # classmethod: alt constructor
        return cls(title=data["title"])

    @classmethod
    def pending_count(cls):                  # classmethod: class-level query
        return sum(1 for t in cls.all_tasks if not t.done)

    @staticmethod
    def is_valid_title(title):               # staticmethod: pure helper
        return bool(title) and len(title) <= 100

t1 = Task("Write report")
t2 = Task.from_dict({"title": "Review PR"})
t1.mark_done()
print(f"pending_count={Task.pending_count()}, valid('')={Task.is_valid_title('')}")


# ---------------------------------------------------------------------------
section("Encapsulation: convention, not enforcement")
# ---------------------------------------------------------------------------
class Account:
    def __init__(self, balance):
        self._balance = balance      # protected: convention only
        self.__secret = "mangled"    # name-mangled

acct = Account(100)
print(f"_balance accessible anyway: {acct._balance}")
print(f"real mangled name: {list(acct.__dict__.keys())}")


# ---------------------------------------------------------------------------
section("Properties: validation without breaking attribute syntax")
# ---------------------------------------------------------------------------
class ValidatedTask:
    def __init__(self, title):
        self.title = title   # goes through the setter below

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not value:
            raise ValueError("Title cannot be empty")
        self._title = value

vt = ValidatedTask("Ship feature")
print(f"vt.title = {vt.title}")
try:
    vt.title = ""             # looks like plain assignment, actually calls the setter
except ValueError as e:
    print(f"Caught: {e}")


# ---------------------------------------------------------------------------
section("Inheritance vs Composition")
# ---------------------------------------------------------------------------
class Notifier:
    def send(self, message):
        return f"[EMAIL] {message}"

class InheritedReminder(Notifier):        # "is-a" Notifier
    def remind(self, task_title):
        return self.send(f"Reminder: {task_title}")

class ComposedReminder:                   # "has-a" Notifier (preferred default)
    def __init__(self, notifier: Notifier):
        self._notifier = notifier
    def remind(self, task_title):
        return self._notifier.send(f"Reminder: {task_title}")

print(InheritedReminder().remind("Write report"))
print(ComposedReminder(Notifier()).remind("Write report"))
print("Composition wins here because swapping notifiers needs zero inheritance change:")

class SlackNotifier(Notifier):
    def send(self, message):
        return f"[SLACK] {message}"

print(ComposedReminder(SlackNotifier()).remind("Write report"))


# ---------------------------------------------------------------------------
section("Abstract Base Classes: enforced contracts")
# ---------------------------------------------------------------------------
class TaskRepository(ABC):
    @abstractmethod
    def save(self, task): ...
    @abstractmethod
    def get_all(self): ...

try:
    TaskRepository()   # cannot instantiate: contract not fulfilled
except TypeError as e:
    print(f"Caught (expected): {e}")

class InMemoryRepo(TaskRepository):
    def __init__(self):
        self._items = []
    def save(self, task):
        self._items.append(task)
    def get_all(self):
        return list(self._items)

repo = InMemoryRepo()
repo.save("a task")
print(f"ABC-backed repo works: {repo.get_all()}")


# ---------------------------------------------------------------------------
section("Protocols: structural typing, no inheritance required")
# ---------------------------------------------------------------------------
class SupportsSave(Protocol):
    def save(self, task) -> None: ...

class ThirdPartyLogger:            # doesn't inherit from anything of ours
    def save(self, task):
        print(f"[external logger] saved: {task}")

def persist(target: SupportsSave, task):
    target.save(task)              # type-checkers accept ThirdPartyLogger here
                                    # because it structurally matches, no
                                    # inheritance relationship needed

persist(ThirdPartyLogger(), "some task")


# ---------------------------------------------------------------------------
section("Dataclasses: less boilerplate for data-holding classes")
# ---------------------------------------------------------------------------
@dataclass
class User:
    name: str
    email: str
    active: bool = True
    roles: list = field(default_factory=list)   # avoids the mutable-default trap

u1 = User(name="Sachin", email="s@example.com")
u2 = User(name="Sachin", email="s@example.com")
print(f"auto __repr__: {u1}")
print(f"auto __eq__: u1 == u2 -> {u1 == u2}")


# ---------------------------------------------------------------------------
section("Magic/dunder methods: integrate with Python's own protocols")
# ---------------------------------------------------------------------------
class Money:
    def __init__(self, cents):
        self.cents = cents
    def __repr__(self):
        return f"Money({self.cents})"
    def __eq__(self, other):
        return isinstance(other, Money) and self.cents == other.cents
    def __add__(self, other):
        return Money(self.cents + other.cents)
    def __lt__(self, other):
        return self.cents < other.cents

m1, m2 = Money(500), Money(250)
print(f"{m1} + {m2} = {m1 + m2}")
print(f"m1 == Money(500): {m1 == Money(500)}")
print(f"m2 < m1: {m2 < m1}")


# ---------------------------------------------------------------------------
section("Dependency Injection: pass collaborators in, don't build them inside")
# ---------------------------------------------------------------------------
class HardCodedManager:
    def __init__(self):
        self._repo = InMemoryRepo()   # BAD for testing: always this one repo

class InjectedManager:
    def __init__(self, repo: TaskRepository):   # GOOD: caller decides
        self._repo = repo

class FakeRepoForTesting(TaskRepository):
    def __init__(self):
        self.saved = []
    def save(self, task):
        self.saved.append(task)
    def get_all(self):
        return self.saved

fake = FakeRepoForTesting()
manager = InjectedManager(fake)     # trivially testable, no real repo needed
manager._repo.save("test task")
print(f"Injected fake repo captured: {fake.saved}")
