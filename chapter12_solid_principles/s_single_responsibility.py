"""
Chapter 12 — Single Responsibility Principle.
A class should have ONE reason to change.
"""


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("BAD: one class, multiple reasons to change")
# ---------------------------------------------------------------------------
class OrderBad:
    """This class changes if: pricing rules change, receipt wording
    changes, OR the notification channel changes. Three unrelated
    reasons to touch the SAME class -- a change to email formatting
    risks accidentally breaking discount math nearby."""

    def __init__(self, items: list[float]):
        self.items = items

    def calculate_total(self) -> float:
        return sum(self.items) * 0.9   # 10% discount, hardcoded here

    def format_receipt(self) -> str:
        return f"Receipt: {len(self.items)} items, total ${self.calculate_total():.2f}"

    def send_email_receipt(self, email: str) -> None:
        print(f"  [MOCK EMAIL to {email}]: {self.format_receipt()}")


order = OrderBad([10.0, 20.0, 30.0])
order.send_email_receipt("customer@example.com")
print("Problem: pricing logic, receipt formatting, and email delivery are")
print("all bundled -- changing HOW email is sent risks the pricing code nearby.")


# ---------------------------------------------------------------------------
section("GOOD: split by responsibility")
# ---------------------------------------------------------------------------
class Order:
    """ONLY responsible for order data and pricing."""
    def __init__(self, items: list[float]):
        self.items = items

    def calculate_total(self) -> float:
        return sum(self.items) * 0.9


class ReceiptFormatter:
    """ONLY responsible for turning an Order into readable text."""
    def format(self, order: Order) -> str:
        return f"Receipt: {len(order.items)} items, total ${order.calculate_total():.2f}"


class EmailSender:
    """ONLY responsible for delivering a message somewhere."""
    def send(self, to: str, message: str) -> None:
        print(f"  [MOCK EMAIL to {to}]: {message}")


good_order = Order([10.0, 20.0, 30.0])
formatter = ReceiptFormatter()
sender = EmailSender()
sender.send("customer@example.com", formatter.format(good_order))

print("\nNow: changing email delivery (e.g. switch to SMS) means editing ONLY")
print("EmailSender/a new SmsSender -- Order and ReceiptFormatter are untouched.")


# ---------------------------------------------------------------------------
section("When NOT to over-apply this")
# ---------------------------------------------------------------------------
print("For a one-off script that formats and prints ONE receipt and will")
print("never grow, splitting into 3 classes is pure overhead -- a single")
print("function is more readable and just as correct. SRP earns its cost")
print("when the responsibilities genuinely tend to change independently.")
