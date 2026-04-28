"""
ClinicalTrials.gov API Tool for EvoAgentX

Search and retrieve clinical trial data from ClinicalTrials.gov.
No API key required (rate limited to ~10 requests/second).

Integration points:
- PharmaSim: Clinical trial phase data for drug simulation
- MediChat-RD: Rare disease clinical trial availability
- DrugMind: Drug development pipeline tracking

API docs: https://clinicaltrials.gov/api/gui
"""

import json
import time
from typing import Any

from .tool import Tool, Toolkit


class ClinicalTrialsSearchTool(Tool):
    """Search ClinicalTrials.gov for clinical trial data."""

    name: str = "clinical_trials_search"
    description: str = (
        "Search ClinicalTrials.gov for clinical trials. Returns trial IDs, "
        "titles, status, phases, conditions, interventions, sponsors, and "
        "enrollment info. Useful for drug development research, clinical "
        "evidence gathering, and understanding treatment landscapes."
    )
    inputs: dict[str, dict[str, Any]] = {
        "query": {
            "type": "string",
            "description": (
                "Search query. Can include condition, intervention, or keyword. "
                "Example: 'gene therapy rare disease' or 'pembrolizumab lung cancer'"
            )
        },
        "status": {
            "type": "string",
            "description": (
                "Filter by status: 'RECRUITING', 'COMPLETED', 'ACTIVE_NOT_RECRUITING', "
                "'NOT_YET_RECRUITING', 'TERMINATED', 'SUSPENDED', 'WITHDRAWN'. "
                "Leave empty for all statuses."
            )
        },
        "phase": {
            "type": "string",
            "description": (
                "Filter by phase: 'PHASE1', 'PHASE2', 'PHASE3', 'PHASE4', "
                "'EARLY_PHASE1', 'NA' (not applicable). Leave empty for all phases."
            )
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum results to return (default 10, max 100)"
        }
    }
    required: list[str] | None = ["query"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
        self.last_request_time = 0

    def _rate_limit(self):
        """ClinicalTrials.gov rate limit: ~10 req/s."""
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.11:
            time.sleep(0.11 - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, params: dict) -> dict:
        """Make request to ClinicalTrials.gov API v2."""
        import urllib.parse
        import urllib.request

        self._rate_limit()
        query_string = urllib.parse.urlencode(params, doseq=True)
        url = f"{self.base_url}?{query_string}"

        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "EvoAgentX/0.1 (medical-ai-framework)",
                    "Accept": "application/json"
                })
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except Exception:
                if attempt < 2:
                    time.sleep(1)
                    continue
                raise
        return {}

    def search(self, query: str, status: str = "", phase: str = "",
               max_results: int = 10) -> dict[str, Any]:
        """Search clinical trials and return structured results."""
        max_results = min(max_results, 100)

        params = {
            "query.cond": query,
            "pageSize": max_results,
            "format": "json",
            "fields": (
                "NCTId,BriefTitle,OverallStatus,Phase,Condition,"
                "InterventionName,LeadSponsorName,EnrollmentCount,"
                "StartDate,CompletionDate,StudyType"
            )
        }

        if status:
            params["filter.overallStatus"] = status
        if phase:
            params["filter.phase"] = phase

        data = self._make_request(params)
        studies = data.get("studies", [])

        results = []
        for study in studies:
            protocol = study.get("protocolSection", {})
            ident = protocol.get("identificationModule", {})
            status_mod = protocol.get("statusModule", {})
            design = protocol.get("designModule", {})
            conditions_mod = protocol.get("conditionsModule", {})
            interventions_mod = protocol.get("armsInterventionsModule", {})
            sponsor_mod = protocol.get("sponsorCollaboratorsModule", {})

            # Extract interventions
            interventions = []
            for iv in interventions_mod.get("interventions", []):
                interventions.append(iv.get("name", ""))

            # Extract phases
            phases = design.get("phases", [])

            results.append({
                "nct_id": ident.get("nctId", ""),
                "title": ident.get("briefTitle", ""),
                "status": status_mod.get("overallStatus", ""),
                "phases": phases,
                "conditions": conditions_mod.get("conditions", []),
                "interventions": interventions,
                "sponsor": sponsor_mod.get("leadSponsor", {}).get("name", ""),
                "enrollment": design.get("enrollmentInfo", {}).get("count", 0),
                "study_type": design.get("studyType", ""),
                "start_date": status_mod.get("startDateStruct", {}).get("date", ""),
                "completion_date": status_mod.get("completionDateStruct", {}).get("date", ""),
                "url": f"https://clinicaltrials.gov/study/{ident.get('nctId', '')}"
            })

        total_count = data.get("totalCount", len(results))

        return {
            "query": query,
            "total_count": total_count,
            "returned": len(results),
            "trials": results
        }

    def __call__(self, query: str, status: str = "", phase: str = "",
                 max_results: int = 10) -> str:
        """Execute search and return formatted results."""
        results = self.search(query, status, phase, max_results)

        if not results["trials"]:
            return f"No clinical trials found for: {query}"

        lines = [
            f"ClinicalTrials.gov Search: '{query}'",
            f"Total: {results['total_count']}, showing {results['returned']}",
            ""
        ]

        for i, trial in enumerate(results["trials"], 1):
            phases = ", ".join(trial["phases"]) if trial["phases"] else "N/A"
            conditions = ", ".join(trial["conditions"][:3])
            interventions = ", ".join(trial["interventions"][:3])

            lines.append(f"[{i}] {trial['nct_id']} | {trial['status']}")
            lines.append(f"    Title: {trial['title']}")
            lines.append(f"    Phase: {phases}")
            lines.append(f"    Conditions: {conditions}")
            lines.append(f"    Interventions: {interventions}")
            lines.append(f"    Sponsor: {trial['sponsor']}")
            lines.append(f"    Enrollment: {trial['enrollment']}")
            lines.append(f"    URL: {trial['url']}")
            lines.append("")

        return "\n".join(lines)


class ClinicalTrialsDetailTool(Tool):
    """Fetch detailed information for a specific clinical trial by NCT ID."""

    name: str = "clinical_trials_detail"
    description: str = (
        "Fetch detailed information for a specific clinical trial by NCT ID. "
        "Returns full protocol, eligibility criteria, outcome measures, and results."
    )
    inputs: dict[str, dict[str, Any]] = {
        "nct_id": {
            "type": "string",
            "description": "NCT ID of the trial (e.g., 'NCT04280705')"
        }
    }
    required: list[str] | None = ["nct_id"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
        self.last_request_time = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.11:
            time.sleep(0.11 - elapsed)
        self.last_request_time = time.time()

    def __call__(self, nct_id: str) -> str:
        """Fetch trial details by NCT ID."""
        import urllib.request

        self._rate_limit()
        url = f"{self.base_url}/{nct_id}?format=json"

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "EvoAgentX/0.1",
                "Accept": "application/json"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return f"Error fetching {nct_id}: {e}"

        protocol = data.get("protocolSection", {})
        ident = protocol.get("identificationModule", {})
        status_mod = protocol.get("statusModule", {})
        desc = protocol.get("descriptionModule", {})
        design = protocol.get("designModule", {})
        conditions_mod = protocol.get("conditionsModule", {})
        elig = protocol.get("eligibilityModule", {})

        return (
            f"NCT ID: {ident.get('nctId', nct_id)}\n"
            f"Title: {ident.get('briefTitle', '')}\n"
            f"Official Title: {ident.get('officialTitle', '')}\n"
            f"Status: {status_mod.get('overallStatus', '')}\n"
            f"Phase: {', '.join(design.get('phases', []))}\n"
            f"Conditions: {', '.join(conditions_mod.get('conditions', []))}\n"
            f"Summary: {desc.get('briefSummary', '')[:500]}\n"
            f"Eligibility: {elig.get('eligibilityCriteria', '')[:300]}\n"
            f"URL: https://clinicaltrials.gov/study/{nct_id}"
        )


class ClinicalTrialsToolkit(Toolkit):
    """Toolkit combining clinical trial search and detail fetch."""

    name: str = "clinical_trials_toolkit"
    description: str = (
        "ClinicalTrials.gov search toolkit. Search for clinical trials by "
        "condition, intervention, or drug name. Get detailed trial protocols."
    )

    def __init__(self, **kwargs):
        tools = [
            ClinicalTrialsSearchTool(),
            ClinicalTrialsDetailTool(),
        ]
        super().__init__(tools=tools, **kwargs)
