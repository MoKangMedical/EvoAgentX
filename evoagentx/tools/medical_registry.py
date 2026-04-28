"""
Medical Tools Registry

Auto-registers all medical tools into EvoAgentX's tool system.
Makes medical tools discoverable by the workflow executor, agent manager,
and API server.

Usage:
    from evoagentx.tools.medical_registry import get_medical_tools, register_medical_tools
    tools = get_medical_tools()
"""


# Import medical tools (with fallback for missing deps)
MEDICAL_TOOLS = {}
MEDICAL_TOOLKITS = {}

try:
    from .pubmed_tool import PubMedFetchDetailTool, PubMedSearchTool, PubMedSearchToolkit
    MEDICAL_TOOLS["pubmed_search"] = PubMedSearchTool
    MEDICAL_TOOLS["pubmed_fetch_detail"] = PubMedFetchDetailTool
    MEDICAL_TOOLKITS["pubmed_toolkit"] = PubMedSearchToolkit
except ImportError:
    pass

try:
    from .clinicaltrials_tool import ClinicalTrialsDetailTool, ClinicalTrialsSearchTool, ClinicalTrialsToolkit
    MEDICAL_TOOLS["clinical_trials_search"] = ClinicalTrialsSearchTool
    MEDICAL_TOOLS["clinical_trials_detail"] = ClinicalTrialsDetailTool
    MEDICAL_TOOLKITS["clinical_trials_toolkit"] = ClinicalTrialsToolkit
except ImportError:
    pass

try:
    from .drugbank_tool import DrugInfoToolkit, DrugInteractionTool, DrugSearchTool, RxNormTool
    MEDICAL_TOOLS["drug_search"] = DrugSearchTool
    MEDICAL_TOOLS["drug_interaction_check"] = DrugInteractionTool
    MEDICAL_TOOLS["rxnorm_lookup"] = RxNormTool
    MEDICAL_TOOLKITS["drug_info_toolkit"] = DrugInfoToolkit
except ImportError:
    pass


def get_medical_tools() -> dict[str, type]:
    """Get all available medical tool classes."""
    return MEDICAL_TOOLS.copy()


def get_medical_toolkits() -> dict[str, type]:
    """Get all available medical toolkit classes."""
    return MEDICAL_TOOLKITS.copy()


def create_medical_tools(**kwargs) -> list:
    """Instantiate all available medical tools."""
    tools = []
    for name, cls in MEDICAL_TOOLS.items():
        try:
            tools.append(cls(**kwargs))
        except Exception:
            pass
    return tools


def create_medical_toolkit(**kwargs):
    """Create a combined medical toolkit with all tools."""
    from .tool import Toolkit

    tools = create_medical_tools(**kwargs)
    if not tools:
        return None

    return Toolkit(
        name="medical_toolkit",
        description=(
            "Comprehensive medical AI toolkit. Includes PubMed literature search, "
            "ClinicalTrials.gov trial lookup, FDA drug labels, drug interaction "
            "checking, and RxNorm drug normalization. For medical research, "
            "systematic reviews, drug development, and clinical evidence gathering."
        ),
        tools=tools
    )


def list_available_tools() -> str:
    """List all available medical tools with descriptions."""
    lines = ["Available Medical Tools:", ""]

    for name, cls in sorted(MEDICAL_TOOLS.items()):
        desc = getattr(cls, "description", "No description")
        # Truncate long descriptions
        if len(desc) > 80:
            desc = desc[:77] + "..."
        lines.append(f"  {name:30s} {desc}")

    lines.append("")
    lines.append("Available Medical Toolkits:")

    for name, cls in sorted(MEDICAL_TOOLKITS.items()):
        desc = getattr(cls, "description", "No description")
        if len(desc) > 80:
            desc = desc[:77] + "..."
        lines.append(f"  {name:30s} {desc}")

    return "\n".join(lines)
