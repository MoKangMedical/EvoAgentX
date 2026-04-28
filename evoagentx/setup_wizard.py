#!/usr/bin/env python3
"""
EvoAgentX Interactive Setup Wizard

Guides new users through first-time configuration:
1. Check Python version
2. Install dependencies
3. Configure API keys
4. Verify medical database connectivity
5. Run quick demo

Usage:
    python evoagentx/setup_wizard.py
"""

import shutil
import sys
from pathlib import Path


def print_banner():
    print()
    print("=" * 60)
    print("  EvoAgentX Medical AI — Setup Wizard")
    print("=" * 60)
    print()


def check_python():
    ver = sys.version_info
    ok = ver >= (3, 10)
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] Python {ver.major}.{ver.minor}.{ver.minor}")
    return ok


def check_deps():
    """Check if key dependencies are importable."""
    deps = [
        ("evoagentx.tools.pubmed_tool", "PubMedSearchTool", "PubMed tool"),
        ("evoagentx.tools.clinicaltrials_tool", "ClinicalTrialsSearchTool", "ClinicalTrials tool"),
        ("evoagentx.tools.drugbank_tool", "DrugSearchTool", "Drug info tool"),
        ("evoagentx.bridge", "EvoXBridge", "EvoX bridge"),
        ("evoagentx.benchmark.medical_benchmark", "MedicalBenchmark", "Benchmark suite"),
    ]
    ok = 0
    for module, cls, name in deps:
        try:
            import importlib
            mod = importlib.import_module(module)
            getattr(mod, cls)
            print(f"  [OK] {name}")
            ok += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
    return ok == len(deps)


def configure_env():
    """Interactive .env configuration."""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("  Created .env from .env.example")

    if not env_file.exists():
        print("  [WARN] No .env file found")
        return

    print()
    print("  API Key Configuration (press Enter to skip):")
    print("  ─────────────────────────────────────────────")

    keys = [
        ("OPENAI_API_KEY", "OpenAI API Key", "For LLM-powered analysis"),
        ("SILICONFLOW_API_KEY", "SiliconFlow Key", "Chinese LLM provider (alternative)"),
        ("NCBI_API_KEY", "NCBI API Key", "Higher PubMed rate limit (optional)"),
        ("NCBI_EMAIL", "NCBI Email", "Your email for PubMed API"),
    ]

    updates = {}
    for key, name, desc in keys:
        current = ""
        with open(env_file) as f:
            for line in f:
                if line.startswith(f"{key}=") and "your-" not in line.lower():
                    current = line.split("=", 1)[1].strip()

        if current:
            print(f"  [OK] {name}: already configured")
            continue

        val = input(f"  {name} ({desc}): ").strip()
        if val:
            updates[key] = val

    if updates:
        # Update .env
        lines = []
        with open(env_file) as f:
            lines = f.readlines()

        with open(env_file, "w") as f:
            for line in lines:
                key = line.split("=", 1)[0].strip()
                if key in updates:
                    f.write(f"{key}={updates[key]}\n")
                else:
                    f.write(line)

        print(f"\n  Updated {len(updates)} key(s) in .env")
    else:
        print("\n  No changes made. Medical tools work without API keys!")


def verify_connectivity():
    """Test medical database connectivity."""
    import urllib.request

    apis = [
        ("PubMed (NCBI)", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed&retmode=json"),
        ("ClinicalTrials.gov", "https://clinicaltrials.gov/api/v2/studies?pageSize=1"),
        ("OpenFDA", "https://api.fda.gov/drug/label.json?limit=1"),
        ("RxNorm", "https://rxnav.nlm.nih.gov/REST/drugs.json?name=aspirin"),
    ]

    ok = 0
    for name, url in apis:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EvoAgentX/0.1"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    print(f"  [OK] {name}")
                    ok += 1
                else:
                    print(f"  [WARN] {name}: HTTP {resp.status}")
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")

    return ok


def run_quick_demo():
    """Run a quick PubMed search to verify end-to-end."""
    print()
    print("  Running quick demo...")
    print("  ─────────────────────")
    try:
        from evoagentx.tools.pubmed_tool import PubMedSearchTool
        tool = PubMedSearchTool()
        result = tool.search(query="aspirin", max_results=1)
        if result["articles"]:
            art = result["articles"][0]
            print(f"  [OK] PubMed: {art['title'][:60]}...")
            print(f"       PMID: {art['pmid']} | {art['journal_abbr']}")
            return True
        else:
            print("  [WARN] No results returned")
            return False
    except Exception as e:
        print(f"  [FAIL] Demo error: {e}")
        return False


def print_next_steps():
    print()
    print("=" * 60)
    print("  Setup Complete! Next Steps:")
    print("=" * 60)
    print()
    print("  # Run the full end-to-end pipeline:")
    print("  python examples/medical/end_to_end_demo.py")
    print()
    print("  # Quick searches:")
    print("  python evoagentx/cli.py search 'gene therapy'")
    print("  python evoagentx/cli.py drugs pembrolizumab")
    print("  python evoagentx/cli.py trials 'CAR-T'")
    print()
    print("  # Run tests:")
    print("  make test-med")
    print()
    print("  # Start API server:")
    print("  make serve")
    print()
    print("  # Docker deployment:")
    print("  docker build -t evoagentx . && docker run -p 8000:8000 evoagentx")
    print()


def main():
    print_banner()

    print("Step 1: Python Version")
    py_ok = check_python()
    if not py_ok:
        print("  Please install Python 3.10+")
        return 1

    print()
    print("Step 2: Dependencies")
    deps_ok = check_deps()

    print()
    print("Step 3: API Configuration")
    configure_env()

    print()
    print("Step 4: Connectivity Check")
    apis_ok = verify_connectivity()

    demo_ok = False
    if apis_ok > 0:
        print()
        print("Step 5: Quick Demo")
        demo_ok = run_quick_demo()

    print_next_steps()

    score = sum([py_ok, deps_ok, apis_ok >= 3, demo_ok])
    print(f"  Health Score: {score}/4")
    return 0 if score >= 3 else 1


if __name__ == "__main__":
    sys.exit(main() or 0)
