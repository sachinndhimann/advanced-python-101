"""
Chapter 11 — modern Python typing constructs. Runs fine with plain
python3 (hints are NOT enforced at runtime) -- run `mypy` on this file
separately to see static checking catch intentional errors.
"""
from typing import (
    Optional, Union, Any, Callable, TypeVar, Generic, Protocol,
    TypedDict, Literal, Final, overload, TypeAlias,
)


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("Basic hints")
# ---------------------------------------------------------------------------
def add(a: int, b: int) -> int:
    return a + b

def get_names() -> list[str]:
    return ["Sachin", "Alex"]

def word_counts() -> dict[str, int]:
    return {"hello": 1, "world": 2}

def coordinates() -> tuple[float, float]:
    return (12.9, 77.6)

print(f"add(2, 3) = {add(2, 3)}")
print(f"get_names() = {get_names()}")
print("(Hints above are NOT enforced -- add('x', 'y') would still run and")
print(" return 'xy' at runtime; only a type checker would flag it.)")


# ---------------------------------------------------------------------------
section("Optional and Union")
# ---------------------------------------------------------------------------
def find_user(user_id: int) -> Optional[str]:
    """Optional[str] means: returns a str, OR None."""
    users = {1: "Sachin"}
    return users.get(user_id)

def parse_id(raw: Union[str, int]) -> int:
    """Union[str, int] means: accepts EITHER type."""
    return int(raw)

# Modern syntax (Python 3.10+), equivalent to the above:
def parse_id_modern(raw: str | int) -> int:
    return int(raw)

print(f"find_user(1) = {find_user(1)!r}, find_user(99) = {find_user(99)!r}")
print(f"parse_id('42') = {parse_id('42')}, parse_id(42) = {parse_id(42)}")


# ---------------------------------------------------------------------------
section("Any: opting out of checking (use sparingly)")
# ---------------------------------------------------------------------------
def process_anything(data: Any) -> Any:
    """Any tells the checker 'don't verify this spot at all'. It's an
    escape hatch for genuinely dynamic data (e.g. raw JSON before
    validation) -- not a substitute for real typing where you CAN be specific."""
    return data

print(f"process_anything(42) = {process_anything(42)}")
print(f"process_anything('x') = {process_anything('x')}")


# ---------------------------------------------------------------------------
section("Callable: typing a function-as-value")
# ---------------------------------------------------------------------------
def apply_twice(fn: Callable[[int], int], value: int) -> int:
    return fn(fn(value))

print(f"apply_twice(lambda x: x + 3, 10) = {apply_twice(lambda x: x + 3, 10)}")


# ---------------------------------------------------------------------------
section("TypeAlias: name a complex type once")
# ---------------------------------------------------------------------------
UserRecord: TypeAlias = dict[str, Union[str, int, bool]]

def format_user(user: UserRecord) -> str:
    return f"{user['name']} ({user['age']})"

print(format_user({"name": "Sachin", "age": 30, "active": True}))


# ---------------------------------------------------------------------------
section("Generic / TypeVar: one class, many types, type preserved")
# ---------------------------------------------------------------------------
T = TypeVar("T")

class Stack(Generic[T]):
    """Stack[int] only ever pushes/pops int; Stack[str] only str. The
    type checker tracks WHICH one you're using per-instance."""
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
print(f"int_stack.pop() = {int_stack.pop()}")
# A type checker would flag int_stack.push("oops") as an error here --
# this file still RUNS it fine at runtime, which is exactly the point.


# ---------------------------------------------------------------------------
section("Protocol: structural typing for the checker")
# ---------------------------------------------------------------------------
class SupportsArea(Protocol):
    def area(self) -> float: ...

class Circle:
    def __init__(self, radius: float):
        self.radius = radius
    def area(self) -> float:
        return 3.14159 * self.radius ** 2

class Square:
    def __init__(self, side: float):
        self.side = side
    def area(self) -> float:
        return self.side ** 2

def total_area(shapes: list[SupportsArea]) -> float:
    return sum(s.area() for s in shapes)

print(f"total_area([Circle(2), Square(3)]) = {total_area([Circle(2), Square(3)]):.2f}")


# ---------------------------------------------------------------------------
section("TypedDict: a dict with a known, fixed shape")
# ---------------------------------------------------------------------------
class ApiResponse(TypedDict):
    status: int
    message: str
    data: list[int]

def handle_response(response: ApiResponse) -> None:
    print(f"  status={response['status']}, message={response['message']}, data={response['data']}")

handle_response({"status": 200, "message": "ok", "data": [1, 2, 3]})


# ---------------------------------------------------------------------------
section("Literal: restrict to specific values")
# ---------------------------------------------------------------------------
def sort_items(items: list[int], direction: Literal["asc", "desc"] = "asc") -> list[int]:
    return sorted(items, reverse=(direction == "desc"))

print(f"sort_items([3,1,2], 'desc') = {sort_items([3, 1, 2], 'desc')}")
# A type checker would flag sort_items([1,2], "sideways") -- not a valid Literal value.


# ---------------------------------------------------------------------------
section("Final: a value that must not be reassigned (checker-enforced)")
# ---------------------------------------------------------------------------
MAX_RETRIES: Final = 3
print(f"MAX_RETRIES = {MAX_RETRIES}")
# A type checker flags `MAX_RETRIES = 5` anywhere else in the file as an error;
# Python itself does NOT prevent the reassignment at runtime.


# ---------------------------------------------------------------------------
section("@overload: multiple valid signatures for one function")
# ---------------------------------------------------------------------------
@overload
def to_list(value: int) -> list[int]: ...
@overload
def to_list(value: str) -> list[str]: ...

def to_list(value):
    """The @overload stubs above are ONLY for the type checker; this real
    implementation below is what actually runs."""
    if isinstance(value, int):
        return list(range(value))
    return list(value)

print(f"to_list(5) = {to_list(5)}")
print(f"to_list('abc') = {to_list('abc')}")
