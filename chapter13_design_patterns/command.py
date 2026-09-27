"""
Chapter 13 — Command Pattern.
Problem: an action (plus its arguments/context) needs to be queued,
logged, delayed, or undone -- not just called immediately and forgotten.
"""
from abc import ABC, abstractmethod


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


section("Why the naive approach fails")

class TextEditorBad:
    def __init__(self):
        self.text = ""
    def insert(self, s: str):
        self.text += s   # once called, there's no record of WHAT happened to undo

editor_bad = TextEditorBad()
editor_bad.insert("Hello ")
editor_bad.insert("World")
print(f"  text: {editor_bad.text!r}")
print("Problem: no record of individual actions exists -- undo, redo, or")
print("logging 'what happened and in what order' isn't possible after the fact.")


section("Command: wrap each action as an object with execute()/undo()")

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...

class TextEditor:
    def __init__(self):
        self.text = ""

class InsertTextCommand(Command):
    def __init__(self, editor: TextEditor, text: str):
        self.editor = editor
        self.text = text

    def execute(self) -> None:
        self.editor.text += self.text

    def undo(self) -> None:
        self.editor.text = self.editor.text[: -len(self.text)]

class CommandHistory:
    """Not just execution -- a queryable, undoable LOG of what happened."""
    def __init__(self):
        self._history: list[Command] = []

    def run(self, command: Command) -> None:
        command.execute()
        self._history.append(command)

    def undo_last(self) -> None:
        if self._history:
            self._history.pop().undo()

editor = TextEditor()
history = CommandHistory()

history.run(InsertTextCommand(editor, "Hello "))
history.run(InsertTextCommand(editor, "World"))
print(f"  After two inserts: {editor.text!r}")

history.undo_last()
print(f"  After undo_last(): {editor.text!r}")

history.undo_last()
print(f"  After undo_last() again: {editor.text!r}")


section("Trade-offs")
print("Every action becomes a class -- more boilerplate than a direct")
print("method call. Worth it when you genuinely need undo/redo, queuing,")
print("replay, or an audit log of actions; pure overhead for a fire-and-")
print("forget action nobody will ever need to reverse or replay.")

section("Real-world use")
print("Undo/redo in any editor, task queues (Celery tasks ARE commands),")
print("and GUI toolkit 'Action' objects bound to menu items and buttons.")
