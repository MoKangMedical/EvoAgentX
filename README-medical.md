# EvoAgentX — Medical AI Enhanced Fork

> Self-Evolving Medical AI Agent Framework | PubMed + ClinicalTrials.gov + FDA + EvoX Evolution

This is the **Medical AI Enhanced** fork of [EvoAgentX/EvoAgentX](https://github.com/EvoAgentX/EvoAgentX), integrating medical research tools with the three-layer evolution engine.

## What's New (Medical AI)

### Medical Tools (3 databases, 7 tools)

| Tool | Database | Capability |
|------|----------|------------|
| `PubMedSearchTool` | PubMed/NCBI | Biomedical literature search with MeSH support |
| `PubMedFetchDetailTool` | PubMed/NCArticle details by PMID |
| `ClinicalTrialsSearchTool` | ClinicalTrials.gov | Clinical trial search with phase/status filters |
| `ClinicalTrialsDetailTool` | ClinicalTrials.gov | Full trial protocol by NCT ID |
| `DrugSearchTool` | OpenFDA | FDA drug labels, indications, warnings |
| `DrugInteractionTool` | OpenFDA/FAERS | Drug-drug interaction via adverse event data |
| `RxNormTool` | RxNorm/NLM | Drug normalization, ingredients, relationships |

### Workflows (2 medical pipelines)

- **Medical Literature Review**: PubMed search -> PICOS screening -> data extraction -> evidence synthesis
- **Drug Safety Analysis**: FDA labels + clinical trials + safety literature -> integrated safety profile

### EvoX Bridge (3-layer evolution)

| Layer | Engine | Target |
|-------|--------|--------|
| 1 | Darwin | Agent configuration (8-dimension scoring) |
| 2 | EvoPrompt | Agent prompts (genetic algorithm) |
| 3 | SEW | Workflow structure (benchmark-driven) |

### OPC Project Integration

- **MetaForge**: Systematic review methodology
- **DrugMind**: Drug development pipeline
- **PharmaSim**: Clinical trial simulation
- **MediChat-RD**: Rare disease research

## Quick Start

```bash
# Clone and setup
git clone https://github.com/MoKangMedical/EvoAgentX.git
cd EvoAgentX
python -m venv venv && source venv/bin/activate
pip install -e ".[tools]" -i https://pypi.tuna.tsinghua.edu.cn/simple

# Verify installation
python evoagentx/cli.py setup

# Run demos (no API key needed for medical tools)
python evoagentx/cli.py demo medical    # Medical tools demo
python evoagentx/cli.py demo evox       # EvoX bridge demo
python evoagentx/cli.py demo all        # All demos

# End-to-end pipeline
python examples/medical/end_to_end_demo.py --topic "CRISPR gene therapy"
```

## CLI Usage

```bash
# Quick searches (no API key needed)
python evoagentx/cli.py search "rare disease gene therapy"
python evoagentx/cli.py drugs pembrolizumab
python evoagentx/cli.py drugs --interaction warfarin,aspirin
python evoagentx/cli.py trials "gene therapy" --status RECRUITING

# System
python evoagentx/cli.py status          # Check all connections
python evoagentx/cli.py test --medical-only  # Run medical tests
python evoagentx/cli.py serve --port 8000    # Start API server

# Makefile shortcuts
make setup       # First-time setup
make test-med    # Medical tests
make demo-e2e    # End-to-end pipeline
make status      # System status
```

## Architecture

```
EvoAgentX/
├── evoagentx/
│   ├── tools/
│   │   ├── pubmed_tool.py          # PubMed literature search
│   │   ├── clinicaltrials_tool.py  # ClinicalTrials.gov API
│   │   ├── drugbank_tool.py        # FDA drugs + interactions
│   │   └── medical_registry.py     # Auto-registration
│   ├── bridge/
│   │   └── __init__.py             # EvoX evolution bridge
│   ├── agents/                     # Agent framework
│   ├── workflow/                   # Workflow engine
│   ├── optimizers/                 # Evolution optimizers
│   ├── rag/                        # RAG pipeline
│   └── app/                        # FastAPI server
├── Wonderful_workflow_corpus/
│   ├── medical_literature_review/  # PubMed review workflow
│   └── drug_safety_analysis/       # Drug safety workflow
├── examples/medical/
│   ├── medical_agent_example.py    # Medical agent demo
│   ├── evox_integration_example.py # EvoX bridge demo
│   └── end_to_end_demo.py          # Full pipeline demo
├── tests/src/tools/
│   └── test_medical_tools.py       # 30 unit tests
├── Makefile                        # One-click operations
└── docs/MEDICAL_INTEGRATION.md     # Integration guide
```

## Test Results

```
30 passed, 0 failed (63.97s)
├── PubMed: 5 tests (import, schema, search, structured, detail)
├── ClinicalTrials: 5 tests (import, schema, search, filter, detail)
├── Drug: 7 tests (import, schema, search, structured, interaction, rxnorm)
├── Registry: 4 tests (tools, toolkits, create, list)
└── Bridge: 4 tests (import, status, session, medical)
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required for LLM-powered features
OPENAI_API_KEY=your-key

# Optional: enhanced rate limits
NCBI_API_KEY=your-ncbi-key
NCBI_EMAIL=your-email@domain.com

# Optional: Chinese LLM providers
SILICONFLOW_API_KEY=your-key
DASHSCOPE_API_KEY=your-key

# OPC Project paths
EVOX_PROJECT_PATH=/path/to/evox
METAFORGE_PROJECT_PATH=/path/to/metaforge
```

## Original EvoAgentX Features

For the full feature set (agents, workflows, optimizers, RAG, HITL, benchmarks), see:
- [Original README](./README.md)
- [Documentation](https://EvoAgentX.github.io/EvoAgentX/)
- [Medical Integration Guide](./docs/MEDICAL_INTEGRATION.md)

## License

MIT License — Same as upstream [EvoAgentX/EvoAgentX](https://github.com/EvoAgentX/EvoAgentX).
