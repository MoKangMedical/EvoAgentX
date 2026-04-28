# Changelog

All notable changes to EvoAgentX Medical AI Enhanced will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [0.2.0] - 2026-04-27

### Added

**Medical Tools (7 new tools)**
- `PubMedSearchTool` — PubMed literature search with MeSH support
- `PubMedFetchDetailTool` — Article detail fetch by PMID
- `ClinicalTrialsSearchTool` — ClinicalTrials.gov API integration
- `ClinicalTrialsDetailTool` — Trial protocol fetch by NCT ID
- `DrugSearchTool` — FDA drug label search via OpenFDA
- `DrugInteractionTool` — Drug-drug interaction via FAERS data
- `RxNormTool` — Drug normalization via NLM RxNorm

**Medical Workflows**
- `medical_literature_review/` — PubMed screening + evidence synthesis pipeline
- `drug_safety_analysis/` — FDA + trials + literature safety profile pipeline

**EvoX Bridge**
- `evoagentx.bridge` — Three-layer evolution bridge (Darwin + EvoPrompt + SEW)
- `MedicalEvolutionBridge` — Medical-specific evaluation (accuracy, traceability, safety)

**CLI**
- `evoagentx/cli.py` — Unified CLI with 9 subcommands
- `evoagentx-cli.py` — CLI entry point script
- Commands: setup, status, search, drugs, trials, demo, serve, test, evolve

**Infrastructure**
- `Dockerfile` — Multi-stage Docker build (base, deps, app, full)
- `docker-compose.yml` — API server, CLI, tests, dashboard services
- `.github/workflows/medical-ci.yaml` — Medical tools CI pipeline
- `Makefile` — One-click operations (setup, test, demo, serve)

**Testing**
- `tests/src/tools/test_medical_tools.py` — 30 unit tests (all passing)
- Coverage: import, schema, search, structured data, registry, bridge

**Caching & Rate Limiting**
- `evoagentx/tools/cache.py` — TTL-based medical API response cache
- `evoagentx/tools/rate_limiter.py` — Per-API rate limiting
- `evoagentx/tools/health.py` — Health check endpoint

**Benchmark**
- `evoagentx/benchmark/medical_benchmark.py` — Medical agent evaluation suite
- 15 built-in questions across medqa, drug_safety, clinical categories

**Documentation**
- `README-medical.md` — Medical AI capabilities overview
- `docs/MEDICAL_INTEGRATION.md` — Integration guide
- `CHANGELOG.md` — This file

### Changed
- `.gitignore` — Added output/ directory
- `evoagentx/bridge/__init__.py` — Lazy imports for optional dependencies
- `evoagentx/tools/medical_registry.py` — Auto-registration of medical tools

## [0.1.0] - 2025-xx-xx

### Initial Release (upstream EvoAgentX)
- Agent framework with workflow autoconstruction
- Built-in evaluation and self-evolution engine
- Plug-and-play LLM compatibility (OpenAI, LiteLLM, SiliconFlow)
- Comprehensive tools (search, browser, file, database, image)
- Memory module (short-term and long-term)
- Human-in-the-loop interactions
- RAG pipeline (readers, chunkers, embeddings, retrievers)
- Optimizers (AFlow, EvoPrompt, SEW, TextGrad, MAP-Elites)
- Benchmarks (GSM8K, HotpotQA, HumanEval, MBPP, LiveCodeBench)
