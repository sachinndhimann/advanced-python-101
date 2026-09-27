"""
Chapter 10 — a production-style logging setup: console + rotating file
handlers, structured JSON output, contextual fields, correlation IDs,
and proper exception logging.
"""
import json
import logging
import logging.handlers
import os
import uuid


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("print() vs logging: why print doesn't scale")
# ---------------------------------------------------------------------------
print("print('user logged in')  -- no level, no routing, no structure, always fires")
print("logger.info('user logged in')  -- has a level, can be routed, can be silenced")


# ---------------------------------------------------------------------------
section("Structured JSON formatter")
# ---------------------------------------------------------------------------
class JsonFormatter(logging.Formatter):
    """Emits each log record as one JSON object per line -- easy for log
    aggregation tools to parse and query by field."""
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Include any extra fields attached via extra={...}
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord("", 0, "", 0, "", (), None).__dict__ and key != "message":
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


# ---------------------------------------------------------------------------
section("Building the logger: console + rotating file handler")
# ---------------------------------------------------------------------------
LOG_FILE = os.path.join(os.path.dirname(__file__), "app.log")

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)          # logger itself allows everything through
logger.handlers.clear()                 # avoid duplicate handlers if rerun

# Console handler: human-readable, WARNING and above only
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(logging.Formatter("%(levelname)s | %(name)s | %(message)s"))

# Rotating file handler: everything INFO and above, structured JSON,
# capped size with backups (a real production pattern to bound disk usage)
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=5000, backupCount=3
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(JsonFormatter())

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.debug("This DEBUG line is dropped by both handlers (below their thresholds)")
logger.info("This INFO line goes to the file only (console requires WARNING+)")
logger.warning("This WARNING line goes to BOTH console and file")
logger.error("This ERROR line goes to BOTH console and file")


# ---------------------------------------------------------------------------
section("Contextual information via extra={}")
# ---------------------------------------------------------------------------
logger.info("Order placed", extra={"order_id": 4821, "user_id": "sachin"})
logger.warning("Inventory low", extra={"sku": "SKU-123", "remaining": 2})


# ---------------------------------------------------------------------------
section("Correlation IDs: tracing one request across many log lines")
# ---------------------------------------------------------------------------
class CorrelationAdapter(logging.LoggerAdapter):
    """Wraps a logger so every call automatically includes the same
    correlation_id, without repeating extra={...} at every call site."""
    def process(self, msg, kwargs):
        kwargs.setdefault("extra", {})
        kwargs["extra"]["correlation_id"] = self.extra["correlation_id"]
        return msg, kwargs


def handle_request():
    correlation_id = str(uuid.uuid4())[:8]
    request_logger = CorrelationAdapter(logger, {"correlation_id": correlation_id})

    request_logger.info("Request received")
    request_logger.info("Validating input")
    request_logger.warning("Input required a default fallback")
    request_logger.info("Request completed")
    return correlation_id

cid = handle_request()
print(f"\n  (Simulated request used correlation_id={cid} -- check app.log to see")
print(f"   every line from this request tagged with the SAME id, even interleaved")
print(f"   with other concurrent requests in a real system.)")


# ---------------------------------------------------------------------------
section("Exception logging: capture the full traceback")
# ---------------------------------------------------------------------------
def risky_operation():
    return 1 / 0

try:
    risky_operation()
except ZeroDivisionError:
    logger.exception("risky_operation failed")   # automatically includes traceback

print(f"\nCheck '{LOG_FILE}' for the full structured JSON output, including the")
print("exception traceback captured by logger.exception(...).")
