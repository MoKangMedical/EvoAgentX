# EvoAgentX Medical AI — Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EvoAgentX Medical AI                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Presentation Layer                          │  │
│  │  ┌─────────┐  ┌───────────┐  ┌───────────┐  ┌─────────────┐  │  │
│  │  │   CLI   │  │ REST API  │  │ Dashboard │  │ Landing Page│  │  │
│  │  │ 9 cmds  │  │ FastAPI   │  │ HTML/JS   │  │ Static HTML │  │  │
│  │  └────┬────┘  └─────┬─────┘  └─────┬─────┘  └──────┬──────┘  │  │
│  └───────┴─────────────┴──────────────┴───────────────┴──────────┘  │
│                              │                                       │
│  ┌───────────────────────────┴───────────────────────────────────┐  │
│  │                    Application Layer                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │  │
│  │  │   Agents     │  │  Workflows   │  │   Benchmarks     │    │  │
│  │  │ Base/Action  │  │ Literature   │  │ MedQA/Drug/Clin  │    │  │
│  │  │ Medical      │  │ Drug Safety  │  │ 15 questions     │    │  │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘    │  │
│  └─────────┴─────────────────┴───────────────────┴───────────────┘  │
│                              │                                       │
│  ┌───────────────────────────┴───────────────────────────────────┐  │
│  │                    Service Layer                                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │  │
│  │  │    Cache     │  │ Rate Limiter │  │   Health Check   │    │  │
│  │  │ TTL-based    │  │ Token bucket │  │ API connectivity │    │  │
│  │  │ File+Memory  │  │ Per-API      │  │ Tool validation  │    │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│  ┌───────────────────────────┴───────────────────────────────────┐  │
│  │                    Data Layer                                   │  │
│  │  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────────┐   │  │
│  │  │ PubMed  │  │ Clinical │  │ OpenFDA │  │   RxNorm     │   │  │
│  │  │ (NCBI)  │  │ Trials   │  │ (FDA)   │  │   (NLM)      │   │  │
│  │  │ 39M+    │  │ 500K+    │  │ Labels  │  │ Normalize    │   │  │
│  │  └─────────┘  └──────────┘  └─────────┘  └──────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│  ┌───────────────────────────┴───────────────────────────────────┐  │
│  │                    Evolution Layer                              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │  │
│  │  │   Darwin     │  │  EvoPrompt   │  │      SEW         │    │  │
│  │  │ Config score │  │ Genetic algo │  │ Workflow struct  │    │  │
│  │  │ 8 dimensions │  │ Prompt optim │  │ Benchmark-driven │    │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘    │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Presentation Layer

| Component | Technology | Purpose |
|-----------|------------|---------|
| CLI | argparse | Command-line interface for all operations |
| REST API | FastAPI | HTTP endpoints for web/mobile clients |
| Dashboard | HTML/JS/CSS | Real-time search and monitoring UI |
| Landing Page | Static HTML | Project showcase and documentation |

### Application Layer

| Component | Purpose |
|-----------|---------|
| Agents | Base agent framework with medical specializations |
| Workflows | Pre-built pipelines for literature review and drug safety |
| Benchmarks | 15-question evaluation suite for medical agents |

### Service Layer

| Component | Purpose |
|-----------|---------|
| Cache | TTL-based response caching (file + memory) |
| Rate Limiter | Per-API token bucket rate limiting |
| Health Check | API connectivity and tool validation |

### Data Layer

| Database | API | Data | Rate Limit |
|----------|-----|------|------------|
| PubMed | NCBI E-utilities | 39M+ articles | 3-10 req/s |
| ClinicalTrials.gov | REST v2 | 500K+ trials | 10 req/s |
| OpenFDA | REST | Drug labels, FAERS | 4 req/s |
| RxNorm | REST | Drug normalization | 5 req/s |

### Evolution Layer

| Layer | Engine | Target | Method |
|-------|--------|--------|--------|
| 1 | Darwin | Agent config | 8-dimension fitness scoring |
| 2 | EvoPrompt | Prompts | Genetic algorithm optimization |
| 3 | SEW | Workflows | Structure evolution with benchmarks |

## Data Flow

```
User Query
    │
    ▼
CLI/API receives query
    │
    ▼
Rate Limiter checks quota
    │
    ▼
Cache checks for existing result
    │
    ├── Cache HIT → Return cached result
    │
    └── Cache MISS → Query medical API
                         │
                         ▼
                    Medical API responds
                         │
                         ▼
                    Cache stores result
                         │
                         ▼
                    Return to user
```

## Security Architecture

```
┌─────────────────────────────────────────────┐
│              Security Layers                 │
├─────────────────────────────────────────────┤
│  Input Validation                            │
│  ├─ Sanitize user queries                    │
│  ├─ Validate API key format                  │
│  └─ Prevent injection attacks                │
│                                              │
│  Rate Limiting                               │
│  ├─ Per-API token buckets                    │
│  └─ Prevent abuse                            │
│                                              │
│  Medical Safety                              │
│  ├─ Safety keyword blacklist                 │
│  ├─ Required disclaimers                     │
│  └─ Evidence traceability                    │
│                                              │
│  Data Privacy                                │
│  ├─ No telemetry                             │
│  ├─ Local cache only                         │
│  └─ API keys gitignored                      │
└─────────────────────────────────────────────┘
```
