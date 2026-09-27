"""
Chapter 13 — Repository Pattern.
Problem: business logic gets tangled with data-access details (SQL,
file I/O, API calls), making it hard to test or swap storage.
(You already built this in Chapters 1 and 12 -- this file names the
pattern explicitly and shows it once more, standalone.)
"""
from abc import ABC, abstractmethod


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


section("Why the naive approach fails")

class UserServiceBad:
    """Business logic directly contains raw storage details (a plain
    list standing in for 'a database'). Testing this means either using
    the real list every time, or manually resetting it between tests --
    and swapping to a real database means rewriting THIS class."""
    def __init__(self):
        self._raw_storage = []   # imagine this is raw SQL/file access instead

    def register_user(self, name: str) -> None:
        if any(u == name for u in self._raw_storage):
            raise ValueError("User already exists")
        self._raw_storage.append(name)

svc_bad = UserServiceBad()
svc_bad.register_user("Sachin")
print(f"  Registered (bad): {svc_bad._raw_storage}")
print("Problem: storage details (a list here, SQL in reality) are baked")
print("directly into the business logic class.")


section("Repository: abstract storage behind a collection-like interface")

class UserRepository(ABC):
    @abstractmethod
    def add(self, name: str) -> None: ...
    @abstractmethod
    def exists(self, name: str) -> bool: ...

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users = []
    def add(self, name): self._users.append(name)
    def exists(self, name): return name in self._users

class SqlUserRepository(UserRepository):
    """Stands in for a real SQL-backed implementation -- same interface."""
    def add(self, name):
        print(f"  [SQL] INSERT INTO users (name) VALUES ('{name}')")
    def exists(self, name):
        print(f"  [SQL] SELECT EXISTS(... WHERE name='{name}')")
        return False   # mocked

class UserService:
    """Business logic depends ONLY on the UserRepository abstraction."""
    def __init__(self, repository: UserRepository):
        self._repo = repository

    def register_user(self, name: str) -> None:
        if self._repo.exists(name):
            raise ValueError("User already exists")
        self._repo.add(name)

svc = UserService(InMemoryUserRepository())
svc.register_user("Sachin")
print("  Registered via in-memory repo, business logic untouched by storage details")

svc_sql = UserService(SqlUserRepository())
svc_sql.register_user("Alex")


section("Trade-offs")
print("An extra abstraction + implementation class per storage backend.")
print("Worth it the moment you need tests without a real database, or")
print("expect to support more than one storage backend; not worth it for")
print("a throwaway script hitting one fixed data source once.")

section("Real-world use")
print("Django's ORM QuerySet, SQLAlchemy sessions wrapped behind app-specific")
print("repositories, and any 'swap Postgres for a test double' setup.")
