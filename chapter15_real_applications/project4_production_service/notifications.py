"""
Project 4 — a Notifier abstraction (Ch.12 DIP) with a real-ish async
implementation and a fake for tests.
"""
import asyncio
from abc import ABC, abstractmethod
from domain import NotificationFailedError


class Notifier(ABC):
    @abstractmethod
    async def notify(self, email: str, message: str) -> None: ...


class AsyncEmailNotifier(Notifier):
    """Stands in for a real async email API call (Ch.6)."""
    async def notify(self, email: str, message: str) -> None:
        await asyncio.sleep(0.05)   # simulated network I/O
        if "@" not in email:
            raise NotificationFailedError(f"Invalid email address: {email}")
        print(f"  [EmailNotifier] sent to {email}: {message}")


class RecordingFakeNotifier(Notifier):
    """Used in tests: records calls instead of doing real I/O."""
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    async def notify(self, email: str, message: str) -> None:
        self.sent.append((email, message))
