import time
from dataclasses import dataclass
from threading import Lock


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_in_seconds: int


class InMemoryFixedWindowLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self._limit = limit
        self._window_seconds = window_seconds
        self._lock = Lock()
        self._buckets: dict[str, tuple[int, int]] = {}

    def check(self, key: str) -> RateLimitResult:
        now = int(time.time())
        window_start = now - (now % self._window_seconds)

        with self._lock:
            count, start = self._buckets.get(key, (0, window_start))
            if start != window_start:
                count, start = 0, window_start
            if count >= self._limit:
                reset_in = (start + self._window_seconds) - now
                return RateLimitResult(False, 0, max(reset_in, 0))

            count += 1
            self._buckets[key] = (count, start)
            remaining = max(self._limit - count, 0)
            reset_in = (start + self._window_seconds) - now
            return RateLimitResult(True, remaining, max(reset_in, 0))

