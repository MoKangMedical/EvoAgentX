"""
Drug Information & Interaction Tool for EvoAgentX

Provides drug information lookup, interaction checking, and pharmacology data.
Uses open APIs: OpenFDA, DrugBank (public), and RxNorm.

Integration points:
- DrugMind: Drug development pipeline and interaction analysis
- PharmaSim: Drug market simulation data
- MediChat-RD: Rare disease drug repurposing candidates
"""

import json
import os
import time
from typing import Any

from .tool import Tool, Toolkit


class DrugSearchTool(Tool):
    """Search for drug information using OpenFDA API."""

    name: str = "drug_search"
    description: str = (
        "Search for drug information from FDA databases. Returns drug names, "
        "active ingredients, indications, warnings, dosage forms, and "
        "manufacturer info. Useful for drug research, pharmacovigilance, "
        "and clinical decision support."
    )
    inputs: dict[str, dict[str, Any]] = {
        "query": {
            "type": "string",
            "description": (
                "Drug name or active ingredient to search. "
                "Example: 'pembrolizumab' or 'aspirin'"
            )
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum results to return (default 5, max 20)"
        }
    }
    required: list[str] | None = ["query"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://api.fda.gov/drug"
        self.last_request_time = 0

    def _rate_limit(self):
        """OpenFDA rate limit: 240 req/min without key, 1200 with key."""
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.26:
            time.sleep(0.26 - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: dict) -> dict:
        """Make request to OpenFDA API."""
        import urllib.parse
        import urllib.request

        self._rate_limit()
        api_key = os.getenv("OPENFDA_API_KEY", "")
        if api_key:
            params["api_key"] = api_key

        query_string = urllib.parse.urlencode(params)
        url = f"{self.base_url}/{endpoint}.json?{query_string}"

        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "EvoAgentX/0.1"
                })
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except Exception:
                if attempt < 2:
                    time.sleep(1)
                    continue
                raise
        return {}

    def search_label(self, query: str, max_results: int = 5) -> list[dict]:
        """Search drug labels from OpenFDA."""
        max_results = min(max_results, 20)
        params = {
            "search": f'openfda.brand_name:"{query}" OR openfda.generic_name:"{query}"',
            "limit": max_results
        }
        data = self._make_request("label", params)
        results = data.get("results", [])

        drugs = []
        for r in results:
            openfda = r.get("openfda", {})
            drugs.append({
                "brand_name": ", ".join(openfda.get("brand_name", ["N/A"])),
                "generic_name": ", ".join(openfda.get("generic_name", ["N/A"])),
                "manufacturer": ", ".join(openfda.get("manufacturer_name", ["N/A"])),
                "route": ", ".join(openfda.get("route", ["N/A"])),
                "substance_name": ", ".join(openfda.get("substance_name", ["N/A"])),
                "indications": self._extract_field(r, "indications_and_usage"),
                "warnings": self._extract_field(r, "warnings"),
                "dosage": self._extract_field(r, "dosage_and_administration"),
                "contraindications": self._extract_field(r, "contraindications"),
                "adverse_reactions": self._extract_field(r, "adverse_reactions"),
                "drug_interactions": self._extract_field(r, "drug_interactions"),
            })

        return drugs

    def _extract_field(self, record: dict, field: str) -> str:
        """Extract and truncate a field from FDA label."""
        values = record.get(field, ["N/A"])
        text = values[0] if values else "N/A"
        return text[:300] + "..." if len(text) > 300 else text

    def __call__(self, query: str, max_results: int = 5) -> str:
        """Search drugs and return formatted results."""
        drugs = self.search_label(query, max_results)

        if not drugs:
            return f"No drug information found for: {query}"

        lines = [f"Drug Search: '{query}'", f"Found {len(drugs)} result(s)", ""]

        for i, drug in enumerate(drugs, 1):
            lines.append(f"[{i}] {drug['brand_name']} ({drug['generic_name']})")
            lines.append(f"    Manufacturer: {drug['manufacturer']}")
            lines.append(f"    Route: {drug['route']}")
            lines.append(f"    Active: {drug['substance_name']}")
            lines.append(f"    Indications: {drug['indications'][:150]}...")
            if drug['drug_interactions'] and drug['drug_interactions'] != 'N/A':
                lines.append(f"    Interactions: {drug['drug_interactions'][:150]}...")
            lines.append("")

        return "\n".join(lines)


class DrugInteractionTool(Tool):
    """Check drug-drug interactions using OpenFDA adverse event data."""

    name: str = "drug_interaction_check"
    description: str = (
        "Check potential drug-drug interactions by analyzing FDA adverse event "
        "reports. Reports co-reported reactions when two drugs appear together. "
        "This is for research purposes only, not clinical decision-making."
    )
    inputs: dict[str, dict[str, Any]] = {
        "drug1": {
            "type": "string",
            "description": "First drug name (brand or generic)"
        },
        "drug2": {
            "type": "string",
            "description": "Second drug name (brand or generic)"
        }
    }
    required: list[str] | None = ["drug1", "drug2"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://api.fda.gov/drug"
        self.last_request_time = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.26:
            time.sleep(0.26 - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: dict) -> dict:
        import urllib.parse
        import urllib.request

        self._rate_limit()
        query_string = urllib.parse.urlencode(params)
        url = f"{self.base_url}/{endpoint}.json?{query_string}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EvoAgentX/0.1"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return {}

    def __call__(self, drug1: str, drug2: str) -> str:
        """Check drug interactions via FDA adverse event reports."""
        # Search for adverse events where both drugs are reported together
        params = {
            "search": (
                f'patient.drug.openfda.brand_name:"{drug1}" AND '
                f'patient.drug.openfda.brand_name:"{drug2}"'
            ),
            "count": "patient.reaction.reactionmeddrapt.exact",
            "limit": 10
        }
        data = self._make_request("event", params)
        reactions = data.get("results", [])

        if not reactions:
            # Try generic names
            params["search"] = (
                f'patient.drug.openfda.generic_name:"{drug1}" AND '
                f'patient.drug.openfda.generic_name:"{drug2}"'
            )
            data = self._make_request("event", params)
            reactions = data.get("results", [])

        total = data.get("meta", {}).get("results", {}).get("total", 0)

        lines = [
            f"Drug Interaction Analysis: {drug1} + {drug2}",
            "Based on FDA Adverse Event Reporting System (FAERS)",
            f"Total co-reported events: {total}",
            ""
        ]

        if reactions:
            lines.append("Most frequently co-reported reactions:")
            for r in reactions[:10]:
                term = r.get("term", "Unknown")
                count = r.get("count", 0)
                lines.append(f"  - {term}: {count} reports")
            lines.append("")
            lines.append(
                "NOTE: This data shows co-occurrence in adverse event reports, "
                "not proven causal interactions. Consult clinical references "
                "for confirmed interactions."
            )
        else:
            lines.append(
                f"No significant co-reported adverse events found for "
                f"{drug1} and {drug2} in FAERS data."
            )

        return "\n".join(lines)


class RxNormTool(Tool):
    """Look up drug information using the RxNorm API."""

    name: str = "rxnorm_lookup"
    description: str = (
        "Look up drug concepts, ingredients, and relationships using RxNorm. "
        "Useful for normalizing drug names, finding ingredients, and "
        "identifying drug classes."
    )
    inputs: dict[str, dict[str, Any]] = {
        "drug_name": {
            "type": "string",
            "description": "Drug name to look up"
        },
        "operation": {
            "type": "string",
            "description": (
                "Operation: 'search' (find concepts), 'ingredients' (get ingredients), "
                "'related' (get related drugs). Default: 'search'"
            )
        }
    }
    required: list[str] | None = ["drug_name"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://rxnav.nlm.nih.gov/REST"
        self.last_request_time = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.2:
            time.sleep(0.2 - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, path: str) -> dict:
        import urllib.request

        self._rate_limit()
        url = f"{self.base_url}/{path}"

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "EvoAgentX/0.1",
                "Accept": "application/json"
            })
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return {}

    def __call__(self, drug_name: str, operation: str = "search") -> str:
        """Look up drug information."""
        if operation == "ingredients":
            data = self._make_request(
                f"drugs.json?name={drug_name}"
            )
            drug_concepts = data.get("drugGroup", {}).get("conceptGroup", [])
            lines = [f"RxNorm Ingredients for: {drug_name}", ""]
            for group in drug_concepts:
                if group.get("conceptProperties"):
                    for concept in group["conceptProperties"]:
                        lines.append(
                            f"  - {concept.get('name', 'N/A')} "
                            f"(RxCUI: {concept.get('rxcui', 'N/A')}, "
                            f"type: {concept.get('tty', 'N/A')})"
                        )
            return "\n".join(lines) if len(lines) > 2 else f"No ingredients found for {drug_name}"

        elif operation == "related":
            # First get RxCUI
            search_data = self._make_request(
                f"drugs.json?name={drug_name}"
            )
            concepts = search_data.get("drugGroup", {}).get("conceptGroup", [])
            rxcui = None
            for group in concepts:
                if group.get("conceptProperties"):
                    rxcui = group["conceptProperties"][0].get("rxcui")
                    break

            if not rxcui:
                return f"Could not find RxCUI for: {drug_name}"

            related_data = self._make_request(f"rxcui/{rxcui}/related.json")
            related = related_data.get("relatedGroup", {}).get("conceptGroup", [])
            lines = [f"RxNorm Related for: {drug_name} (RxCUI: {rxcui})", ""]
            for group in related:
                for concept in group.get("conceptProperties", []):
                    lines.append(
                        f"  - {concept.get('name', 'N/A')} "
                        f"({concept.get('tty', 'N/A')})"
                    )
            return "\n".join(lines) if len(lines) > 2 else f"No related drugs found for {drug_name}"

        else:  # search
            data = self._make_request(
                f"approximateTerm.json?term={drug_name}&maxEntries=5"
            )
            candidates = data.get("approximateGroup", {}).get("candidate", [])
            lines = [f"RxNorm Search: '{drug_name}'", ""]
            for c in candidates[:5]:
                lines.append(
                    f"  - {c.get('name', 'N/A')} "
                    f"(RxCUI: {c.get('rxcui', 'N/A')}, "
                    f"score: {c.get('score', 'N/A')})"
                )
            return "\n".join(lines) if len(lines) > 2 else f"No results for {drug_name}"


class DrugInfoToolkit(Toolkit):
    """Comprehensive drug information toolkit."""

    name: str = "drug_info_toolkit"
    description: str = (
        "Drug information toolkit combining FDA drug labels, interaction "
        "checking, and RxNorm drug normalization. For medical research "
        "and drug development workflows."
    )

    def __init__(self, **kwargs):
        tools = [
            DrugSearchTool(),
            DrugInteractionTool(),
            RxNormTool(),
        ]
        super().__init__(tools=tools, **kwargs)
