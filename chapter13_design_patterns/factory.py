"""
Chapter 13 — Factory Pattern.
Problem: callers need to create objects but shouldn't need to know which
concrete class to instantiate, or how.
"""
from abc import ABC, abstractmethod


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("Why the naive approach fails")
# ---------------------------------------------------------------------------
class EmailNotification:
    def send(self, msg): print(f"  [Email] {msg}")

class SmsNotification:
    def send(self, msg): print(f"  [SMS] {msg}")

def naive_send(channel: str, msg: str):
    # Every caller that needs a notification must know about EVERY
    # concrete class AND the construction logic -- this duplicates and
    # spreads out across the codebase as more callers appear.
    if channel == "email":
        notifier = EmailNotification()
    elif channel == "sms":
        notifier = SmsNotification()
    else:
        raise ValueError(channel)
    notifier.send(msg)

naive_send("email", "hello via naive approach")
print("Problem: every call site that creates a notifier repeats this")
print("if/elif -- adding a new channel means finding and editing them all.")


# ---------------------------------------------------------------------------
section("Factory: centralize creation logic in ONE place")
# ---------------------------------------------------------------------------
class Notification(ABC):
    @abstractmethod
    def send(self, msg: str) -> None: ...

class EmailNotificationGood(Notification):
    def send(self, msg): print(f"  [Email] {msg}")

class SmsNotificationGood(Notification):
    def send(self, msg): print(f"  [SMS] {msg}")

class SlackNotificationGood(Notification):
    def send(self, msg): print(f"  [Slack] {msg}")


class NotificationFactory:
    """The ONLY place that knows about concrete classes and how to build
    them. Every caller depends on this factory + the Notification
    abstraction, never on concrete classes directly."""
    _registry = {
        "email": EmailNotificationGood,
        "sms": SmsNotificationGood,
        "slack": SlackNotificationGood,
    }

    @classmethod
    def create(cls, channel: str) -> Notification:
        notification_cls = cls._registry.get(channel)
        if notification_cls is None:
            raise ValueError(f"Unknown channel: {channel}")
        return notification_cls()


def send_via_factory(channel: str, msg: str):
    notifier = NotificationFactory.create(channel)   # caller doesn't know/care which class
    notifier.send(msg)

send_via_factory("slack", "hello via factory")
print("\nAdding a new channel means registering ONE new class in the factory --")
print("callers like send_via_factory() never change.")


# ---------------------------------------------------------------------------
section("Trade-offs")
# ---------------------------------------------------------------------------
print("Cost: one more layer of indirection -- you can't just Ctrl+click a")
print("class name to see what gets built; you go through the factory's")
print("registry first. Worth it once there are 3+ concrete types AND")
print("multiple call sites that create them; not worth it for one type")
print("constructed in one place.")


# ---------------------------------------------------------------------------
section("Real-world use")
# ---------------------------------------------------------------------------
print("Django's forms/model field system, logging.getLogger() (returns")
print("different logger configurations by name), and most plugin systems")
print("(e.g. 'give me a parser for this file extension') use factories.")
