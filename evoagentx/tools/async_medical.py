"""
Async Medical Tools for EvoAgentX

Provides async versions of medical tools for use with FastAPI
and concurrent workflows.

Usage:
    import asyncio
    from evoagentx.tools.async_medical import AsyncPubMedSearch
    async def main():
        tool = AsyncPubMedSearch()
        result = await tool.asearch("gene therapy", max_results=5)
    asyncio.run(main())
"""

import asyncio
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor

# Thread pool for running sync tools in async context
_executor = ThreadPoolExecutor(max_workers=4)


class AsyncPubMedSearch:
    """Async wrapper for PubMed search."""

    def __init__(self):
        self._tool = None

    def _get_tool(self):
        if self._tool is None:
            from .pubmed_tool import PubMedSearchTool
            self._tool = PubMedSearchTool()
        return self._tool

    async def asearch(self, query: str, max_results: int = 5,
                      sort: str = "relevance") -> Dict[str, Any]:
        """Async PubMed search."""
        loop = asyncio.get_event_loop()
        tool = self._get_tool()
        return await loop.run_in_executor(
            _executor,
            lambda: tool.search(query, max_results, sort)
        )

    async def __call__(self, query: str, max_results: int = 5,
                       sort: str = "relevance") -> str:
        """Async callable interface."""
        loop = asyncio.get_event_loop()
        tool = self._get_tool()
        return await loop.run_in_executor(
            _executor,
            lambda: tool(query, max_results, sort)
        )


class AsyncClinicalTrialsSearch:
    """Async wrapper for ClinicalTrials.gov search."""

    def __init__(self):
        self._tool = None

    def _get_tool(self):
        if self._tool is None:
            from .clinicaltrials_tool import ClinicalTrialsSearchTool
            self._tool = ClinicalTrialsSearchTool()
        return self._tool

    async def asearch(self, query: str, status: str = "",
                      phase: str = "", max_results: int = 5) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        tool = self._get_tool()
        return await loop.run_in_executor(
            _executor,
            lambda: tool.search(query, status, phase, max_results)
        )


class AsyncDrugSearch:
    """Async wrapper for drug search."""

    def __init__(self):
        self._tool = None

    def _get_tool(self):
        if self._tool is None:
            from .drugbank_tool import DrugSearchTool
            self._tool = DrugSearchTool()
        return self._tool

    async def asearch(self, query: str, max_results: int = 3) -> list:
        loop = asyncio.get_event_loop()
        tool = self._get_tool()
        return await loop.run_in_executor(
            _executor,
            lambda: tool.search_label(query, max_results)
        )


class AsyncMedicalSearcher:
    """
    Combined async searcher that queries all medical databases concurrently.

    Usage:
        searcher = AsyncMedicalSearcher()
        results = await searcher.search_all("CRISPR gene therapy")
    """

    def __init__(self):
        self.pubmed = AsyncPubMedSearch()
        self.trials = AsyncClinicalTrialsSearch()
        self.drugs = AsyncDrugSearch()

    async def search_all(self, query: str, max_per_db: int = 5) -> Dict[str, Any]:
        """Search all databases concurrently."""
        pubmed_task = self.pubmed.asearch(query, max_per_db)
        trials_task = self.trials.asearch(query, max_results=max_per_db)

        # Try to extract drug name from query for drug search
        drug_query = self._extract_drug_name(query)
        drugs_task = self.drugs.asearch(drug_query, max_per_db) if drug_query else None

        tasks = [pubmed_task, trials_task]
        if drugs_task:
            tasks.append(drugs_task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = {
            "query": query,
            "pubmed": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "trials": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
        }
        if drugs_task and len(results) > 2:
            output["drugs"] = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}

        return output

    def _extract_drug_name(self, query: str) -> Optional[str]:
        """Try to extract a drug name from the query."""
        known_drugs = [
            "pembrolizumab", "nivolumab", "atezolizumab", "durvalumab",
            "trastuzumab", "bevacizumab", "rituximab", "adalimumab",
            "insulin", "metformin", "aspirin", "warfarin", "heparin",
            "zolgensma", "casgevy", "luxturna", "kymriah",
        ]
        query_lower = query.lower()
        for drug in known_drugs:
            if drug in query_lower:
                return drug
        return None
