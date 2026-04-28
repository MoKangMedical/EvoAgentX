# EvoAgentX Medical AI — Makefile
# =================================
# One-click operations for the self-evolving medical AI agent framework.
#
# Usage:
#   make setup       First-time setup (install + verify)
#   make test        Run all tests
#   make test-med    Run medical tests only
#   make demo        Run all demos
#   make demo-med    Run medical demo
#   make demo-e2e    Run end-to-end pipeline
#   make serve       Start API server
#   make status      Check system status
#   make clean       Clean generated files

.PHONY: setup test test-med demo demo-med demo-e2e serve status clean help

PYTHON = python3
VENV = venv
PIP = $(VENV)/bin/pip
PY = $(VENV)/bin/python

help:
	@echo "EvoAgentX Medical AI — Available Commands"
	@echo "=========================================="
	@echo ""
	@echo "  make setup       First-time setup (install deps + verify)"
	@echo "  make install     Install EvoAgentX in dev mode"
	@echo "  make test        Run all tests"
	@echo "  make test-med    Run medical tool tests only"
	@echo "  make demo        Run all demos"
	@echo "  make demo-med    Run medical tools demo"
	@echo "  make demo-e2e    Run end-to-end pipeline"
	@echo "  make demo-evox   Run EvoX bridge demo"
	@echo "  make serve       Start API server on port 8000"
	@echo "  make status      Check system status"
	@echo "  make search Q=   Quick PubMed search (make search Q='gene therapy')"
	@echo "  make drugs D=    Quick drug lookup (make drugs D=aspirin)"
	@echo "  make clean       Clean generated files"
	@echo ""

setup:
	@echo "=== EvoAgentX Setup ==="
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(PIP) install -e ".[tools]" -i https://pypi.tuna.tsinghua.edu.cn/simple -q 2>/dev/null || true
	@$(PIP) install docker html2text beautifulsoup4 selenium googlesearch-python \
		wikipedia ddgs telethon google-api-python-client google-auth-oauthlib \
		pymongo psycopg2-binary -i https://pypi.tuna.tsinghua.edu.cn/simple -q 2>/dev/null || true
	@$(PY) -c "from evoagentx.tools.pubmed_tool import PubMedSearchTool; print('[OK] PubMed')"
	@$(PY) -c "from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool; print('[OK] ClinicalTrials')"
	@$(PY) -c "from evoagentx.tools.drugbank_tool import DrugSearchTool; print('[OK] DrugInfo')"
	@$(PY) -c "from evoagentx.bridge import EvoXBridge; print('[OK] EvoX Bridge')"
	@echo "=== Setup Complete ==="

install:
	@$(PIP) install -e ".[tools]" -i https://pypi.tuna.tsinghua.edu.cn/simple

test:
	@$(PY) -m pytest tests/ -v --tb=short 2>&1 | tail -30

test-med:
	@$(PY) -m pytest tests/src/tools/test_medical_tools.py -v --tb=short

test-med-quick:
	@$(PY) -m pytest tests/src/tools/test_medical_tools.py -v -k "import or schema or registry" --tb=short

demo:
	@$(PY) evoagentx/cli.py demo all

demo-med:
	@$(PY) evoagentx/cli.py demo medical

demo-evox:
	@$(PY) evoagentx/cli.py demo evox

demo-e2e:
	@$(PY) examples/medical/end_to_end_demo.py

demo-workflow:
	@$(PY) examples/medical/evox_integration_example.py

serve:
	@echo "Starting EvoAgentX API on http://localhost:8000"
	@$(PY) -m uvicorn evoagentx.app.main:app --host 0.0.0.0 --port 8000 --reload

status:
	@$(PY) evoagentx/cli.py status

search:
	@$(PY) evoagentx/cli.py search "$(Q)"

drugs:
	@$(PY) evoagentx/cli.py drugs "$(D)"

trials:
	@$(PY) evoagentx/cli.py trials "$(T)"

clean:
	@rm -rf output/*.md
	@rm -rf .pytest_cache
	@rm -rf __pycache__
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned."
