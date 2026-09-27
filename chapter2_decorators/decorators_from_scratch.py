"""
Chapter 2 — decorators built up from first principles: functions as
objects, closures, a manual decorator, functools.wraps, decorators with
arguments, and class-based decorators.
"""
import functools


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("Functions are objects")
# ---------------------------------------------------------------------------
def greet():
    return "hello"

# A function can be assigned to a variable, passed around, stored in a list.
say_hi = greet
functions = [greet, say_hi]
print(f"say_hi() = {say_hi()}")
print(f"greet is say_hi: {greet is say_hi}")   # same object, two names


# ---------------------------------------------------------------------------
section("Functions can return functions: closures")
# ---------------------------------------------------------------------------
def make_multiplier(factor):
    def multiply(x):
        return x * factor   # `factor` is remembered from the enclosing scope
    return multiply

times3 = make_multiplier(3)
times5 = make_multiplier(5)
print(f"times3(10) = {times3(10)}, times5(10) = {times5(10)}")
# Each call to make_multiplier creates a NEW closure with its own `factor`.
print(f"times3.__closure__[0].cell_contents = {times3.__closure__[0].cell_contents}")


# ---------------------------------------------------------------------------
section("A manual decorator: a function that wraps a function")
# ---------------------------------------------------------------------------
def loud(func):
    def wrapper(*args, **kwargs):
        print(f"[loud] about to call {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[loud] {func.__name__} returned {result!r}")
        return result
    return wrapper

def add(a, b):
    return a + b

add = loud(add)          # this is what @loud does automatically
print(add(2, 3))


# ---------------------------------------------------------------------------
section("@decorator syntax is exactly this")
# ---------------------------------------------------------------------------
@loud
def subtract(a, b):
    return a - b
# The line above is EXACTLY: def subtract(a,b): ...; subtract = loud(subtract)

print(subtract(10, 4))


# ---------------------------------------------------------------------------
section("Without functools.wraps: identity is lost")
# ---------------------------------------------------------------------------
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def documented_function():
    """This docstring should survive decoration."""
    return 42

print(f"Name without wraps: {documented_function.__name__}")     # 'wrapper' -- wrong!
print(f"Docstring without wraps: {documented_function.__doc__}")  # None -- lost!


# ---------------------------------------------------------------------------
section("With functools.wraps: identity is preserved")
# ---------------------------------------------------------------------------
def good_decorator(func):
    @functools.wraps(func)          # copies __name__, __doc__, etc. onto wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@good_decorator
def documented_function_v2():
    """This docstring survives decoration."""
    return 42

print(f"Name with wraps: {documented_function_v2.__name__}")      # correct
print(f"Docstring with wraps: {documented_function_v2.__doc__}")   # correct


# ---------------------------------------------------------------------------
section("Decorators with arguments: an extra layer of function nesting")
# ---------------------------------------------------------------------------
def repeat(times):
    """This is a DECORATOR FACTORY: a function that returns a decorator."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(times=3)
def roll_die():
    import random
    return random.randint(1, 6)

print(f"repeat(times=3) results: {roll_die()}")
# Expansion: roll_die = repeat(times=3)(roll_die)
#            repeat(times=3) returns `decorator`
#            decorator(roll_die) returns `wrapper`


# ---------------------------------------------------------------------------
section("Class-based decorators: __call__ makes an object callable")
# ---------------------------------------------------------------------------
class CountCalls:
    """A decorator implemented as a class instead of a function. Useful
    when the decorator needs to hold state across calls cleanly."""
    def __init__(self, func):
        functools.update_wrapper(self, func)   # class-version of @wraps
        self.func = func
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        print(f"[CountCalls] {self.func.__name__} called {self.call_count} time(s)")
        return self.func(*args, **kwargs)

@CountCalls
def ping():
    return "pong"

ping()
ping()
print(f"Total calls tracked on the decorator object: {ping.call_count}")
