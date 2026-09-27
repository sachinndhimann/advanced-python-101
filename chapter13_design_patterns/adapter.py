"""
Chapter 13 — Adapter Pattern.
Problem: an existing interface doesn't match what your code expects,
and you can't (or shouldn't) modify the existing thing.
"""


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


section("Why the naive approach fails")

class LegacyXmlLogger:
    """Third-party or legacy code -- you can't/shouldn't edit its interface."""
    def write_entry(self, xml_fragment: str) -> None:
        print(f"  [LegacyXmlLogger] {xml_fragment}")

class ModernLoggerInterface:
    """Your application's code expects THIS shape everywhere."""
    def log(self, level: str, message: str) -> None:
        raise NotImplementedError

def do_work(logger: ModernLoggerInterface):
    logger.log("INFO", "work started")

try:
    do_work(LegacyXmlLogger())   # wrong interface entirely -- no .log() method
except AttributeError as e:
    print(f"  Fails outright: {e}")
print("Problem: LegacyXmlLogger's interface doesn't match what our code expects,")
print("and we can't/shouldn't rewrite the legacy/third-party class itself.")


section("Adapter: wrap the incompatible interface")

class XmlLoggerAdapter(ModernLoggerInterface):
    """Wraps LegacyXmlLogger, translating calls into its actual shape.
    Our application code only ever talks to ModernLoggerInterface."""
    def __init__(self, legacy_logger: LegacyXmlLogger):
        self._legacy = legacy_logger

    def log(self, level: str, message: str) -> None:
        xml = f"<log level='{level}'>{message}</log>"
        self._legacy.write_entry(xml)

adapted_logger = XmlLoggerAdapter(LegacyXmlLogger())
do_work(adapted_logger)   # do_work() is completely unaware anything was adapted


section("Trade-offs")
print("One extra class per adapted interface. Worth it when you genuinely")
print("can't change the wrapped thing (third-party lib, legacy system) --")
print("if you own both sides, it's usually simpler to just fix the interface")
print("directly instead of adapting around it forever.")

section("Real-world use")
print("Python's `contextlib.suppress`-style wrapping, ORM adapters that make")
print("different databases look the same to your app code, and wrapping a")
print("synchronous library to present an async-looking interface.")
