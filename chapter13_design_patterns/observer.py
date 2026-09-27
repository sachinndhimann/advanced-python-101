"""
Chapter 13 — Observer Pattern.
Problem: one object's state change needs to notify many dependents,
without that object needing to know who they are or hardcode calls to them.
"""
from abc import ABC, abstractmethod


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


section("Why the naive approach fails")

class TaskBad:
    """Hardcodes every side-effect of completion directly -- adding a
    new side-effect (e.g. also notify Slack) means editing THIS class."""
    def mark_done(self):
        print("  [TaskBad] marked done")
        print("  [TaskBad] -> sending email (hardcoded)")
        print("  [TaskBad] -> updating analytics (hardcoded)")

TaskBad().mark_done()
print("Problem: Task itself has to know about email AND analytics AND")
print("anything else that should react -- growing and coupling over time.")


section("Observer: subject notifies registered observers, doesn't know them")

class Observer(ABC):
    @abstractmethod
    def on_task_done(self, task_title: str) -> None: ...

class EmailObserver(Observer):
    def on_task_done(self, task_title):
        print(f"  [EmailObserver] sending completion email for '{task_title}'")

class AnalyticsObserver(Observer):
    def on_task_done(self, task_title):
        print(f"  [AnalyticsObserver] recording completion metric for '{task_title}'")

class Task:
    def __init__(self, title: str):
        self.title = title
        self._observers: list[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        self._observers.append(observer)

    def mark_done(self) -> None:
        print(f"  [Task] '{self.title}' marked done")
        for observer in self._observers:
            observer.on_task_done(self.title)   # Task doesn't know WHAT these do

task = Task("Ship feature")
task.subscribe(EmailObserver())
task.subscribe(AnalyticsObserver())
task.mark_done()

print("\nAdding a THIRD observer (e.g. SlackObserver) means zero changes to Task:")
class SlackObserver(Observer):
    def on_task_done(self, task_title):
        print(f"  [SlackObserver] posting to #done channel: '{task_title}'")

task.subscribe(SlackObserver())
task2 = Task("Review PR")
task2.subscribe(EmailObserver())
task2.subscribe(SlackObserver())
task2.mark_done()


section("Trade-offs")
print("Harder to trace 'what happens when this fires' by reading one file --")
print("you have to know which observers are subscribed. Worth it when the")
print("set of reactions genuinely varies/grows; overkill for one fixed,")
print("never-changing side effect.")

section("Real-world use")
print("GUI event handlers (button.on_click), Django signals, RxPY/reactive")
print("streams, and pub/sub systems in general are all Observer at heart.")
