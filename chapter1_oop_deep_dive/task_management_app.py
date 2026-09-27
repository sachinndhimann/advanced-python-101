"""
Chapter 1 — a small Task Management System combining OOP concepts:
dataclasses, properties, ABCs/Protocols, composition, aggregation, and
dependency injection. This is deliberately small; Module 15 builds a
larger production-style application on the same foundations.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


# --- Entities -----------------------------------------------------------
@dataclass
class User:
    """A dataclass: mostly data, little behavior. Auto __init__/__repr__/__eq__."""
    name: str
    email: str


@dataclass
class Project:
    name: str
    owner: User


class Task:
    """A hand-written class (not a dataclass) because it has real
    invariants (title validation) enforced through a property, plus
    behavior beyond plain data storage."""

    def __init__(self, title: str, project: Project, assignee: Optional[User] = None):
        self.title = title          # goes through the property setter below
        self.project = project      # AGGREGATION: project exists independently
        self.assignee = assignee    # AGGREGATION: user exists independently
        self.done = False

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Task title cannot be empty")
        if len(value) > 200:
            raise ValueError("Task title too long (max 200 chars)")
        self._title = value.strip()

    def mark_done(self) -> None:
        self.done = True

    def __repr__(self) -> str:
        status = "done" if self.done else "pending"
        who = self.assignee.name if self.assignee else "unassigned"
        return f"Task('{self.title}', project={self.project.name}, {who}, {status})"


# --- Repository layer: ABC defines the contract -------------------------
class TaskRepository(ABC):
    """Anything that wants to be a TaskRepository MUST implement these.
    TaskManager (below) depends on THIS abstraction, not a concrete class
    -- that's Dependency Inversion (Module 12) in miniature."""

    @abstractmethod
    def add(self, task: Task) -> None: ...

    @abstractmethod
    def all(self) -> list[Task]: ...

    @abstractmethod
    def pending(self) -> list[Task]: ...


class InMemoryTaskRepository(TaskRepository):
    """One concrete implementation. Swappable for a database-backed or
    JSON-file-backed one without touching TaskManager at all."""

    def __init__(self):
        self._tasks: list[Task] = []

    def add(self, task: Task) -> None:
        self._tasks.append(task)

    def all(self) -> list[Task]:
        return list(self._tasks)

    def pending(self) -> list[Task]:
        return [t for t in self._tasks if not t.done]


# --- Service layer: composition + dependency injection -------------------
class TaskManager:
    """COMPOSES a repository (has-a, not is-a) and receives it via
    DEPENDENCY INJECTION -- the constructor takes the repository as a
    parameter rather than constructing a concrete one itself. This is
    the single change that makes TaskManager trivially testable."""

    def __init__(self, repository: TaskRepository):
        self._repository = repository

    def create_task(self, title: str, project: Project, assignee: Optional[User] = None) -> Task:
        task = Task(title=title, project=project, assignee=assignee)
        self._repository.add(task)
        return task

    def complete_task(self, task: Task) -> None:
        task.mark_done()

    def pending_report(self) -> str:
        pending = self._repository.pending()
        if not pending:
            return "No pending tasks."
        lines = [f"- {t}" for t in pending]
        return f"{len(pending)} pending task(s):\n" + "\n".join(lines)


# --- Demo -----------------------------------------------------------------
if __name__ == "__main__":
    sachin = User(name="Sachin", email="sachin@example.com")
    project = Project(name="DocGen Platform", owner=sachin)

    repo = InMemoryTaskRepository()          # concrete repo, chosen HERE
    manager = TaskManager(repository=repo)   # injected into the manager

    t1 = manager.create_task("Write module 1 docs", project, sachin)
    t2 = manager.create_task("Review PR #42", project)
    manager.complete_task(t1)

    print(manager.pending_report())
    print()
    print("All tasks:", repo.all())

    print()
    print("--- Demonstrating why validation lives in the property ---")
    try:
        t2.title = ""   # bypasses create_task entirely, still caught
    except ValueError as e:
        print(f"Blocked invalid direct assignment: {e}")

    print()
    print("--- Demonstrating DI swappability with a fake repo (no changes to TaskManager) ---")

    class RecordingFakeRepository(TaskRepository):
        def __init__(self):
            self.added = []
        def add(self, task):
            self.added.append(task)
        def all(self):
            return self.added
        def pending(self):
            return [t for t in self.added if not t.done]

    fake_repo = RecordingFakeRepository()
    test_manager = TaskManager(repository=fake_repo)   # same class, different repo
    test_manager.create_task("Fake task for a unit test", project)
    print("Fake repo recorded:", fake_repo.added)
