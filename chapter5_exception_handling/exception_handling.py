"""
Chapter 5 — exception handling as an engineering discipline: hierarchy,
chaining, retryable-vs-not, bad-vs-good, and a small robust strategy.
"""
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("try / except / else / finally")
# ---------------------------------------------------------------------------
def divide_safely(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("  [except] division by zero")
        return None
    else:
        print("  [else] no exception occurred, result is valid")
        return result
    finally:
        print("  [finally] always runs, exception or not")

print("divide_safely(10, 2):", divide_safely(10, 2))
print("divide_safely(10, 0):", divide_safely(10, 0))


# ---------------------------------------------------------------------------
section("A domain exception hierarchy")
# ---------------------------------------------------------------------------
class AppError(Exception):
    """Base for ALL of this application's own exceptions. Callers who
    want to catch 'anything our app raises on purpose' catch this."""

class RetryableError(AppError):
    """Base for errors worth retrying (transient, likely to succeed later)."""

class NonRetryableError(AppError):
    """Base for errors NOT worth retrying (the input/state is simply wrong)."""

class InventoryUnavailableError(RetryableError):
    """Stock check failed transiently -- worth a retry."""

class InvalidOrderError(NonRetryableError):
    """The order itself is malformed -- retrying changes nothing."""

class PaymentDeclinedError(NonRetryableError):
    """Card declined -- retrying the SAME payment won't help."""


# ---------------------------------------------------------------------------
section("Exception chaining: preserve the original cause")
# ---------------------------------------------------------------------------
def check_inventory(sku):
    raise ConnectionError("inventory service timed out")   # a LOW-LEVEL error

def process_order(sku, qty):
    try:
        check_inventory(sku)
    except ConnectionError as original_error:
        # Transform a low-level error into a domain-meaningful one,
        # WITHOUT losing the original cause (`from original_error`).
        raise InventoryUnavailableError(
            f"Could not verify inventory for {sku}"
        ) from original_error

try:
    process_order("SKU-123", 2)
except InventoryUnavailableError as e:
    print(f"Caught domain error: {e}")
    print(f"Original cause preserved: {e.__cause__!r}")


# ---------------------------------------------------------------------------
section("Retryable vs non-retryable: callers can branch on the TYPE")
# ---------------------------------------------------------------------------
def attempt_order(order_valid: bool, inventory_ok: bool):
    if not order_valid:
        raise InvalidOrderError("order failed schema validation")
    if not inventory_ok:
        raise InventoryUnavailableError("inventory check timed out")
    return "order placed"

def handle_order_with_retry(order_valid, inventory_ok, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            return attempt_order(order_valid, inventory_ok)
        except RetryableError as e:
            logger.info(f"Attempt {attempt}: retryable failure ({e}), will retry")
            if attempt == max_attempts:
                logger.error(f"Exhausted retries: {e}")
                raise
        except NonRetryableError as e:
            logger.error(f"Non-retryable failure, aborting immediately: {e}")
            raise   # no point retrying -- propagate right away

print("\n-- Retryable path (fails every time, exhausts retries) --")
try:
    handle_order_with_retry(order_valid=True, inventory_ok=False)
except InventoryUnavailableError:
    print("Caller sees: order ultimately failed after retries")

print("\n-- Non-retryable path (fails fast, no wasted retries) --")
try:
    handle_order_with_retry(order_valid=False, inventory_ok=True)
except InvalidOrderError:
    print("Caller sees: order failed immediately, no retries wasted")


# ---------------------------------------------------------------------------
section("Bad vs good: why 'except Exception: pass' is dangerous")
# ---------------------------------------------------------------------------
def bad_handler():
    try:
        data = {"a": 1}
        # A TYPO bug: 'b' doesn't exist. This is NOT the error we meant to guard against.
        return data["b"]
    except Exception:
        pass   # the KeyError from our typo silently vanishes -- no log, no trace

result = bad_handler()
print(f"bad_handler() returned {result!r} -- the bug is completely invisible")

def good_handler():
    try:
        data = {"a": 1}
        return data["b"]
    except KeyError as e:
        # Catch the SPECIFIC error you anticipated, log it, decide explicitly.
        logger.warning(f"Expected key missing, using default: {e}")
        return None
    # Anything else (a real bug, e.g. AttributeError from a typo elsewhere)
    # is NOT caught here, and will surface loudly, as it should.

result = good_handler()
print(f"good_handler() returned {result!r} -- and a warning was LOGGED, not hidden")


# ---------------------------------------------------------------------------
section("A robust error-handling strategy, end to end")
# ---------------------------------------------------------------------------
def place_order(order_valid: bool, inventory_ok: bool) -> str:
    """The pattern real services use: catch at the boundary, log with
    context, decide recover/fail based on exception TYPE, never swallow
    silently."""
    try:
        return handle_order_with_retry(order_valid, inventory_ok)
    except RetryableError as e:
        logger.error(f"Order failed after retries: {e}")
        return "FAILED: please try again later"
    except NonRetryableError as e:
        logger.error(f"Order rejected: {e}")
        return f"FAILED: {e}"
    except AppError as e:
        # Catches anything else from OUR app we didn't specifically anticipate.
        logger.error(f"Unexpected application error: {e}")
        return "FAILED: unexpected error"
    # Deliberately NOT catching bare Exception here -- a truly unexpected
    # bug (not one of our domain errors) should propagate and be loud.

print("\nFinal strategy in action:")
print(" ", place_order(order_valid=True, inventory_ok=True))
print(" ", place_order(order_valid=False, inventory_ok=True))
print(" ", place_order(order_valid=True, inventory_ok=False))
