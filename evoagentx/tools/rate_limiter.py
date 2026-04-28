"""
Rate Limiter for Medical APIs

Enforces per-API rate limits to comply with NCBI, ClinicalTrials.gov,
OpenFDA, and RxNorm usage policies.

Usage:
    from evoagentx.tools.rate_limiter import get_limiter
    limiter = get_limiter()
    limiter.wait("pubmed")  # Blocks until safe to make request
"""

import threading
import time
from collections import deque


class RateLimiter:
    """
    Token bucket rate limiter with per-API configuration.

    Default limits:
    - PubMed: 3 req/s (without key), 10 req/s (with key)
    - ClinicalTrials.gov: 10 req/s
    - OpenFDA: 4 req/s (240/min without key)
    - RxNorm: 5 req/s (conservative)
    """

    DEFAULT_LIMITS = {
        "pubmed": {"rate": 3, "per": 1.0},
        "clinicaltrials": {"rate": 10, "per": 1.0},
        "openfda": {"rate": 4, "per": 1.0},
        "rxnorm": {"rate": 5, "per": 1.0},
    }

    def __init__(self):
        self._buckets: dict[str, deque] = {}
        self._lock = threading.Lock()
        self._stats: dict[str, int] = {}

    def wait(self, api: str, timeout: float = 30.0):
        """Wait until it's safe to make a request to the given API."""
        config = self.DEFAULT_LIMITS.get(api, {"rate": 5, "per": 1.0})
        rate = config["rate"]
        per = config["per"]

        with self._lock:
            if api not in self._buckets:
                self._buckets[api] = deque()
                self._stats[api] = 0

            bucket = self._buckets[api]
            now = time.time()

            # Remove old timestamps outside the window
            while bucket and bucket[0] < now - per:
                bucket.popleft()

            # If at capacity, wait
            if len(bucket) >= rate:
                wait_time = bucket[0] + per - now
                if wait_time > 0:
                    if wait_time > timeout:
                        raise TimeoutError(
                            f"Rate limit wait ({wait_time:.1f}s) exceeds timeout ({timeout}s)"
                        )
                    # Release lock while waiting
                    self._lock.release()
                    try:
                        time.sleep(wait_time)
                    finally:
                        self._lock.acquire()
                    # Clean up again after waiting
                    now = time.time()
                    while bucket and bucket[0] < now - per:
                        bucket.popleft()

            bucket.append(time.time())
            self._stats[api] = self._stats.get(api, 0) + 1

    def get_stats(self) -> dict[str, int]:
        """Get request counts per API."""
        with self._lock:
            return dict(self._stats)


# Global instance
_global_limiter: RateLimiter | None = None


def get_limiter() -> RateLimiter:
    """Get or create the global rate limiter."""
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = RateLimiter()
    return _global_limiter
