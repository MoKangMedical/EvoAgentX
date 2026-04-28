"""
Medical Agent Example for EvoAgentX

Demonstrates how to create a medical research agent with:
- PubMed literature search
- ClinicalTrials.gov search
- Drug information lookup
- EvoX evolution optimization

Integration with OPC projects:
- MetaForge: Systematic review methodology
- DrugMind: Drug development pipeline
- MediChat-RD: Rare disease research
- PharmaSim: Clinical trial simulation

Usage:
    cd /Users/apple/EvoAgentX
    source venv/bin/activate
    python examples/medical/medical_agent_example.py
"""

import os
import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evoagentx.agents.agent import Agent
from evoagentx.models.openai_model import OpenAILLMConfig, OpenAILLM
from evoagentx.tools.pubmed_tool import PubMedSearchTool, PubMedSearchToolkit
from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool, ClinicalTrialsToolkit
from evoagentx.tools.drugbank_tool import DrugSearchTool, DrugInteractionTool, DrugInfoToolkit


def create_medical_research_agent():
    """
    Create a medical research agent with comprehensive tools.

    This agent can:
    1. Search PubMed for biomedical literature
    2. Query ClinicalTrials.gov for trial data
    3. Look up drug information from FDA databases
    4. Check drug-drug interactions
    """
    # Configure LLM
    llm_config = OpenAILLMConfig(
        model="gpt-4o-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        temperature=0.3,  # Lower temperature for medical accuracy
        max_tokens=2048
    )
    llm = OpenAILLM(config=llm_config)

    # Create tools
    tools = [
        PubMedSearchTool(),
        ClinicalTrialsSearchTool(),
        DrugSearchTool(),
        DrugInteractionTool(),
    ]

    # Create agent
    agent = Agent(
        name="MedicalResearchAgent",
        llm=llm,
        tools=tools,
        system_prompt=(
            "You are a medical research assistant specialized in evidence-based "
            "medicine. Your capabilities include:\n\n"
            "1. PubMed Literature Search: Search and analyze biomedical publications\n"
            "2. Clinical Trials: Find and evaluate clinical trial data\n"
            "3. Drug Information: Look up FDA drug labels and safety data\n"
            "4. Drug Interactions: Check potential drug-drug interactions\n\n"
            "IMPORTANT GUIDELINES:\n"
            "- Always cite sources (PMIDs, NCT IDs, FDA references)\n"
            "- Clearly state limitations and uncertainty levels\n"
            "- Never provide clinical diagnoses or treatment recommendations\n"
            "- Always recommend consulting healthcare professionals\n"
            "- Use evidence-based language (e.g., 'studies suggest', 'evidence indicates')\n"
            "- Flag when evidence is insufficient or conflicting\n"
        )
    )

    return agent


def demo_pubmed_search():
    """Demo: Search PubMed for rare disease gene therapy."""
    print("=" * 60)
    print("Demo 1: PubMed Literature Search")
    print("=" * 60)

    tool = PubMedSearchTool()
    results = tool(
        query="rare disease AND gene therapy[tiab] AND 2023:2025[dp]",
        max_results=5,
        sort="relevance"
    )
    print(results)
    print()


def demo_clinical_trials():
    """Demo: Search ClinicalTrials.gov for gene therapy trials."""
    print("=" * 60)
    print("Demo 2: Clinical Trials Search")
    print("=" * 60)

    tool = ClinicalTrialsSearchTool()
    results = tool(
        query="gene therapy rare disease",
        status="RECRUITING",
        phase="PHASE3",
        max_results=5
    )
    print(results)
    print()


def demo_drug_search():
    """Demo: Search FDA drug labels."""
    print("=" * 60)
    print("Demo 3: Drug Information Search")
    print("=" * 60)

    tool = DrugSearchTool()
    results = tool(query="pembrolizumab", max_results=2)
    print(results)
    print()


def demo_drug_interaction():
    """Demo: Check drug interactions."""
    print("=" * 60)
    print("Demo 4: Drug Interaction Check")
    print("=" * 60)

    tool = DrugInteractionTool()
    results = tool(drug1="warfarin", drug2="aspirin")
    print(results)
    print()


def demo_evox_integration():
    """Demo: EvoX evolution integration."""
    print("=" * 60)
    print("Demo 5: EvoX Bridge Integration")
    print("=" * 60)

    from evoagentx.bridge import EvoXBridge

    bridge = EvoXBridge()
    status = bridge.get_status()

    print(f"EvoX Path: {status['evox_path']}")
    print(f"EvoX Available: {status['evox_available']}")
    print(f"Darwin Available: {status['darwin_available']}")
    print(f"Layers: {json.dumps(status['layers'], indent=2)}")
    print()

    if status['evox_available']:
        print("EvoX bridge is ready for agent evolution.")
        print("Use bridge.evolve_agent(agent) to run evolution.")
    else:
        print("EvoX project not found. Install from:")
        print("  https://github.com/MoKangMedical/evox")
    print()


def demo_medical_workflow():
    """Demo: Run medical literature review workflow."""
    print("=" * 60)
    print("Demo 6: Medical Workflow Execution")
    print("=" * 60)

    # Check if workflow file exists
    workflow_path = Path(__file__).parent.parent.parent / \
        "Wonderful_workflow_corpus" / "medical_literature_review" / "workflow.json"

    if workflow_path.exists():
        with open(workflow_path) as f:
            workflow = json.load(f)
        print(f"Workflow: {workflow['name']}")
        print(f"Description: {workflow['description']}")
        print(f"Nodes: {len(workflow['nodes'])}")
        print(f"Tags: {', '.join(workflow['tags'])}")
    else:
        print(f"Workflow not found at: {workflow_path}")

    print()


def main():
    """Run all demos."""
    print("EvoAgentX Medical AI Integration Demo")
    print("=" * 60)
    print("Integration with OPC projects:")
    print("  - MetaForge: Systematic review methodology")
    print("  - DrugMind: Drug development pipeline")
    print("  - MediChat-RD: Rare disease research")
    print("  - PharmaSim: Clinical trial simulation")
    print("=" * 60)
    print()

    # Run demos that don't require API keys
    demo_evox_integration()
    demo_medical_workflow()

    # Run API-dependent demos if key is available
    if os.getenv("OPENAI_API_KEY"):
        demo_pubmed_search()
        demo_clinical_trials()
        demo_drug_search()
        demo_drug_interaction()
    else:
        print("Note: Set OPENAI_API_KEY to run API-dependent demos.")
        print("The medical tools (PubMed, ClinicalTrials, FDA) work without API keys.")
        print()

    # Tool-only demos (no LLM needed)
    print("=" * 60)
    print("Running Tool-Only Demos (no API key needed)")
    print("=" * 60)
    print()

    try:
        demo_pubmed_search()
    except Exception as e:
        print(f"PubMed demo error: {e}")
        print("(This is expected if running without network access)")

    try:
        demo_clinical_trials()
    except Exception as e:
        print(f"Clinical trials demo error: {e}")

    try:
        demo_drug_search()
    except Exception as e:
        print(f"Drug search demo error: {e}")

    print()
    print("=" * 60)
    print("Demo Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
