# Chapter 12 — SOLID Principles

## Concept

SOLID is five principles for keeping object-oriented code changeable
without it collapsing into spaghetti as it grows. Taught here entirely
through before/after code, not abstract definitions. Each file follows:

```
Bad code -> the problem it causes -> refactor -> the improvement -> when to NOT do this
```

## The five principles

- **S — Single Responsibility**: a class should have ONE reason to
  change. Not "one method" — one AXIS of change. Mixing "how to
  calculate a discount" with "how to send an email receipt" in one class
  means a change to email formatting risks breaking discount logic.
- **O — Open/Closed**: code should be open for extension, closed for
  modification. Adding a new case (e.g. a new discount type) should mean
  ADDING code, not editing a growing `if/elif` chain that touches
  existing, already-tested branches.
- **L — Liskov Substitution**: a subclass must be usable anywhere its
  parent is expected, without breaking the caller's assumptions. The
  classic violation: a `Square(Rectangle)` that overrides `width`'s
  setter to also change `height` — this breaks any code that assumed
  setting `Rectangle.width` doesn't affect `height`.
- **I — Interface Segregation**: don't force a class to implement methods
  it doesn't need just because they're bundled into one large interface.
  Split large interfaces into focused, specific ones.
- **D — Dependency Inversion**: high-level code should depend on
  abstractions (interfaces/protocols), not concrete low-level
  implementations. This is Chapter 1's Dependency Injection, formalized
  as a principle: `TaskManager` depending on `TaskRepository` (an ABC),
  not `InMemoryTaskRepository` directly.

## When SOLID can be overused

Every principle here has a cost: more classes, more indirection, more
files to jump between. Applying SOLID rigidly to a 20-line script that
will never change is over-engineering — the "when to NOT do this" section
in each file is not an afterthought, it's as important as the principle
itself. SOLID earns its cost in code that's genuinely expected to grow
or vary.

## Mental model

SOLID principles are all, underneath, about isolating the parts of your
code that change often from the parts that don't, so a change to one
doesn't ripple unpredictably into the other.

## Files (one principle each, self-contained, runnable)

- `s_single_responsibility.py`
- `o_open_closed.py`
- `l_liskov_substitution.py`
- `i_interface_segregation.py`
- `d_dependency_inversion.py`

Each file uses a realistic order-processing / notification scenario, so
you see the SAME kind of application evolve across all five principles.

## Run it

```bash
python3 s_single_responsibility.py
python3 o_open_closed.py
python3 l_liskov_substitution.py
python3 i_interface_segregation.py
python3 d_dependency_inversion.py
```

## Experiment

1. In `o_open_closed.py`, add a THIRD discount type to both the bad
   version (edit the `if/elif`) and the good version (add one new class)
   — feel directly how much smaller and safer the good version's change is.
2. In `l_liskov_substitution.py`, write a test function that takes any
   `Bird` and calls `.fly()` — run it against the bad hierarchy (with a
   `Penguin`) and watch it break, then run it against the fixed hierarchy.
3. In `d_dependency_inversion.py`, swap the injected dependency for a
   fake/mock version and confirm the high-level class needs zero changes
   — this is the same DI mechanic from Chapter 1, now framed as WHY it
   matters architecturally, not just how to write it.
