# Medical AI Integration Guide

## Overview

EvoAgentX has been enhanced with medical AI capabilities, integrating with the OPC (Open Pharma Collaboration) project ecosystem. This guide covers the medical-specific tools, workflows, and evolution strategies.

## Medical Tools

### PubMed Search Tool
Search biomedical literature from PubMed/NCBI.

```python
from evoagentx.tools.pubmed_tool import PubMedSearchTool, PubMedSearchToolkit

# Single tool
tool = PubMedSearchTool()
results = tool(query="rare disease AND gene therapy[tiab]", max_results=10)

# Full toolkit (search + detail fetch)
toolkit = PubMedSearchToolkit()
```

**Integration with MetaForge:**
- Shares PubMed API client for systematic review workflows
- Uses PICOS-based screening methodology
- Generates PRISMA-compliant reports

### ClinicalTrials.gov Tool
Search and analyze clinical trial data.

```python
from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool

tool = ClinicalTrialsSearchTool()
results = tool(
    query="gene therapy rare disease",
    status="RECRUITING",
    phase="PHASE3",
    max_results=10
)
```

**Integration with PharmaSim:**
- Provides clinical trial phase data for market simulation
- Tracks enrollment and completion timelines
- Identifies competitive landscape

### Drug Information Tool
FDA drug labels, interactions, and RxNorm lookups.

```python
from evoagentx.tools.drugbank_tool import DrugSearchTool, DrugInteractionTool, DrugInfoToolkit

# Drug label search
search = DrugSearchTool()
info = search(query="pembrolizumab")

# Drug interaction check
interaction = DrugInteractionTool()
result = interaction(drug1="warfarin", drug2="aspirin")

# Full toolkit
toolkit = DrugInfoToolkit()
```

**Integration with DrugMind:**
- FDA adverse event data for safety profiles
- Drug interaction analysis for combination therapies
- RxNorm normalization for drug name standardization

## Medical Workflows

### Literature Review Workflow
Location: `Wonderful_workflow_corpus/medical_literature_review/`

Automated pipeline:
1. Query Builder: Constructs optimized PubMed search queries
2. PubMed Search: Executes literature search
3. Screening: PICOS-based relevance screening
4. Data Extraction: Structured data extraction with citations
5. Synthesis: Evidence synthesis and report generation

### Drug Safety Analysis Workflow
Location: `Wonderful_workflow_corpus/drug_safety_analysis/`

Comprehensive pipeline:
1. Drug Info Lookup: FDA label data
2. Clinical Trials: Related trial data
3. Literature Search: Safety publications
4. Safety Analysis: Integrated safety profile generation

## EvoX Evolution Bridge

The EvoX bridge connects the three-layer evolution engine with EvoAgentX agents.

### Three-Layer Architecture

| Layer | Engine | Target | Method |
|-------|--------|--------|--------|
| 1 | Darwin | Agent Config | 8-dimension fitness scoring |
| 2 | EvoPrompt | Agent Prompts | Genetic algorithm optimization |
| 3 | SEW | Workflow Structure | Structure evolution with benchmark feedback |

### Usage

```python
from evoagentx.bridge import EvoXBridge, MedicalEvolutionBridge

# Standard bridge
bridge = EvoXBridge()
bridge.start_session("my_medical_agent")
session = bridge.evolve_agent(agent, rounds=3)
print(bridge.generate_report())

# Medical-specific bridge
med_bridge = MedicalEvolutionBridge()
results = med_bridge.evaluate_medical_agent(agent, test_cases)
```

### Medical Evaluation Criteria

The `MedicalEvolutionBridge` adds medical-specific evaluation:
- **Clinical Accuracy**: Correct medical information
- **Evidence Traceability**: PMID/citation presence
- **Safety**: No harmful recommendations
- **Hallucination Detection**: Verifiable claims only

## OPC Project Integration Matrix

| EvoAgentX Component | OPC Project | Integration Point |
|---------------------|-------------|-------------------|
| PubMedSearchTool | MetaForge | Systematic review pipeline |
| ClinicalTrialsTool | PharmaSim | Drug market simulation |
| DrugInfoTool | DrugMind | Drug safety profiling |
| EvoX Bridge | EvoX | Three-layer evolution |
| Medical Evolution | MediChat-RD | Rare disease diagnosis |
| HITL Module | KnowHealth | Multi-doctor review |

## Running Examples

```bash
cd /Users/apple/EvoAgentX
source venv/bin/activate

# Medical agent demo (tools only, no LLM needed)
python examples/medical/medical_agent_example.py

# EvoX integration demo
python examples/medical/evox_integration_example.py
```

## Configuration

Add to `.env`:
```bash
# Medical Database APIs
NCBI_API_KEY=your-ncbi-key
NCBI_EMAIL=your-email@domain.com

# OPC Project Paths
EVOX_PROJECT_PATH=/Users/apple/Desktop/OPC/evox
METAFORGE_PROJECT_PATH=/Users/apple/Desktop/OPC/metaforge
DRUGMIND_PROJECT_PATH=/Users/apple/Desktop/OPC/DrugMind
PHARMASIM_PROJECT_PATH=/Users/apple/Desktop/OPC/PharmaSim
```

## Contributing

To add new medical tools:
1. Create tool class in `evoagentx/tools/`
2. Extend `Tool` base class with proper `name`, `description`, `inputs`
3. Add to toolkit if appropriate
4. Create workflow in `Wonderful_workflow_corpus/`
5. Add example in `examples/medical/`
