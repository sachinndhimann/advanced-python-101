# Chapter 13 — Design Patterns in Python

## Concept

For each pattern:

```
Problem -> Why the naive approach fails -> Pattern -> Implementation -> Trade-offs -> Real-world use
```

Patterns are not automatically good — each file ends with an honest
trade-off, because reaching for a pattern where a plain function or
dict would do is a real, common way to make code WORSE, not better.

## Patterns covered

- **Factory** — centralize object creation logic so callers don't need
  to know which concrete class to instantiate.
- **Strategy** — swap an algorithm/behavior at runtime (you already
  built this in Chapter 12's Open/Closed example).
- **Adapter** — make an incompatible interface work where a different
  one is expected, without modifying the incompatible thing.
- **Observer** — one object (subject) notifies many dependents
  (observers) automatically when its state changes.
- **Repository** — abstract data access behind a collection-like
  interface (you already built this in Chapter 1/12).
- **Dependency Injection** — covered thoroughly in Chapters 1 and 12;
  this file adds a small DI "container" for when manual injection gets
  repetitive.
- **Command** — encapsulate an action (plus its arguments) as an object,
  so it can be queued, logged, or undone.
- **Singleton** — ensure exactly one instance of a class exists globally
  (you touched this in Module 1's `__new__` exercise).
- **Builder** — construct a complex object step by step, separating
  construction from representation.

## Mental model

Every pattern here answers "how do I keep two things decoupled while
still letting them work together?" — decoupling creation from use
(Factory, Builder, Singleton), decoupling behavior from the class using
it (Strategy, Command), decoupling incompatible shapes (Adapter),
decoupling notification from the notified (Observer), decoupling policy
from storage detail (Repository, DI).

## Files (one pattern per file, runnable)

`factory.py`, `strategy.py`, `adapter.py`, `observer.py`, `repository.py`,
`dependency_injection.py`, `command.py`, `singleton.py`, `builder.py`

## Run it

```bash
python3 factory.py
python3 strategy.py
python3 adapter.py
python3 observer.py
python3 repository.py
python3 dependency_injection.py
python3 command.py
python3 singleton.py
python3 builder.py
```

## Experiment

1. In `command.py`, implement `undo()` for one more command type beyond
   the one provided.
2. In `observer.py`, add a second observer type and confirm the subject
   needs zero code changes to notify it — that's the actual payoff of
   the pattern.
3. Pick ONE pattern here you don't currently use in your own codebase,
   and find (or imagine) a real spot in the UKG DocGen four-repo pipeline
   where it would genuinely reduce coupling — then write one paragraph on
   whether it's actually worth introducing there, applying this chapter's
   "when does the trade-off pay off" lens for real.
