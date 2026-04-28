"""
EvoX + EvoAgentX Integration Example

Demonstrates how to use the EvoX bridge to evolve agents using
the three-layer evolution engine.

Layer 1 (Darwin): Fitness evaluation and natural selection
Layer 2 (EvoPrompt): Genetic algorithm prompt optimization
Layer 3 (SEW): Workflow structure evolution

Usage:
    cd /Users/apple/EvoAgentX
    source venv/bin/activate
    python examples/medical/evox_integration_example.py
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evoagentx.bridge import EvoXBridge, MedicalEvolutionBridge
from evoagentx.bridge import EvolutionResult, EvolutionSession


def demo_bridge_status():
    """Demo: Check EvoX bridge status."""
    print("=" * 60)
    print("EvoX Bridge Status")
    print("=" * 60)

    bridge = EvoXBridge()
    status = bridge.get_status()

    print(f"  EvoX Path:     {status['evox_path']}")
    print(f"  EvoX Available: {status['evox_available']}")
    print(f"  Darwin Path:   {status['darwin_path']}")
    print(f"  Darwin Available: {status['darwin_available']}")
    print(f"  Output Dir:    {status['output_dir']}")
    print()
    print("  Layer Status:")
    for layer, state in status['layers'].items():
        print(f"    {layer:12s}: {state}")
    print()


def demo_session_management():
    """Demo: Evolution session management."""
    print("=" * 60)
    print("Evolution Session Management")
    print("=" * 60)

    bridge = EvoXBridge()

    # Start session
    session_id = bridge.start_session("medical_research_agent")
    print(f"  Started session: {session_id}")

    # Simulate evolution results
    bridge.session.results = [
        EvolutionResult(
            round_num=1, layer="darwin", target="agent_config",
            before_score=45.0, after_score=52.0, improved=True,
            description="Darwin fitness evaluation: improved prompt clarity"
        ),
        EvolutionResult(
            round_num=2, layer="evoprompt", target="agent_prompt",
            before_score=52.0, after_score=58.0, improved=True,
            description="EvoPrompt: optimized search strategy prompt"
        ),
        EvolutionResult(
            round_num=3, layer="sew", target="workflow_structure",
            before_score=58.0, after_score=56.0, improved=False,
            description="SEW: added validation step (reverted - too slow)"
        ),
    ]
    bridge.session.total_rounds = 3
    bridge.session.successful = 2
    bridge.session.reverted = 1

    # Generate report
    report = bridge.generate_report()
    print()
    print(report)
    print()


def demo_evox_project_integration():
    """Demo: Integration with external EvoX project."""
    print("=" * 60)
    print("EvoX Project Integration")
    print("=" * 60)

    evox_path = Path(os.path.expanduser("~/Desktop/OPC/evox"))

    if not evox_path.exists():
        print(f"  EvoX project not found at: {evox_path}")
        print("  Clone from: https://github.com/MoKangMedical/evox")
        return

    print(f"  EvoX project found at: {evox_path}")

    # Check EvoX components
    components = {
        "darwin.py": "Darwin evolution engine",
        "evox_integration.py": "EvoAgentX integration bridge",
        "src/": "Source modules",
        "scripts/": "Utility scripts",
    }

    for path, desc in components.items():
        full_path = evox_path / path
        status = "OK" if full_path.exists() else "MISSING"
        print(f"    [{status}] {path:30s} - {desc}")

    print()

    # Check for integration file
    integration_file = evox_path / "evox_integration.py"
    if integration_file.exists():
        print("  EvoX integration bridge found!")
        print("  This enables direct communication between EvoX and EvoAgentX.")
    else:
        print("  EvoX integration bridge not found.")
        print("  Creating bridge will enable three-layer evolution.")

    print()


def demo_darwin_framework_integration():
    """Demo: Integration with Darwin framework."""
    print("=" * 60)
    print("Darwin Framework Integration")
    print("=" * 60)

    darwin_path = Path(os.path.expanduser("~/Desktop/OPC/darwin-framework"))

    if not darwin_path.exists():
        print(f"  Darwin framework not found at: {darwin_path}")
        return

    print(f"  Darwin framework found at: {darwin_path}")

    # Check key files
    for f in ["darwin.py", "README.md"]:
        full_path = darwin_path / f
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"    [OK] {f:20s} ({size:,d} bytes)")

    print()
    print("  Darwin's 8-dimension scoring can evaluate:")
    print("    1. Frontmatter规范 (max 8)")
    print("    2. 工作流清晰度 (max 15)")
    print("    3. 异常处理 (max 10)")
    print("    4. 确认检查点 (max 7)")
    print("    5. 指令具体性 (max 15)")
    print("    6. 路径完整性 (max 5)")
    print("    7. 架构合理性 (max 15)")
    print("    8. 实测输出质量 (max 25)")
    print()


def demo_medical_evolution():
    """Demo: Medical-specific agent evolution."""
    print("=" * 60)
    print("Medical Agent Evolution")
    print("=" * 60)

    bridge = MedicalEvolutionBridge()

    print("  Medical evolution bridge initialized.")
    print()
    print("  Medical evaluation criteria:")
    print("    - Clinical accuracy scoring")
    print("    - Evidence traceability (PMID citations)")
    print("    - Safety constraint checking")
    print("    - Hallucination detection")
    print()
    print("  Integration with OPC projects:")
    print("    - MetaForge: Systematic review workflows")
    print("    - DrugMind: Drug safety analysis")
    print("    - MediChat-RD: Rare disease diagnosis")
    print("    - PharmaSim: Clinical trial simulation")
    print()

    # Show example test cases
    example_cases = [
        {
            "question": "What is the evidence for gene therapy in spinal muscular atrophy?",
            "safety_keywords": ["definitely cure", "guaranteed"],
            "expected": "Should cite Zolgensma trials, mention FDA approval"
        },
        {
            "question": "Compare pembrolizumab vs nivolumab for NSCLC first-line",
            "safety_keywords": ["always better", "no side effects"],
            "expected": "Should reference KEYNOTE-024 and CheckMate-026"
        }
    ]

    print("  Example medical test cases:")
    for i, case in enumerate(example_cases, 1):
        print(f"    [{i}] {case['question'][:60]}...")
    print()


def main():
    """Run all integration demos."""
    print("=" * 60)
    print("EvoX + EvoAgentX Integration Demo")
    print("=" * 60)
    print()

    demo_bridge_status()
    demo_session_management()
    demo_evox_project_integration()
    demo_darwin_framework_integration()
    demo_medical_evolution()

    print("=" * 60)
    print("Integration Demo Complete")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Set up API keys in .env")
    print("  2. Run medical_agent_example.py to test tools")
    print("  3. Use EvoXBridge.evolve_agent() for evolution")
    print("  4. Create medical workflows for your use cases")
    print()


if __name__ == "__main__":
    main()
