# EvoAgentX Medical AI — FAQ

## General

### What is EvoAgentX Medical AI?
EvoAgentX Medical AI is an open-source, self-evolving agent framework for medical research. It connects to 4 major medical databases (PubMed, ClinicalTrials.gov, OpenFDA, RxNorm) and provides automated research pipelines with a 3-layer evolution engine.

### Do I need API keys?
No! All 7 medical tools work without API keys. API keys are optional for:
- OpenAI/Anthropic: For LLM-powered analysis
- NCBI: For higher PubMed rate limits (3→10 req/s)

### What databases does it connect to?
- PubMed (NCBI) — 39M+ biomedical articles
- ClinicalTrials.gov — 500K+ clinical trials
- OpenFDA — FDA drug labels and adverse events
- RxNorm — Drug normalization and relationships

### Is it free?
Yes, completely free and open-source (MIT License).

## Installation

### How do I install?
```bash
git clone https://github.com/MoKangMedical/EvoAgentX.git
cd EvoAgentX
python -m venv venv && source venv/bin/activate
pip install -e ".[tools]" -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Can I use Docker?
Yes!
```bash
docker build -t evoagentx .
docker run -p 8000:8000 evoagentx
```

### What Python version is required?
Python 3.10 or higher.

## Usage

### How do I search PubMed?
```bash
python evoagentx/cli.py search "CRISPR gene therapy" --max 10
```

### How do I check drug interactions?
```bash
python evoagentx/cli.py drugs --interaction warfarin,aspirin
```

### How do I run the full pipeline?
```bash
python examples/medical/end_to_end_demo.py --topic "your topic"
```

### How do I start the API server?
```bash
python evoagentx/cli.py serve --port 8000
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'docker'"
Install docker: `pip install docker`

### "ModuleNotFoundError: No module named 'google'"
Install google packages: `pip install google-api-python-client google-auth-oauthlib`

### "Rate limit exceeded"
Wait a few seconds and try again. Or add an NCBI API key for higher limits.

### "Connection timeout"
Check your internet connection. Some APIs may be blocked in certain regions.

### Tests failing
Run `make setup` to verify your environment.

## Contributing

### How do I contribute?
See [CONTRIBUTING-medical.md](CONTRIBUTING-medical.md) for detailed guidelines.

### Where do I report bugs?
Open a GitHub issue with the "Bug Report" template.

### How do I add a new medical tool?
1. Create `evoagentx/tools/my_tool.py`
2. Extend the `Tool` base class
3. Register in `medical_registry.py`
4. Add tests
5. Submit a PR

## Medical Safety

### Is this for clinical use?
No. This is a research tool. Always consult healthcare professionals for clinical decisions.

### How do you prevent hallucinations?
- All data comes from real APIs (PubMed, FDA, etc.)
- Every result includes source citations (PMID, NCT ID)
- Safety keyword blacklist prevents harmful advice
- Disclaimers are required in all medical outputs

### Can I use this for patient data?
This tool is not designed for patient data. For clinical use, ensure HIPAA compliance and consult your institution's IRB.
