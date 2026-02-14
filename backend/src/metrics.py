"""Prometheus metrics definitions.

All application metrics are defined here for centralized management.
"""

from prometheus_client import Counter, Gauge, Histogram

# --- HTTP metrics ---

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method"],
)

# --- Schedule sync metrics ---

SCHEDULE_SYNC_TOTAL = Counter(
    "schedule_sync_total",
    "Total schedule sync attempts",
    ["status"],
)

SCHEDULE_SYNC_DURATION_SECONDS = Histogram(
    "schedule_sync_duration_seconds",
    "Schedule sync duration in seconds",
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0),
)

# --- App info ---

APP_INFO = Gauge(
    "app_info",
    "Application version info",
    ["version"],
)
