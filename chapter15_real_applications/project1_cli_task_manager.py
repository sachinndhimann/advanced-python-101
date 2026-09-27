"""
Chapter 15, Project 1 — CLI Task Manager.

Combines: OOP (Ch.1), type hints (Ch.11), exceptions (Ch.5), logging
(Ch.10), dataclasses (Ch.1). Persists tasks to a JSON file next to this
script.

Usage:
    python3 project1_cli_task_manager.py add "Write docs"
    python3 project1_cli_task_manager.py list
    python3 project1_cli_task_manager.py complete 1
    python3 project1_cli_task_manager.py delete 1
"""
import json
import logging
import os
import sys
from dataclasses import dataclass, asdict
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("task_manager")

STORE_PATH = os.path.join(os.path.dirname(__file__), "_tasks_store.json")


# --- Domain -----------------------------------------------------------
@dataclass
class Task:
    id: int
    title: str
    done: bool = False


class TaskManagerError(Exception):
    """Base for all errors this app raises on purpose."""

class TaskNotFoundError(TaskManagerError):
    pass

class InvalidTaskError(TaskManagerError):
    pass


# --- Persistence (a tiny repository, Ch.1/12/13 pattern) ---------------
class JsonTaskStore:
    def __init__(self, path: str):
        self._path = path

    def load(self) -> list[Task]:
        if not os.path.exists(self._path):
            return []
        try:
            with open(self._path, "r") as f:
                raw = json.load(f)
            return [Task(**item) for item in raw]
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Corrupt task store, starting fresh: {e}")
            return []

    def save(self, tasks: list[Task]) -> None:
        with open(self._path, "w") as f:
            json.dump([asdict(t) for t in tasks], f, indent=2)


# --- Service layer ------------------------------------------------------
class TaskManager:
    def __init__(self, store: JsonTaskStore):
        self._store = store
        self._tasks = store.load()

    def add(self, title: str) -> Task:
        if not title or not title.strip():
            raise InvalidTaskError("Task title cannot be empty")
        next_id = max((t.id for t in self._tasks), default=0) + 1
        task = Task(id=next_id, title=title.strip())
        self._tasks.append(task)
        self._store.save(self._tasks)
        logger.info(f"Added task #{task.id}: {task.title}")
        return task

    def list_tasks(self) -> list[Task]:
        return list(self._tasks)

    def _find(self, task_id: int) -> Task:
        for t in self._tasks:
            if t.id == task_id:
                return t
        raise TaskNotFoundError(f"No task with id {task_id}")

    def complete(self, task_id: int) -> Task:
        task = self._find(task_id)
        task.done = True
        self._store.save(self._tasks)
        logger.info(f"Completed task #{task.id}")
        return task

    def delete(self, task_id: int) -> None:
        task = self._find(task_id)
        self._tasks.remove(task)
        self._store.save(self._tasks)
        logger.info(f"Deleted task #{task.id}")


# --- CLI -----------------------------------------------------------------
def print_tasks(tasks: list[Task]) -> None:
    if not tasks:
        print("No tasks yet.")
        return
    for t in tasks:
        status = "x" if t.done else " "
        print(f"[{status}] #{t.id}  {t.title}")


def main(argv: list[str]) -> int:
    manager = TaskManager(JsonTaskStore(STORE_PATH))

    if not argv:
        print("Usage: add <title> | list | complete <id> | delete <id>")
        return 1

    command = argv[0]
    try:
        if command == "add":
            if len(argv) < 2:
                raise InvalidTaskError("Usage: add <title>")
            task = manager.add(" ".join(argv[1:]))
            print(f"Added #{task.id}: {task.title}")

        elif command == "list":
            print_tasks(manager.list_tasks())

        elif command == "complete":
            if len(argv) < 2:
                raise InvalidTaskError("Usage: complete <id>")
            task = manager.complete(int(argv[1]))
            print(f"Completed #{task.id}: {task.title}")

        elif command == "delete":
            if len(argv) < 2:
                raise InvalidTaskError("Usage: delete <id>")
            manager.delete(int(argv[1]))
            print(f"Deleted #{argv[1]}")

        else:
            print(f"Unknown command: {command}")
            return 1

    except TaskManagerError as e:
        # Expected, domain-level failure: clean message, no traceback spam.
        print(f"Error: {e}")
        return 1
    except ValueError:
        print("Error: id must be a number")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
