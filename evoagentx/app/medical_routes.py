"""
Medical API Routes for EvoAgentX FastAPI Server

Provides REST endpoints for medical tools, health checks,
and dashboard data.

Endpoints:
  GET  /api/health              - Health check
  GET  /api/health/detailed     - Detailed status
  GET  /api/medical/search      - PubMed search
  GET  /api/medical/trials      - Clinical trials search
  GET  /api/medical/drugs       - Drug search
  GET  /api/medical/interactions - Drug interaction check
  GET  /api/medical/rxnorm      - RxNorm lookup
  GET  /api/medical/stats       - Cache and rate limiter stats
  POST /api/medical/evolve      - Run evolution
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    from fastapi import APIRouter, Query, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

if HAS_FASTAPI:
    router = APIRouter(prefix="/api/medical", tags=["medical"])

    # Lazy imports for tools
    _tools = {}

    def _get_tool(name):
        if name not in _tools:
            try:
                if name == "pubmed":
                    from evoagentx.tools.pubmed_tool import PubMedSearchTool
                    _tools[name] = PubMedSearchTool()
                elif name == "trials":
                    from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool
                    _tools[name] = ClinicalTrialsSearchTool()
                elif name == "drugs":
                    from evoagentx.tools.drugbank_tool import DrugSearchTool
                    _tools[name] = DrugSearchTool()
                elif name == "interactions":
                    from evoagentx.tools.drugbank_tool import DrugInteractionTool
                    _tools[name] = DrugInteractionTool()
                elif name == "rxnorm":
                    from evoagentx.tools.drugbank_tool import RxNormTool
                    _tools[name] = RxNormTool()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Tool init error: {e}")
        return _tools.get(name)

    @router.get("/health")
    async def health():
        from evoagentx.tools.health import get_health
        return get_health()

    @router.get("/health/detailed")
    async def health_detailed():
        from evoagentx.tools.health import get_detailed_health
        return get_detailed_health()

    @router.get("/search")
    async def pubmed_search(
        q: str = Query(..., description="PubMed search query"),
        max: int = Query(5, ge=1, le=50, description="Max results"),
        sort: str = Query("relevance", description="Sort: relevance, date")
    ):
        tool = _get_tool("pubmed")
        start = time.time()
        result = tool.search(query=q, max_results=max, sort=sort)
        latency = (time.time() - start) * 1000
        return {
            "query": q,
            "total": result["total_count"],
            "returned": result["returned"],
            "articles": result["articles"],
            "latency_ms": round(latency, 1),
            "timestamp": datetime.utcnow().isoformat()
        }

    @router.get("/trials")
    async def trials_search(
        q: str = Query(..., description="Search query"),
        status: Optional[str] = Query(None, description="Filter by status"),
        phase: Optional[str] = Query(None, description="Filter by phase"),
        max: int = Query(5, ge=1, le=50)
    ):
        tool = _get_tool("trials")
        start = time.time()
        result = tool.search(query=q, status=status or "", phase=phase or "", max_results=max)
        latency = (time.time() - start) * 1000
        return {
            "query": q,
            "total": result["total_count"],
            "returned": result["returned"],
            "trials": result["trials"],
            "latency_ms": round(latency, 1),
            "timestamp": datetime.utcnow().isoformat()
        }

    @router.get("/drugs")
    async def drug_search(
        q: str = Query(..., description="Drug name"),
        max: int = Query(3, ge=1, le=20)
    ):
        tool = _get_tool("drugs")
        start = time.time()
        result = tool.search_label(query=q, max_results=max)
        latency = (time.time() - start) * 1000
        return {
            "query": q,
            "returned": len(result),
            "drugs": result,
            "latency_ms": round(latency, 1),
            "timestamp": datetime.utcnow().isoformat()
        }

    @router.get("/interactions")
    async def drug_interactions(
        drug1: str = Query(..., description="First drug"),
        drug2: str = Query(..., description="Second drug")
    ):
        tool = _get_tool("interactions")
        start = time.time()
        result = tool(drug1=drug1, drug2=drug2)
        latency = (time.time() - start) * 1000
        return {
            "drug1": drug1,
            "drug2": drug2,
            "result": result,
            "latency_ms": round(latency, 1),
            "timestamp": datetime.utcnow().isoformat()
        }

    @router.get("/rxnorm")
    async def rxnorm_lookup(
        name: str = Query(..., description="Drug name"),
        op: str = Query("search", description="Operation: search, ingredients, related")
    ):
        tool = _get_tool("rxnorm")
        result = tool(drug_name=name, operation=op)
        return {"result": result}

    @router.get("/stats")
    async def stats():
        from evoagentx.tools.cache import get_cache
        from evoagentx.tools.rate_limiter import get_limiter
        cache = get_cache()
        limiter = get_limiter()
        return {
            "cache": cache.stats(),
            "rate_limiter": limiter.get_stats(),
        }

    @router.get("/benchmark")
    async def benchmark_info():
        from evoagentx.benchmark.medical_benchmark import MedicalBenchmark
        bench = MedicalBenchmark()
        return {
            "categories": bench.list_categories(),
            "total_questions": len(bench.questions),
            "by_category": {cat: len(qs) for cat, qs in bench._by_category.items()},
        }
