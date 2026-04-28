# Contributing to EvoAgentX

Thank you for your interest in contributing to EvoAgentX! We welcome contributions from the community and are excited to see what you'll bring to the project. Whether you're fixing a bug, adding a feature, improving documentation, or helping with medical AI tools, your contribution matters.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Architecture Overview](#architecture-overview)
- [Code Style and Standards](#code-style-and-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Medical AI Guidelines](#medical-ai-guidelines)
- [Community](#community)

---

## Code of Conduct

Please be respectful and constructive in all interactions. We are committed to providing a welcoming and inclusive experience for everyone.

---

## Getting Started

1. **Fork** the repository on GitHub: [MoKangMedical/EvoAgentX](https://github.com/MoKangMedical/EvoAgentX)
2. **Clone** your fork locally
3. **Create a branch** for your work
4. **Make your changes** with tests
5. **Submit a Pull Request**

For first-time contributors, look for issues labeled [`good first issue`](https://github.com/MoKangMedical/EvoAgentX/labels/good%20first%20issue) or [`help wanted`](https://github.com/MoKangMedical/EvoAgentX/labels/help%20wanted).

---

## Development Setup

### Prerequisites

- **Python 3.10+** (3.11 or 3.12 recommended)
- **Git**
- A virtual environment tool (`venv`, `conda`, or similar)

### Step-by-Step Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/<your-username>/EvoAgentX.git
cd EvoAgentX

# 2. Add the upstream remote
git remote add upstream https://github.com/MoKangMedical/EvoAgentX.git

# 3. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 4. Install the project in editable mode with all extras
pip install -e '.[dev,medical,tools]'

# 5. Install pre-commit hooks (if configured)
pre-commit install

# 6. Verify the installation
python -c "import evoagentx; print('EvoAgentX installed successfully')"
pytest --version
ruff --version
```

### Dependency Extras

| Extra     | Purpose                                       |
|-----------|-----------------------------------------------|
| `dev`     | Development tools: pytest, ruff, coverage, mypy |
| `medical` | Medical AI tools: PubMed, ClinicalTrials, DrugBank clients |
| `tools`   | Additional tool integrations and utilities     |

### Environment Variables

Some features require API keys. Create a `.env` file in the project root (never commit this file):

```bash
# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Medical APIs (optional)
PUBMED_API_KEY=...
CLINICALTRIALS_API_KEY=...
DRUGBANK_API_KEY=...
```

---

## Architecture Overview

EvoAgentX is organized into several core modules. Understanding this structure will help you navigate the codebase and make effective contributions.

```
EvoAgentX/
├── evoagentx/
│   ├── agents/          # Agent definitions, base classes, and orchestration
│   ├── tools/           # Tool interfaces and implementations
│   │   ├── medical/     # Medical-specific tools (PubMed, ClinicalTrials, DrugBank)
│   │   └── ...
│   ├── workflow/        # Workflow engine for multi-step agent pipelines
│   ├── optimizers/      # Evolutionary and other optimization strategies
│   ├── rag/             # Retrieval-Augmented Generation components
│   ├── memory/          # Agent memory systems (short-term, long-term, vector stores)
│   ├── hitl/            # Human-in-the-loop interfaces and approval flows
│   ├── benchmark/       # Benchmarking and evaluation frameworks
│   └── core/            # Shared utilities, configs, and base abstractions
├── tests/               # Test suite (mirrors evoagentx/ structure)
├── docs/                # Documentation sources
├── examples/            # Example scripts and tutorials
└── setup.py             # Package configuration
```

### Key Design Principles

- **Modularity**: Each module has a clear responsibility and clean interfaces.
- **Extensibility**: New agents, tools, and optimizers can be added by subclassing base classes.
- **Composability**: Workflows compose agents and tools into reusable pipelines.
- **Safety**: Medical and sensitive tools include built-in validation and human-in-the-loop checkpoints.

### Adding a New Tool

1. Create a class that inherits from the base tool interface in `evoagentx/tools/`.
2. Implement required methods (`execute`, `validate_input`, etc.).
3. Register the tool in the appropriate module `__init__.py`.
4. Add tests in `tests/tools/`.
5. Document usage in your PR.

### Adding a New Agent

1. Subclass the appropriate base agent in `evoagentx/agents/`.
2. Define the agent's system prompt, tools, and behavior.
3. Add tests and documentation.

---

## Code Style and Standards

We enforce consistent code style using **Ruff** and follow Python best practices.

### Linting with Ruff

Ruff is our primary linter and formatter. Configuration is defined in `pyproject.toml` / `ruff.toml`.

```bash
# Check for linting issues
ruff check .

# Auto-fix fixable issues
ruff check --fix .

# Format code
ruff format .

# Check formatting without modifying files
ruff format --check .
```

**All code must pass `ruff check` and `ruff format` before submitting a PR.**

### Type Hints

- **All public functions and methods must have type annotations** for parameters and return values.
- Use `from __future__ import annotations` when appropriate.
- Prefer modern syntax: `list[str]` over `List[str]`, `X | Y` over `Optional[X]` (Python 3.10+).
- Use `TypedDict`, `Protocol`, or `dataclass` for complex structures.

```python
from __future__ import annotations

def search_pubmed(query: str, max_results: int = 10) -> list[dict[str, str]]:
    """Search PubMed for articles matching the query.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return.

    Returns:
        A list of dictionaries containing article metadata.
    """
    ...
```

### Docstrings

- Use **Google-style** docstrings for all public classes, functions, and methods.
- Include `Args`, `Returns`, `Raises`, and `Examples` sections where applicable.
- Keep docstrings concise but informative.

```python
class PubMedTool(BaseTool):
    """Tool for searching and retrieving articles from PubMed.

    This tool interfaces with the NCBI E-utilities API to search
    PubMed's database of biomedical literature.

    Attributes:
        api_key: Optional NCBI API key for higher rate limits.
        email: Contact email for NCBI (required by their policy).
    """

    def search(self, query: str, max_results: int = 20) -> list[Article]:
        """Search PubMed for articles matching the query.

        Args:
            query: PubMed search query (supports full query syntax).
            max_results: Maximum number of articles to retrieve.

        Returns:
            List of Article objects with title, abstract, PMID, etc.

        Raises:
            PubMedAPIError: If the API request fails.
            ValueError: If query is empty or max_results < 1.

        Example:
            >>> tool = PubMedTool(email="researcher@example.com")
            >>> articles = tool.search("CRISPR gene editing", max_results=5)
            >>> print(articles[0].title)
        """
        ...
```

### General Style Rules

- Maximum line length: **120 characters** (enforced by Ruff).
- Use descriptive variable names; avoid single-letter names except in comprehensions.
- Prefer `pathlib.Path` over `os.path` for file operations.
- Use `logging` instead of `print` for operational output.
- Keep imports organized: stdlib, third-party, local (Ruff handles this automatically).

---

## Testing Guidelines

We use **pytest** as our testing framework and aim for high test coverage.

### Running Tests

```bash
# Run the full test suite
pytest

# Run with verbose output
pytest -v

# Run tests for a specific module
pytest tests/agents/
pytest tests/tools/test_pubmed.py

# Run tests matching a pattern
pytest -k "test_search"

# Run with coverage report
pytest --cov=evoagentx --cov-report=term-missing

# Generate an HTML coverage report
pytest --cov=evogenx --cov-report=html
# Open htmlcov/index.html in your browser
```

### Writing Tests

- Place tests in the `tests/` directory, mirroring the source structure.
- Name test files `test_<module>.py`.
- Name test functions `test_<behavior>`.
- Use **fixtures** for common setup (`conftest.py`).
- Mock external API calls — **never hit real APIs in tests**.
- Use `pytest.mark.parametrize` for testing multiple inputs.

```python
import pytest
from unittest.mock import MagicMock, patch
from evoagentx.tools.medical.pubmed import PubMedTool

@pytest.fixture
def pubmed_tool():
    """Create a PubMedTool instance for testing."""
    return PubMedTool(email="test@example.com")

class TestPubMedTool:
    """Tests for the PubMedTool class."""

    def test_search_returns_results(self, pubmed_tool: PubMedTool) -> None:
        """Test that search returns a non-empty list for valid queries."""
        with patch.object(pubmed_tool, "_make_request") as mock_request:
            mock_request.return_value = [{"title": "Test Article", "pmid": "12345"}]
            results = pubmed_tool.search("test query")
            assert len(results) > 0
            assert results[0]["pmid"] == "12345"

    def test_search_empty_query_raises(self, pubmed_tool: PubMedTool) -> None:
        """Test that an empty query raises ValueError."""
        with pytest.raises(ValueError, match="query"):
            pubmed_tool.search("")

    @pytest.mark.parametrize("max_results", [1, 5, 50, 100])
    def test_search_respects_max_results(
        self, pubmed_tool: PubMedTool, max_results: int
    ) -> None:
        """Test that the number of results does not exceed max_results."""
        ...
```

### Coverage Requirements

- **Minimum coverage**: 80% for new code.
- **Critical paths** (medical tools, optimizers, workflow engine): aim for 95%+.
- Coverage is checked in CI; PRs that decrease overall coverage may be asked to add tests.

### Test Categories

Use pytest markers to categorize tests:

```bash
# Run only unit tests (fast, no external dependencies)
pytest -m "not integration and not slow"

# Run integration tests (may require API keys)
pytest -m integration

# Run slow tests
pytest -m slow
```

---

## Pull Request Process

### Before You Start

1. **Check existing issues/PRs** to avoid duplicate work.
2. **Open an issue** first for large changes to discuss the approach.
3. **Keep PRs focused** — one feature or fix per PR.

### PR Workflow

```bash
# 1. Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes and commit
git add .
git commit -m "feat: add support for XYZ"  # Use conventional commits

# 4. Push to your fork
git push origin feature/your-feature-name

# 5. Open a Pull Request on GitHub
```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

| Type       | Description                          |
|------------|--------------------------------------|
| `feat`     | New feature                          |
| `fix`      | Bug fix                              |
| `docs`     | Documentation changes                |
| `style`    | Code style changes (formatting)      |
| `refactor` | Code refactoring (no behavior change)|
| `test`     | Adding or updating tests             |
| `chore`    | Build process, dependencies, CI      |
| `perf`     | Performance improvements             |

Examples:
```
feat(tools): add DrugBank interaction checker
fix(agents): resolve memory leak in long-running workflows
docs(readme): update installation instructions
test(rag): add integration tests for vector store retrieval
```

### PR Checklist

Before submitting, ensure your PR meets these requirements:

- [ ] Code passes `ruff check` and `ruff format`
- [ ] Type annotations on all public APIs
- [ ] Docstrings on all public classes and functions
- [ ] Tests added for new functionality
- [ ] All existing tests pass (`pytest`)
- [ ] Coverage does not decrease
- [ ] CHANGELOG updated (for user-facing changes)
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow conventional commits
- [ ] PR description clearly explains the change

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Motivation
Why is this change needed? Link to related issues.

## Changes
- List of specific changes made
- Any design decisions and rationale

## Testing
How was this tested? What test cases were added?

## Screenshots (if applicable)
Visual changes should include before/after screenshots.

## Checklist
- [ ] Tests pass
- [ ] Code is linted and formatted
- [ ] Documentation updated
```

### Review Process

1. A maintainer will review your PR within **5 business days**.
2. Address review comments promptly; push new commits (don't force-push during review).
3. Once approved, a maintainer will merge your PR.
4. For first-time contributors, a maintainer may need to approve CI runs.

---

## Issue Guidelines

### Bug Reports

When reporting a bug, please include:

```markdown
## Bug Report

**Environment:**
- OS: [e.g., macOS 14.2, Ubuntu 22.04]
- Python version: [e.g., 3.11.5]
- EvoAgentX version: [e.g., 0.1.0]
- Relevant dependencies: [e.g., openai==1.x.x]

**Description:**
A clear description of the bug.

**Steps to Reproduce:**
1. ...
2. ...
3. ...

**Expected Behavior:**
What you expected to happen.

**Actual Behavior:**
What actually happened. Include full traceback if applicable.

**Additional Context:**
Screenshots, logs, or any other relevant information.
```

### Feature Requests

```markdown
## Feature Request

**Summary:**
A brief description of the feature.

**Motivation:**
Why is this feature needed? What problem does it solve?

**Proposed Solution:**
How you envision this working. Include API design if possible.

**Alternatives Considered:**
Other approaches you've thought about.

**Additional Context:**
Examples, references, or mockups.
```

### Security Issues

**Do not open public issues for security vulnerabilities.** Please email the maintainers directly or use GitHub's private vulnerability reporting feature.

---

## Medical AI Guidelines

EvoAgentX includes medical AI tools that interact with biomedical databases and can influence healthcare-related decisions. Contributors working on medical tools must follow these guidelines.

### Data Handling

- **No PHI in code or tests**: Never commit Protected Health Information (PHI), real patient data, or real clinical records — even in test fixtures.
- **Synthetic data only**: Use synthetic or publicly available datasets for testing (e.g., MIMIC-III demo data with proper credentialing, or fully synthetic records).
- **No persistent storage of medical queries by default**: Medical tool usage should not log or store query contents unless explicitly configured by the user with informed consent.
- **API key security**: Medical API keys (DrugBank, etc.) must never be committed to the repository. Use environment variables or secrets management.

### HIPAA Considerations

While EvoAgentX is a developer framework and not a covered entity, users may deploy it in HIPAA-regulated environments. We design with the following principles:

1. **Minimum Necessary Access**: Tools should request and process only the minimum data needed for the task.
2. **Audit Logging**: Medical tools should support optional audit logging for compliance, without logging actual patient data.
3. **Data Encryption**: When medical data is transmitted or stored, support encryption at rest and in transit.
4. **User Consent**: HITL (Human-in-the-Loop) checkpoints should be enforced for clinical decision support outputs.
5. **No Auto-Action**: Medical tools should never automatically execute clinical actions without explicit human approval.

### Medical Tool Development Standards

When contributing to `evoagentx/tools/medical/`:

- **Cite sources**: All medical information retrieved must include source attribution (PMID, NCT ID, etc.).
- **Uncertainty communication**: Tools should surface confidence levels and data freshness where available.
- **Scope disclaimers**: Tools should clearly indicate they are research aids, not clinical decision-making tools.
- **Rate limiting**: Respect API rate limits for medical databases (PubMed, ClinicalTrials.gov, DrugBank).
- **Validation**: Validate all inputs before making API calls. Sanitize outputs before returning to users.
- **Error handling**: Gracefully handle API failures, timeouts, and partial results.

### Testing Medical Tools

```bash
# Run medical tool tests specifically
pytest tests/tools/medical/ -v

# These tests should use mocked API responses
# Never make real API calls to medical databases in tests
```

### Regulatory Awareness

Contributors should be aware that:
- Medical AI systems may be subject to FDA regulation depending on intended use.
- The EU AI Act classifies medical AI as "high-risk."
- Different jurisdictions have varying requirements for AI in healthcare.

EvoAgentX provides building blocks — **the responsibility for regulatory compliance lies with the deployer.**

---

## Community

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions, ideas, and general discussion
- **Pull Requests**: For contributing code and documentation

### Recognition

All contributors are recognized in our release notes. Significant contributors may be invited to join as maintainers.

---

## Thank You!

Your contributions make EvoAgentX better for everyone. We appreciate your time, expertise, and dedication to advancing AI agent technology — especially in the critical domain of medical AI.

*— The EvoAgentX Team*
