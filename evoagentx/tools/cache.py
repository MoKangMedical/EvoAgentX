"""
Medical API Cache Layer

Caches responses from PubMed, ClinicalTrials.gov, OpenFDA, and RxNorm
to reduce API calls and improve performance.

Features:
- TTL-based cache (configurable per API)
- File-based persistence (survives restarts)
- Thread-safe operations
- Cache statistics

Usage:
    from evoagentx.tools.cache import MedicalCache
    cache = MedicalCache()
    result = cache.get_or_fetch("pubmed", "cancer therapy", fetch_fn)
"""

import hashlib
import json
import os
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any


class MedicalCache:
    """
    Thread-safe cache for medical API responses.

    Default TTLs (seconds):
    - PubMed: 3600 (1 hour) - literature updates daily
    - ClinicalTrials: 1800 (30 min) - trial status changes
    - OpenFDA: 86400 (24 hours) - labels rarely change
    - RxNorm: 604800 (7 days) - drug names are stable
    """

    DEFAULT_TTLS = {
        "pubmed": 3600,
        "clinicaltrials": 1800,
        "openfda": 86400,
        "rxnorm": 604800,
        "default": 3600,
    }

    def __init__(self, cache_dir: str | None = None, default_ttl: int = 3600):
        self.cache_dir = Path(cache_dir or os.path.expanduser("~/.evoagentx/cache"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self._memory_cache: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._stats = {"hits": 0, "misses": 0, "saves": 0}

    def _make_key(self, api: str, query: str) -> str:
        """Generate cache key from API name and query."""
        raw = f"{api}:{query}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _get_ttl(self, api: str) -> int:
        """Get TTL for an API."""
        return self.DEFAULT_TTLS.get(api, self.default_ttl)

    def get(self, api: str, query: str) -> Any | None:
        """Get cached result if available and not expired."""
        key = self._make_key(api, query)

        # Check memory cache first
        with self._lock:
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                if time.time() < entry["expires"]:
                    self._stats["hits"] += 1
                    return entry["data"]
                else:
                    del self._memory_cache[key]

        # Check file cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    entry = json.load(f)
                if time.time() < entry["expires"]:
                    # Load into memory cache
                    with self._lock:
                        self._memory_cache[key] = entry
                        self._stats["hits"] += 1
                    return entry["data"]
                else:
                    cache_file.unlink(missing_ok=True)
            except (json.JSONDecodeError, KeyError):
                cache_file.unlink(missing_ok=True)

        with self._lock:
            self._stats["misses"] += 1
        return None

    def set(self, api: str, query: str, data: Any, ttl: int | None = None):
        """Cache a result."""
        key = self._make_key(api, query)
        expires = time.time() + (ttl or self._get_ttl(api))

        entry = {
            "api": api,
            "query": query,
            "data": data,
            "expires": expires,
            "cached_at": time.time(),
        }

        # Save to memory
        with self._lock:
            self._memory_cache[key] = entry
            self._stats["saves"] += 1

        # Save to file
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(entry, f, ensure_ascii=False)
        except Exception:
            pass  # Non-critical failure

    def get_or_fetch(self, api: str, query: str, fetch_fn: Callable,
                     ttl: int | None = None) -> Any:
        """Get from cache or fetch and cache."""
        cached = self.get(api, query)
        if cached is not None:
            return cached

        result = fetch_fn()
        self.set(api, query, result, ttl)
        return result

    def invalidate(self, api: str, query: str):
        """Remove a specific cache entry."""
        key = self._make_key(api, query)
        with self._lock:
            self._memory_cache.pop(key, None)
        cache_file = self.cache_dir / f"{key}.json"
        cache_file.unlink(missing_ok=True)

    def clear(self):
        """Clear all cache."""
        with self._lock:
            self._memory_cache.clear()
        for f in self.cache_dir.glob("*.json"):
            f.unlink(missing_ok=True)

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total if total > 0 else 0
            return {
                **self._stats,
                "total_requests": total,
                "hit_rate": f"{hit_rate:.1%}",
                "memory_entries": len(self._memory_cache),
                "disk_entries": len(list(self.cache_dir.glob("*.json"))),
            }

    def cleanup(self):
        """Remove expired entries."""
        removed = 0
        for f in self.cache_dir.glob("*.json"):
            try:
                with open(f) as fh:
                    entry = json.load(fh)
                if time.time() >= entry.get("expires", 0):
                    f.unlink()
                    removed += 1
            except Exception:
                f.unlink()
                removed += 1
        return removed


# Global cache instance
_global_cache: MedicalCache | None = None


def get_cache() -> MedicalCache:
    """Get or create the global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = MedicalCache()
    return _global_cache
