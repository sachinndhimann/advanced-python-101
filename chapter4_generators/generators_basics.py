"""
Chapter 4 — generator fundamentals: yield, yield from, generator
expressions, lazy evaluation, send(), close(), throw().
"""


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("A basic generator function")
# ---------------------------------------------------------------------------
def count_up_to(n):
    i = 1
    while i <= n:
        yield i           # pauses here, remembers `i`, resumes on next()
        i += 1

gen = count_up_to(3)
print(f"Calling the function returns a generator object immediately: {gen}")
print(f"Values: {list(gen)}")


# ---------------------------------------------------------------------------
section("Laziness made visible")
# ---------------------------------------------------------------------------
def noisy_range(n):
    for i in range(n):
        print(f"  [generator] about to yield {i}")
        yield i

print("Creating the generator (nothing printed yet):")
g = noisy_range(3)
print("Now consuming it one step at a time:")
for value in g:
    print(f"  [consumer] received {value}")


# ---------------------------------------------------------------------------
section("yield from: delegate to a sub-generator")
# ---------------------------------------------------------------------------
def inner():
    yield 1
    yield 2

def outer():
    yield "start"
    yield from inner()     # flattens inner's yields into outer's stream
    yield "end"

print(f"outer(): {list(outer())}")


# ---------------------------------------------------------------------------
section("Generator expressions: like list comprehensions, but lazy")
# ---------------------------------------------------------------------------
squares_list = [x * x for x in range(5)]        # eager: built entirely now
squares_gen = (x * x for x in range(5))          # lazy: nothing computed yet

print(f"List comprehension (eager): {squares_list}")
print(f"Generator expression object: {squares_gen}")
print(f"Consumed lazily: {list(squares_gen)}")


# ---------------------------------------------------------------------------
section("send(): pushing a value INTO a paused generator")
# ---------------------------------------------------------------------------
def running_total():
    total = 0
    while True:
        received = yield total    # yields current total, receives next value here
        if received is not None:
            total += received

acc = running_total()
next(acc)                  # PRIME the generator: advance to the first yield
print(f"After priming, current total: (nothing consumed yet)")
print(f"send(5) -> {acc.send(5)}")
print(f"send(10) -> {acc.send(10)}")
print(f"send(-3) -> {acc.send(-3)}")


# ---------------------------------------------------------------------------
section("Priming gotcha: send() before the first next() fails")
# ---------------------------------------------------------------------------
fresh = running_total()
try:
    fresh.send(5)     # generator hasn't reached the first yield yet
except TypeError as e:
    print(f"Caught (expected): {e}")


# ---------------------------------------------------------------------------
section("close(): stopping a generator early, cleanly")
# ---------------------------------------------------------------------------
def resource_generator():
    print("  [gen] resource acquired")
    try:
        yield 1
        yield 2
        yield 3
    finally:
        print("  [gen] resource released (finally block on close())")

rg = resource_generator()
print(f"First value: {next(rg)}")
rg.close()   # triggers GeneratorExit inside the generator, runs its finally block


# ---------------------------------------------------------------------------
section("throw(): injecting an exception INTO a paused generator")
# ---------------------------------------------------------------------------
def error_aware_generator():
    try:
        yield "first"
        yield "second"
    except ValueError as e:
        print(f"  [gen] caught injected error: {e}")
        yield "recovered"

eg = error_aware_generator()
print(f"First: {next(eg)}")
print(f"After throw(): {eg.throw(ValueError('injected problem'))}")
