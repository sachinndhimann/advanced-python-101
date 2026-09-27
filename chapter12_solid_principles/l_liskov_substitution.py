"""
Chapter 12 — Liskov Substitution Principle.
A subclass must be usable anywhere its parent is expected, without
breaking the caller's assumptions.
"""


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("BAD: a subclass that breaks the parent's contract")
# ---------------------------------------------------------------------------
class Bird:
    def fly(self) -> str:
        return "flying"

class Sparrow(Bird):
    pass   # inherits fly() correctly, fine

class Penguin(Bird):
    """Penguins can't fly -- but Penguin IS-A Bird in the taxonomy sense.
    Forcing it into this hierarchy breaks the CONTRACT that 'any Bird can
    fly()', even though it's biologically an 'is-a' relationship."""
    def fly(self) -> str:
        raise NotImplementedError("Penguins can't fly!")

def make_it_fly(bird: Bird) -> str:
    """Any caller of this function reasonably assumes ANY Bird works here
    -- that's the whole point of typing the parameter as Bird."""
    return bird.fly()

print(f"make_it_fly(Sparrow()): {make_it_fly(Sparrow())}")
try:
    make_it_fly(Penguin())
except NotImplementedError as e:
    print(f"make_it_fly(Penguin()) BREAKS the caller's assumption: {e}")

print("\nProblem: any code written against 'Bird' and correctly tested with")
print("Sparrow can crash the moment a Penguin is substituted in -- that's")
print("exactly the Liskov violation: the subclass isn't truly substitutable.")


# ---------------------------------------------------------------------------
section("GOOD: model the actual capability, not the taxonomy")
# ---------------------------------------------------------------------------
from abc import ABC, abstractmethod

class BirdGood(ABC):
    """The base no longer promises flight -- because not all birds can."""
    @abstractmethod
    def move(self) -> str: ...

class FlyingBird(BirdGood):
    def move(self) -> str:
        return "flying"

class SparrowGood(FlyingBird):
    pass

class PenguinGood(BirdGood):
    def move(self) -> str:
        return "swimming"   # a real, valid behavior for THIS bird

def make_it_move(bird: BirdGood) -> str:
    return bird.move()   # every BirdGood genuinely supports this, no surprises

print(f"make_it_move(SparrowGood()): {make_it_move(SparrowGood())}")
print(f"make_it_move(PenguinGood()): {make_it_move(PenguinGood())}")
print("\nEvery subclass is now truly substitutable -- move() never breaks the caller.")


# ---------------------------------------------------------------------------
section("When NOT to over-apply this")
# ---------------------------------------------------------------------------
print("Don't invent elaborate capability hierarchies for a closed, known set")
print("of types that will never be substituted polymorphically. If EVERY")
print("caller already knows exactly which concrete bird type it has and")
print("branches on it explicitly, the substitutability guarantee LSP")
print("protects isn't actually being relied on anywhere.")
