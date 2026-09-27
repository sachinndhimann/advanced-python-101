"""
Chapter 2 — practical decorators built from scratch: @timer, @logger,
@retry, @validate, @cache. Each is a real, usable pattern, not a toy.
"""
import functools
import time


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("@timer")
# ---------------------------------------------------------------------------
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer] {func.__name__} took {elapsed*1000:.3f} ms")
        return result
    return wrapper

@timer
def slow_computation(n):
    return sum(i * i for i in range(n))

slow_computation(1_000_000)


# ---------------------------------------------------------------------------
section("@logger")
# ---------------------------------------------------------------------------
def logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        arg_str = ", ".join([repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()])
        print(f"[logger] CALL {func.__name__}({arg_str})")
        try:
            result = func(*args, **kwargs)
            print(f"[logger] RETURN {func.__name__} -> {result!r}")
            return result
        except Exception as e:
            print(f"[logger] EXCEPTION in {func.__name__}: {e!r}")
            raise
    return wrapper

@logger
def divide(a, b):
    return a / b

divide(10, 2)
try:
    divide(10, 0)
except ZeroDivisionError:
    print("[demo] caught the re-raised exception outside the decorator")


# ---------------------------------------------------------------------------
section("@retry")
# ---------------------------------------------------------------------------
def retry(max_attempts=3, delay_seconds=0.0):
    """Decorator FACTORY: takes config, returns the actual decorator."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"[retry] attempt {attempt}/{max_attempts} failed: {e}")
                    if attempt < max_attempts and delay_seconds:
                        time.sleep(delay_seconds)
            raise last_exception   # exhausted retries: propagate the last error
        return wrapper
    return decorator

_flaky_state = {"calls": 0}

@retry(max_attempts=3)
def flaky_operation():
    _flaky_state["calls"] += 1
    if _flaky_state["calls"] < 3:
        raise ConnectionError("simulated transient failure")
    return "success"

print(f"flaky_operation() -> {flaky_operation()}")


# ---------------------------------------------------------------------------
section("@validate")
# ---------------------------------------------------------------------------
def validate(**validators):
    """@validate(a=lambda x: x > 0, b=lambda x: x != 0) -- validate specific
    named arguments before the function body ever runs."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import inspect
            bound = inspect.signature(func).bind(*args, **kwargs)
            bound.apply_defaults()
            for name, check in validators.items():
                value = bound.arguments.get(name)
                if not check(value):
                    raise ValueError(f"Validation failed for argument '{name}={value!r}'")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate(a=lambda x: x > 0, b=lambda x: x != 0)
def safe_divide(a, b):
    return a / b

print(f"safe_divide(10, 2) = {safe_divide(10, 2)}")
try:
    safe_divide(10, 0)
except ValueError as e:
    print(f"Caught: {e}")


# ---------------------------------------------------------------------------
section("@cache (built manually -- functools.lru_cache does this for real use)")
# ---------------------------------------------------------------------------
def cache(func):
    stored_results = {}
    @functools.wraps(func)
    def wrapper(*args):
        if args in stored_results:
            print(f"[cache] HIT for {args}")
            return stored_results[args]
        print(f"[cache] MISS for {args}, computing...")
        result = func(*args)
        stored_results[args] = result
        return result
    return wrapper

@cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(f"fibonacci(10) = {fibonacci(10)}")
print(f"fibonacci(10) again (should be a cache hit): {fibonacci(10)}")


# ---------------------------------------------------------------------------
section("Stacking decorators: order matters")
# ---------------------------------------------------------------------------
@timer
@logger
def stacked_example(x):
    return x * 2

# Expansion: stacked_example = timer(logger(stacked_example))
# So logger's wrapper runs INSIDE timer's wrapper: timer starts the clock,
# then calls logger's wrapper, which logs, then calls the real function.
stacked_example(21)
