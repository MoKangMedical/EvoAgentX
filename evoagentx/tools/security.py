"""
Security Module for EvoAgentX Medical AI

Input validation, API key management, and safety checks.
"""

import os
import re

# Medical safety keywords that should NEVER appear in agent outputs
SAFETY_BLACKLIST = [
    "definitely cure", "guaranteed to work", "100% effective",
    "no side effects", "completely safe", "take this medication",
    "stop taking your", "don't see a doctor", "ignore symptoms",
    "self-diagnose", "self-medicate", "overdose",
]

# Required disclaimers for medical content
REQUIRED_DISCLAIMERS = [
    "consult", "physician", "doctor", "healthcare professional",
    "medical advice", "not a substitute",
]


def sanitize_query(query: str) -> str:
    """Sanitize user input for API queries."""
    # Remove potentially dangerous characters
    query = re.sub(r'[<>"\';\\]', '', query)
    # Limit length
    query = query[:500]
    # Strip whitespace
    query = query.strip()
    return query


def validate_api_key(key: str, provider: str = "openai") -> bool:
    """Validate API key format without making a call."""
    if not key or key.startswith("your-"):
        return False

    patterns = {
        "openai": r"^sk-[a-zA-Z0-9]{20,}$",
        "anthropic": r"^sk-ant-[a-zA-Z0-9]{20,}$",
        "ncbi": r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    }

    pattern = patterns.get(provider)
    if pattern:
        return bool(re.match(pattern, key))

    # Generic check: at least 10 chars, no spaces
    return len(key) >= 10 and ' ' not in key


def check_safety_violations(text: str) -> list:
    """Check for safety violations in medical content."""
    violations = []
    text_lower = text.lower()
    for keyword in SAFETY_BLACKLIST:
        if keyword.lower() in text_lower:
            violations.append(keyword)
    return violations


def has_disclaimer(text: str) -> bool:
    """Check if medical content has appropriate disclaimers."""
    text_lower = text.lower()
    return any(d in text_lower for d in REQUIRED_DISCLAIMERS)


def mask_api_key(key: str) -> str:
    """Mask API key for logging."""
    if not key or len(key) < 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"


def get_configured_keys() -> dict:
    """Get status of all configured API keys."""
    from dotenv import load_dotenv
    load_dotenv()

    keys = {
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic",
        "SILICONFLOW_API_KEY": "SiliconFlow",
        "DASHSCOPE_API_KEY": "DashScope",
        "NCBI_API_KEY": "NCBI PubMed",
        "EXA_API_KEY": "Exa Search",
    }

    result = {}
    for env_key, name in keys.items():
        val = os.getenv(env_key, "")
        configured = bool(val) and "your-" not in val.lower()
        result[name] = {
            "configured": configured,
            "masked": mask_api_key(val) if configured else None,
        }

    return result
