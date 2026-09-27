"""
Chapter 13 — Builder Pattern.
Problem: constructing a complex object needs many optional pieces
assembled step by step -- a single giant constructor call becomes
unreadable and error-prone (especially with many same-typed arguments).
"""


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


section("Why the naive approach fails")

class HttpRequestBad:
    def __init__(self, url, method="GET", headers=None, body=None,
                 timeout=30, retries=3, verify_ssl=True, follow_redirects=True):
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.body = body
        self.timeout = timeout
        self.retries = retries
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects

# Easy to pass arguments in the wrong ORDER or forget which positional
# slot means what, especially with several same-typed (bool/int) params.
req_bad = HttpRequestBad("https://api.example.com", "POST", None, '{"a":1}', 60, 5, False, True)
print(f"  Constructed, but which argument was which? {req_bad.timeout=}, {req_bad.retries=}, {req_bad.verify_ssl=}")
print("Problem: a long positional constructor call is unreadable and a")
print("single misordered argument silently produces a wrong, valid-looking object.")


section("Builder: assemble step by step, named and readable")

class HttpRequest:
    def __init__(self):
        self.url = None
        self.method = "GET"
        self.headers = {}
        self.body = None
        self.timeout = 30
        self.retries = 3
        self.verify_ssl = True

class HttpRequestBuilder:
    """Each method returns self, enabling a readable fluent chain.
    Nothing is 'finalized' until .build() is called."""
    def __init__(self):
        self._request = HttpRequest()

    def url(self, url: str) -> "HttpRequestBuilder":
        self._request.url = url
        return self

    def method(self, method: str) -> "HttpRequestBuilder":
        self._request.method = method
        return self

    def header(self, key: str, value: str) -> "HttpRequestBuilder":
        self._request.headers[key] = value
        return self

    def body(self, body: str) -> "HttpRequestBuilder":
        self._request.body = body
        return self

    def timeout(self, seconds: int) -> "HttpRequestBuilder":
        self._request.timeout = seconds
        return self

    def no_ssl_verification(self) -> "HttpRequestBuilder":
        self._request.verify_ssl = False
        return self

    def build(self) -> HttpRequest:
        if not self._request.url:
            raise ValueError("A request must have a url")
        return self._request

request = (
    HttpRequestBuilder()
    .url("https://api.example.com")
    .method("POST")
    .header("Content-Type", "application/json")
    .body('{"a":1}')
    .timeout(60)
    .no_ssl_verification()
    .build()
)
print(f"  Built request: method={request.method}, timeout={request.timeout}, "
      f"verify_ssl={request.verify_ssl}, headers={request.headers}")
print("  Every field is set by NAME -- impossible to misorder or confuse.")


section("Trade-offs")
print("A builder class plus a fluent chain is more code than one")
print("constructor call. Worth it for objects with MANY optional fields")
print("(especially several of the same type); overkill for a class with")
print("2-3 obviously-ordered required parameters.")

section("Real-world use")
print("requests.Session() configuration, SQLAlchemy's query building")
print("(.filter().order_by().limit()), and most HTTP client / query")
print("builder libraries use exactly this fluent pattern.")
