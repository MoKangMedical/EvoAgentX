"""
Unit tests for medical tools.

Tests PubMed, ClinicalTrials, and Drug tools with real API calls.
No API keys required for these public APIs.

Usage:
    pytest tests/src/tools/test_medical_tools.py -v
    pytest tests/src/tools/test_medical_tools.py -v -k "pubmed"  # PubMed only
"""

import pytest
import time


# ──────────────────────────────────────────────
# PubMed Tests
# ──────────────────────────────────────────────

class TestPubMedSearchTool:
    """Test PubMed search functionality."""

    def test_import(self):
        from evoagentx.tools.pubmed_tool import PubMedSearchTool
        assert PubMedSearchTool is not None

    def test_tool_schema(self):
        from evoagentx.tools.pubmed_tool import PubMedSearchTool
        tool = PubMedSearchTool()
        schema = tool.get_tool_schema()
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "pubmed_search"
        assert "query" in schema["function"]["parameters"]["properties"]

    def test_search_returns_results(self):
        from evoagentx.tools.pubmed_tool import PubMedSearchTool
        tool = PubMedSearchTool()
        result = tool(query="cancer immunotherapy", max_results=3)
        assert "PubMed Search" in result
        assert "PMID" in result

    def test_search_empty_query(self):
        from evoagentx.tools.pubmed_tool import PubMedSearchTool
        tool = PubMedSearchTool()
        result = tool(query="zzzznonexistentquery12345zzzz", max_results=1)
        assert "No PubMed results" in result or "Total results" in result

    def test_search_structured(self):
        from evoagentx.tools.pubmed_tool import PubMedSearchTool
        tool = PubMedSearchTool()
        results = tool.search(query="rare disease gene therapy", max_results=2)
        assert "query" in results
        assert "total_count" in results
        assert "articles" in results
        assert results["returned"] <= 2
        if results["articles"]:
            art = results["articles"][0]
            assert "pmid" in art
            assert "title" in art
            assert "url" in art
            assert art["url"].startswith("https://pubmed.ncbi.nlm.nih.gov/")


class TestPubMedFetchDetail:
    """Test PubMed detail fetch."""

    def test_fetch_known_pmid(self):
        from evoagentx.tools.pubmed_tool import PubMedFetchDetailTool
        tool = PubMedFetchDetailTool()
        # PMID 33309881 is a well-known COVID review paper
        result = tool(pmid="33309881")
        assert "PMID" in result
        assert "33309881" in result

    def test_fetch_invalid_pmid(self):
        from evoagentx.tools.pubmed_tool import PubMedFetchDetailTool
        tool = PubMedFetchDetailTool()
        result = tool(pmid="99999999999")
        assert "No article found" in result or "Error" in result or "PMID" in result


# ──────────────────────────────────────────────
# ClinicalTrials Tests
# ──────────────────────────────────────────────

class TestClinicalTrialsSearchTool:
    """Test ClinicalTrials.gov search functionality."""

    def test_import(self):
        from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool
        assert ClinicalTrialsSearchTool is not None

    def test_tool_schema(self):
        from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool
        tool = ClinicalTrialsSearchTool()
        schema = tool.get_tool_schema()
        assert schema["function"]["name"] == "clinical_trials_search"

    def test_search_returns_results(self):
        from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool
        tool = ClinicalTrialsSearchTool()
        result = tool(query="diabetes type 2", max_results=3)
        assert "ClinicalTrials.gov" in result
        assert "NCT" in result

    def test_search_with_status_filter(self):
        from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool
        tool = ClinicalTrialsSearchTool()
        result = tool(query="lung cancer", status="RECRUITING", max_results=2)
        assert "RECRUITING" in result or "Total:" in result

    def test_search_structured(self):
        from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool
        tool = ClinicalTrialsSearchTool()
        results = tool.search(query="immunotherapy", max_results=2)
        assert "trials" in results
        if results["trials"]:
            trial = results["trials"][0]
            assert "nct_id" in trial
            assert trial["nct_id"].startswith("NCT")
            assert "url" in trial


class TestClinicalTrialsDetail:
    """Test clinical trial detail fetch."""

    def test_fetch_known_nct(self):
        from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsDetailTool
        tool = ClinicalTrialsDetailTool()
        # NCT04280705 is a well-known COVID trial
        result = tool(nct_id="NCT04280705")
        assert "NCT04280705" in result
        assert "Title" in result


# ──────────────────────────────────────────────
# Drug Tools Tests
# ──────────────────────────────────────────────

class TestDrugSearchTool:
    """Test FDA drug search functionality."""

    def test_import(self):
        from evoagentx.tools.drugbank_tool import DrugSearchTool
        assert DrugSearchTool is not None

    def test_tool_schema(self):
        from evoagentx.tools.drugbank_tool import DrugSearchTool
        tool = DrugSearchTool()
        schema = tool.get_tool_schema()
        assert schema["function"]["name"] == "drug_search"

    def test_search_known_drug(self):
        from evoagentx.tools.drugbank_tool import DrugSearchTool
        tool = DrugSearchTool()
        result = tool(query="aspirin", max_results=1)
        assert "Drug Search" in result
        assert "aspirin" in result.lower() or "ASPIRIN" in result

    def test_search_structured(self):
        from evoagentx.tools.drugbank_tool import DrugSearchTool
        tool = DrugSearchTool()
        drugs = tool.search_label(query="metformin", max_results=1)
        if drugs:
            assert "brand_name" in drugs[0]
            assert "generic_name" in drugs[0]


class TestDrugInteractionTool:
    """Test drug interaction checking."""

    def test_import(self):
        from evoagentx.tools.drugbank_tool import DrugInteractionTool
        assert DrugInteractionTool is not None

    def test_interaction_check(self):
        from evoagentx.tools.drugbank_tool import DrugInteractionTool
        tool = DrugInteractionTool()
        result = tool(drug1="warfarin", drug2="aspirin")
        assert "Drug Interaction" in result
        assert "warfarin" in result.lower()
        assert "aspirin" in result.lower()


class TestRxNormTool:
    """Test RxNorm drug normalization."""

    def test_import(self):
        from evoagentx.tools.drugbank_tool import RxNormTool
        assert RxNormTool is not None

    def test_search(self):
        from evoagentx.tools.drugbank_tool import RxNormTool
        tool = RxNormTool()
        result = tool(drug_name="ibuprofen", operation="search")
        assert "RxNorm" in result
        assert "ibuprofen" in result.lower() or "IBUPROFEN" in result

    def test_ingredients(self):
        from evoagentx.tools.drugbank_tool import RxNormTool
        tool = RxNormTool()
        result = tool(drug_name="metformin", operation="ingredients")
        assert "RxNorm" in result


# ──────────────────────────────────────────────
# Medical Registry Tests
# ──────────────────────────────────────────────

class TestMedicalRegistry:
    """Test medical tools registry."""

    def test_get_medical_tools(self):
        from evoagentx.tools.medical_registry import get_medical_tools
        tools = get_medical_tools()
        assert "pubmed_search" in tools
        assert "clinical_trials_search" in tools
        assert "drug_search" in tools

    def test_get_medical_toolkits(self):
        from evoagentx.tools.medical_registry import get_medical_toolkits
        toolkits = get_medical_toolkits()
        assert "pubmed_toolkit" in toolkits
        assert "clinical_trials_toolkit" in toolkits
        assert "drug_info_toolkit" in toolkits

    def test_create_medical_tools(self):
        from evoagentx.tools.medical_registry import create_medical_tools
        tools = create_medical_tools()
        assert len(tools) >= 3  # At least pubmed, trials, drug

    def test_list_available(self):
        from evoagentx.tools.medical_registry import list_available_tools
        listing = list_available_tools()
        assert "pubmed_search" in listing
        assert "clinical_trials" in listing
        assert "drug" in listing


# ──────────────────────────────────────────────
# Bridge Tests
# ──────────────────────────────────────────────

class TestEvoXBridge:
    """Test EvoX bridge functionality."""

    def test_import(self):
        from evoagentx.bridge import EvoXBridge, MedicalEvolutionBridge
        assert EvoXBridge is not None
        assert MedicalEvolutionBridge is not None

    def test_bridge_status(self):
        from evoagentx.bridge import EvoXBridge
        bridge = EvoXBridge()
        status = bridge.get_status()
        assert "evox_path" in status
        assert "layers" in status

    def test_session_management(self):
        from evoagentx.bridge import EvoXBridge
        bridge = EvoXBridge()
        session_id = bridge.start_session("test")
        assert session_id.startswith("evo-test-")

    def test_medical_bridge(self):
        from evoagentx.bridge import MedicalEvolutionBridge
        bridge = MedicalEvolutionBridge()
        status = bridge.get_status()
        assert status is not None
