"""
Chapter 3 — building the Iterable/Iterator protocol by hand: a custom
iterator, an infinite iterator, and a stateful iterator.
"""


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("A custom iterator: implements both __iter__ and __next__")
# ---------------------------------------------------------------------------
class Countdown:
    """This class is BOTH an iterable (__iter__) and an iterator
    (__next__). That's the common but slightly confusing pattern where a
    class is its own iterator -- fine for single-pass use, but see the
    'gotcha' section below for why it's not always the best design."""

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self   # "I am my own iterator"

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

print("Countdown(5):", end=" ")
for n in Countdown(5):
    print(n, end=" ")
print()

# Manual protocol walkthrough -- this is what the for-loop does internally:
cd = Countdown(3)
it = iter(cd)          # calls cd.__iter__()
print("Manual next() calls:", next(it), next(it), next(it))
try:
    next(it)
except StopIteration:
    print("4th next() raised StopIteration, as expected")


# ---------------------------------------------------------------------------
section("Gotcha: a single-pass iterator can't be reused")
# ---------------------------------------------------------------------------
cd2 = Countdown(3)
print("First pass:", list(cd2))
print("Second pass over the SAME instance:", list(cd2))  # empty! already exhausted


# ---------------------------------------------------------------------------
section("Fix: separate the Iterable from the Iterator")
# ---------------------------------------------------------------------------
class CountdownRange:
    """This class is an ITERABLE only. Each call to __iter__ builds a
    FRESH iterator object, so the same CountdownRange can be iterated
    over multiple times independently -- like a real list."""

    def __init__(self, start):
        self.start = start

    def __iter__(self):
        return _CountdownIterator(self.start)


class _CountdownIterator:
    """The actual iterator: holds the per-iteration state."""
    def __init__(self, current):
        self.current = current

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


cr = CountdownRange(3)
print("First pass:", list(cr))
print("Second pass over the SAME iterable:", list(cr))  # works! fresh iterator each time


# ---------------------------------------------------------------------------
section("An infinite iterator")
# ---------------------------------------------------------------------------
class NaturalNumbers:
    """No upper bound -- StopIteration is never raised. The CONSUMER is
    responsible for deciding when to stop (via break, itertools.islice,
    or similar). This is a real, useful pattern for streams with no
    natural end (sensor readings, an event feed, etc.)."""

    def __iter__(self):
        return self

    def __init__(self):
        self.n = 0

    def __next__(self):
        self.n += 1
        return self.n

naturals = NaturalNumbers()
collected = []
for n in naturals:
    if n > 5:
        break             # the consumer decides when to stop
    collected.append(n)
print(f"First 5 natural numbers via break: {collected}")


# ---------------------------------------------------------------------------
section("A stateful iterator reflecting external state")
# ---------------------------------------------------------------------------
class LiveQueueIterator:
    """Iterates over a queue that can have items added to it WHILE
    iteration is in progress -- demonstrating that an iterator's state
    isn't limited to 'position in a fixed sequence'. It ends only when
    told to (a sentinel), not when a fixed length is reached."""

    _SENTINEL = object()

    def __init__(self):
        self._queue = []
        self._closed = False

    def push(self, item):
        self._queue.append(item)

    def close(self):
        self._closed = True

    def __iter__(self):
        return self

    def __next__(self):
        if self._queue:
            return self._queue.pop(0)
        if self._closed:
            raise StopIteration
        return self._SENTINEL   # "nothing right now, but not finished either"

live = LiveQueueIterator()
live.push("event 1")
live.push("event 2")

results = []
for _ in range(5):
    try:
        item = next(live)
    except StopIteration:
        break
    if item is LiveQueueIterator._SENTINEL:
        live.push("event 3 (added mid-iteration)")
        live.close()
        continue
    results.append(item)

print(f"Consumed from a live, mutating queue: {results}")
