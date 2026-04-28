"""
Health Check Endpoint for EvoAgentX

Provides system health status for Docker, Kubernetes, and monitoring.

Usage:
    GET /health           -> Basic health check
    GET /health/detailed  -> Full system status
"""

import time
from datetime import datetime
from typing import Any


class HealthChecker:
    """System health checker for medical API connectivity and dependencies."""

    def __init__(self):
        self.start_time = time.time()

    def basic(self) -> dict[str, Any]:
        """Basic health check (always returns 200 if process alive)."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": int(time.time() - self.start_time),
        }

    def detailed(self) -> dict[str, Any]:
        """Detailed health check with dependency verification."""
        import urllib.request

        checks = {}

        # Medical API connectivity
        apis = {
            "pubmed": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed&retmode=json",
            "clinicaltrials": "https://clinicaltrials.gov/api/v2/studies?pageSize=1",
            "openfda": "https://api.fda.gov/drug/label.json?limit=1",
            "rxnorm": "https://rxnav.nlm.nih.gov/REST/drugs.json?name=aspirin",
        }

        for name, url in apis.items():
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "EvoAgentX/0.1"})
                start = time.time()
                with urllib.request.urlopen(req, timeout=10) as resp:
                    latency = (time.time() - start) * 1000
                    checks[name] = {
                        "status": "ok",
                        "latency_ms": round(latency, 1),
                        "status_code": resp.status,
                    }
            except Exception as e:
                checks[name] = {
                    "status": "error",
                    "error": str(e)[:100],
                }

        # Tool imports
        tool_checks = {}
        tools = [
            ("pubmed_tool", "evoagentx.tools.pubmed_tool", "PubMedSearchTool"),
            ("clinicaltrials_tool", "evoagentx.tools.clinicaltrials_tool", "ClinicalTrialsSearchTool"),
            ("drugbank_tool", "evoagentx.tools.drugbank_tool", "DrugSearchTool"),
            ("bridge", "evoagentx.bridge", "EvoXBridge"),
        ]
        for name, module, cls_name in tools:
            try:
                import importlib
                mod = importlib.import_module(module)
                getattr(mod, cls_name)
                tool_checks[name] = "ok"
            except Exception as e:
                tool_checks[name] = f"error: {e}"

        # Overall status
        all_ok = all(
            c.get("status") == "ok" if isinstance(c, dict) else c == "ok"
            for c in {**checks, **tool_checks}.values()
        )

        return {
            "status": "healthy" if all_ok else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": int(time.time() - self.start_time),
            "version": "0.1.0-medical",
            "apis": checks,
            "tools": tool_checks,
        }


# Global instance
_health = HealthChecker()


def get_health() -> dict[str, Any]:
    """Get basic health status."""
    return _health.basic()


def get_detailed_health() -> dict[str, Any]:
    """Get detailed health status."""
    return _health.detailed()
