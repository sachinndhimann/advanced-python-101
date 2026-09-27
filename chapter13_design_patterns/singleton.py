"""
Chapter 13 — Singleton Pattern.
Problem: some resources genuinely must have exactly ONE instance
application-wide (a config object, a connection pool) -- multiple
instances would mean inconsistent state or wasted resources.

(You touched the __new__ mechanism behind this in Module 1's exercise --
this file shows the complete pattern plus its very real downsides.)
"""


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


section("Why the naive approach fails")

class ConfigBad:
    def __init__(self):
        self.settings = {"debug": False}

c1 = ConfigBad()
c2 = ConfigBad()
c1.settings["debug"] = True
print(f"  c1.settings is c2.settings: {c1.settings is c2.settings}")   # False -- separate!
print(f"  c2.settings: {c2.settings}")   # unaffected by c1's change
print("Problem: two 'the config' objects exist with independent state --")
print("a change through one is invisible to code holding the other.")


section("Singleton via __new__: force exactly one instance")

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.settings = {"debug": False}   # init only once
        return cls._instance

conf1 = Config()
conf2 = Config()
conf1.settings["debug"] = True
print(f"  conf1 is conf2: {conf1 is conf2}")
print(f"  conf2.settings (sees conf1's change): {conf2.settings}")


section("Trade-offs (these are real, not hypothetical)")
print("Singletons introduce GLOBAL mutable state -- the same danger as any")
print("global variable: hidden coupling between unrelated parts of code,")
print("and genuinely hard-to-test code (a test that mutates the singleton")
print("leaks state into the NEXT test unless carefully reset). Many")
print("experienced engineers prefer passing a single shared instance via")
print("Dependency Injection (Chapters 1/12/13) instead of a true Singleton --")
print("same 'one instance' benefit, without the hidden global coupling,")
print("because the instance is explicit in every constructor that needs it.")

section("Real-world use")
print("Logging configuration, a single database connection pool, and")
print("application-wide settings objects are the few places Singleton")
print("(or its DI-based cousin, a shared instance registered once) is")
print("commonly justified.")
