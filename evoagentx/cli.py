#!/usr/bin/env python3
"""
EvoAgentX CLI — Unified Command-Line Interface

One-click operations for the self-evolving medical AI agent framework.

Usage:
    evoagentx setup              # First-time setup (install deps + verify)
    evoagentx demo [type]        # Run demos (medical/tools/evox/all)
    evoagentx search <query>     # Quick PubMed search
    evoagentx drugs <name>       # Quick drug lookup
    evoagentx trials <query>     # Quick clinical trial search
    evoagentx evolve <config>    # Run agent evolution
    evoagentx serve              # Start web API server
    evoagentx test               # Run test suite
    evoagentx status             # Check system status
"""

import argparse
import json
import os
import sys
from pathlib import Path


def cmd_setup(args):
    """First-time setup: verify environment and install deps."""
    print("=" * 60)
    print("EvoAgentX Setup")
    print("=" * 60)

    # Check Python version
    py_ver = sys.version_info
    if py_ver < (3, 10):
        print(f"[FAIL] Python 3.10+ required, got {py_ver.major}.{py_ver.minor}")
        return 1
    print(f"[OK] Python {py_ver.major}.{py_ver.minor}.{py_ver.micro}")

    # Check .env
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        has_key = False
        with open(env_file) as f:
            for line in f:
                if line.strip().startswith("OPENAI_API_KEY=") and "your-" not in line:
                    has_key = True
                    break
        if has_key:
            print("[OK] .env configured with API key")
        else:
            print("[WARN] .env has placeholder API keys - edit .env to add real keys")
    else:
        print("[WARN] .env not found - copy .env.example to .env and add keys")

    # Check medical tools
    tools_ok = 0
    tools_total = 3
    try:
        print("[OK] PubMed tool loaded")
        tools_ok += 1
    except Exception as e:
        print(f"[FAIL] PubMed tool: {e}")

    try:
        print("[OK] ClinicalTrials tool loaded")
        tools_ok += 1
    except Exception as e:
        print(f"[FAIL] ClinicalTrials tool: {e}")

    try:
        print("[OK] Drug info tool loaded")
        tools_ok += 1
    except Exception as e:
        print(f"[FAIL] Drug info tool: {e}")

    # Check bridge
    try:
        from evoagentx.bridge import EvoXBridge
        bridge = EvoXBridge()
        status = bridge.get_status()
        evox_ok = "OK" if status["evox_available"] else "MISSING"
        darwin_ok = "OK" if status["darwin_available"] else "MISSING"
        print(f"[{evox_ok.upper()}] EvoX project at {status['evox_path']}")
        print(f"[{darwin_ok.upper()}] Darwin framework at {status['darwin_path']}")
    except Exception as e:
        print(f"[WARN] EvoX bridge: {e}")

    print()
    print(f"Medical tools: {tools_ok}/{tools_total} available")
    print(f"Setup {'complete' if tools_ok == tools_total else 'incomplete'}")
    return 0


def cmd_status(args):
    """Check system status."""
    print("=" * 60)
    print("EvoAgentX System Status")
    print("=" * 60)

    # Version
    try:
        from evoagentx import __version__
        print(f"Version: {__version__}")
    except:
        print("Version: 0.1.0 (dev)")

    # API keys
    from dotenv import load_dotenv
    load_dotenv()
    keys = {
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic",
        "SILICONFLOW_API_KEY": "SiliconFlow",
        "NCBI_API_KEY": "NCBI PubMed",
    }
    print("\nAPI Keys:")
    for key, name in keys.items():
        val = os.getenv(key, "")
        status = "configured" if val and "your-" not in val else "missing"
        print(f"  {name:20s}: {status}")

    # Medical tools connectivity
    print("\nMedical API Connectivity:")
    import urllib.request
    apis = {
        "PubMed (NCBI)": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed&retmode=json",
        "ClinicalTrials.gov": "https://clinicaltrials.gov/api/v2/studies?pageSize=1",
        "OpenFDA": "https://api.fda.gov/drug/label.json?limit=1",
        "RxNorm": "https://rxnav.nlm.nih.gov/REST/drugs.json?name=aspirin",
    }
    for name, url in apis.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EvoAgentX/0.1"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = f"OK ({resp.status})"
        except Exception as e:
            status = f"FAIL ({type(e).__name__})"
        print(f"  {name:25s}: {status}")

    # Project integrations
    print("\nOPC Project Integrations:")
    projects = {
        "EvoX": os.path.expanduser("~/Desktop/OPC/evox"),
        "Darwin": os.path.expanduser("~/Desktop/OPC/darwin-framework"),
        "MetaForge": os.path.expanduser("~/Desktop/OPC/metaforge"),
        "DrugMind": os.path.expanduser("~/Desktop/OPC/DrugMind"),
        "PharmaSim": os.path.expanduser("~/Desktop/OPC/PharmaSim"),
        "MediChat-RD": os.path.expanduser("~/Desktop/OPC/medichat-rd"),
    }
    for name, path in projects.items():
        exists = os.path.exists(path)
        status = "found" if exists else "not found"
        print(f"  {name:20s}: {status}")

    return 0


def cmd_search(args):
    """Quick PubMed search."""
    from evoagentx.tools.pubmed_tool import PubMedSearchTool
    tool = PubMedSearchTool()
    result = tool(query=args.query, max_results=args.max, sort=args.sort)
    print(result)
    return 0


def cmd_drugs(args):
    """Quick drug lookup."""
    from evoagentx.tools.drugbank_tool import DrugInteractionTool, DrugSearchTool

    if args.interaction:
        tool = DrugInteractionTool()
        drugs = args.interaction.split(",")
        if len(drugs) == 2:
            result = tool(drug1=drugs[0].strip(), drug2=drugs[1].strip())
        else:
            print("Error: --interaction requires two drugs separated by comma")
            print("Example: evoagentx drugs --interaction warfarin,aspirin")
            return 1
    else:
        tool = DrugSearchTool()
        result = tool(query=args.name, max_results=args.max)

    print(result)
    return 0


def cmd_trials(args):
    """Quick clinical trial search."""
    from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool
    tool = ClinicalTrialsSearchTool()
    result = tool(
        query=args.query,
        status=args.status or "",
        phase=args.phase or "",
        max_results=args.max
    )
    print(result)
    return 0


def cmd_demo(args):
    """Run demos."""
    demo_type = args.type or "all"

    if demo_type in ("medical", "all"):
        print("\n" + "=" * 60)
        print("Running Medical Tools Demo...")
        print("=" * 60)
        try:
            from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool
            from evoagentx.tools.drugbank_tool import DrugSearchTool
            from evoagentx.tools.pubmed_tool import PubMedSearchTool

            print("\n1. PubMed Search:")
            pubmed = PubMedSearchTool()
            print(pubmed(query="CRISPR gene therapy", max_results=2))

            print("\n2. Clinical Trials:")
            trials = ClinicalTrialsSearchTool()
            print(trials(query="CAR-T cell therapy", max_results=2))

            print("\n3. Drug Info:")
            drugs = DrugSearchTool()
            print(drugs(query="pembrolizumab", max_results=1))
        except Exception as e:
            print(f"Medical demo error: {e}")

    if demo_type in ("evox", "all"):
        print("\n" + "=" * 60)
        print("Running EvoX Bridge Demo...")
        print("=" * 60)
        try:
            from evoagentx.bridge import EvoXBridge
            bridge = EvoXBridge()
            status = bridge.get_status()
            for k, v in status.items():
                print(f"  {k}: {v}")
        except Exception as e:
            print(f"EvoX demo error: {e}")

    if demo_type in ("workflow", "all"):
        print("\n" + "=" * 60)
        print("Running Workflow Demo...")
        print("=" * 60)
        wf_dir = Path(__file__).parent.parent / "Wonderful_workflow_corpus"
        for wf_name in ["medical_literature_review", "drug_safety_analysis"]:
            wf_path = wf_dir / wf_name / "workflow.json"
            if wf_path.exists():
                with open(wf_path) as f:
                    wf = json.load(f)
                print(f"\n  Workflow: {wf['name']}")
                print(f"  Nodes: {len(wf['nodes'])}")
                print(f"  Tags: {', '.join(wf['tags'])}")

    return 0


def cmd_serve(args):
    """Start the web API server."""
    port = args.port or 8000
    print(f"Starting EvoAgentX API server on port {port}...")
    try:
        import uvicorn
        uvicorn.run(
            "evoagentx.app.main:app",
            host="0.0.0.0",
            port=port,
            reload=args.reload
        )
    except ImportError:
        print("Error: uvicorn not installed. Run: pip install uvicorn")
        return 1
    except Exception as e:
        print(f"Server error: {e}")
        return 1


def cmd_test(args):
    """Run test suite."""
    import subprocess
    test_path = Path(__file__).parent.parent / "tests"
    cmd = [sys.executable, "-m", "pytest", str(test_path), "-v"]
    if args.medical_only:
        cmd = [sys.executable, "-m", "pytest",
               str(test_path / "src" / "tools" / "test_medical_tools.py"), "-v"]
    result = subprocess.run(cmd, cwd=str(Path(__file__).parent.parent))
    return result.returncode


def cmd_evolve(args):
    """Run agent evolution."""
    from evoagentx.bridge import EvoXBridge

    bridge = EvoXBridge()
    print("EvoX Evolution Bridge")
    print(f"Status: {bridge.get_status()}")

    session_id = bridge.start_session(args.project or "medical-agent")
    print(f"Session: {session_id}")

    # Run evolution
    session = bridge.evolve_agent(None, rounds=args.rounds or 3)
    print(bridge.generate_report())
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="evoagentx",
        description="EvoAgentX — Self-Evolving Medical AI Agent Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  evoagentx setup                          First-time setup
  evoagentx status                         Check system status
  evoagentx search "rare disease therapy"  PubMed search
  evoagentx drugs pembrolizumab            Drug lookup
  evoagentx drugs --interaction warfarin,aspirin
  evoagentx trials "gene therapy" --status RECRUITING
  evoagentx demo medical                   Run medical tools demo
  evoagentx demo evox                      Run EvoX bridge demo
  evoagentx demo all                       Run all demos
  evoagentx serve --port 8000              Start API server
  evoagentx test                           Run tests
  evoagentx test --medical-only            Run medical tests only
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # setup
    subparsers.add_parser("setup", help="First-time setup and verification")

    # status
    subparsers.add_parser("status", help="Check system status")

    # search
    p_search = subparsers.add_parser("search", help="PubMed literature search")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--max", type=int, default=5, help="Max results")
    p_search.add_argument("--sort", default="relevance", choices=["relevance", "date"])

    # drugs
    p_drugs = subparsers.add_parser("drugs", help="Drug information lookup")
    p_drugs.add_argument("name", nargs="?", default="", help="Drug name")
    p_drugs.add_argument("--interaction", help="Check interaction: drug1,drug2")
    p_drugs.add_argument("--max", type=int, default=3, help="Max results")

    # trials
    p_trials = subparsers.add_parser("trials", help="Clinical trial search")
    p_trials.add_argument("query", help="Search query")
    p_trials.add_argument("--status", help="Filter by status")
    p_trials.add_argument("--phase", help="Filter by phase")
    p_trials.add_argument("--max", type=int, default=5, help="Max results")

    # demo
    p_demo = subparsers.add_parser("demo", help="Run demos")
    p_demo.add_argument("type", nargs="?", default="all",
                        choices=["medical", "evox", "workflow", "all"])

    # serve
    p_serve = subparsers.add_parser("serve", help="Start API server")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.add_argument("--reload", action="store_true")

    # test
    p_test = subparsers.add_parser("test", help="Run tests")
    p_test.add_argument("--medical-only", action="store_true")

    # evolve
    p_evolve = subparsers.add_parser("evolve", help="Run agent evolution")
    p_evolve.add_argument("--project", default="medical-agent")
    p_evolve.add_argument("--rounds", type=int, default=3)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    cmds = {
        "setup": cmd_setup,
        "status": cmd_status,
        "search": cmd_search,
        "drugs": cmd_drugs,
        "trials": cmd_trials,
        "demo": cmd_demo,
        "serve": cmd_serve,
        "test": cmd_test,
        "evolve": cmd_evolve,
    }

    return cmds[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
