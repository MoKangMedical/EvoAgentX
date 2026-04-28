# EvoAgentX Medical AI — API Reference

## Medical Tools API

### PubMedSearchTool

Search PubMed for biomedical literature.

```python
from evoagentx.tools.pubmed_tool import PubMedSearchTool

tool = PubMedSearchTool(email="your@email.com", api_key="optional")

# Search
results = tool.search(
    query="rare disease AND gene therapy[tiab]",
    max_results=10,
    sort="relevance"  # or "date"
)

# Returns:
{
    "query": "rare disease AND gene therapy[tiab]",
    "total_count": 23068,
    "returned": 10,
    "articles": [
        {
            "pmid": "39392045",
            "title": "...",
            "abstract": "...",
            "authors": ["Author 1", "Author 2"],
            "journal": "Journal Name",
            "journal_abbr": "J Name",
            "pub_date": "2024-Oct",
            "doi": "10.xxx/xxx",
            "mesh_terms": ["Term1", "Term2"],
            "url": "https://pubmed.ncbi.nlm.nih.gov/39392045/"
        },
        ...
    ]
}
```

### ClinicalTrialsSearchTool

Search ClinicalTrials.gov for clinical trials.

```python
from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool

tool = ClinicalTrialsSearchTool()

results = tool.search(
    query="gene therapy",
    status="RECRUITING",  # Optional filter
    phase="PHASE3",       # Optional filter
    max_results=10
)

# Returns:
{
    "query": "gene therapy",
    "total_count": 156,
    "returned": 10,
    "trials": [
        {
            "nct_id": "NCT06615206",
            "title": "...",
            "status": "RECRUITING",
            "phases": ["PHASE3"],
            "conditions": ["Disease"],
            "interventions": ["Drug"],
            "sponsor": "Company",
            "enrollment": 100,
            "study_type": "INTERVENTIONAL",
            "start_date": "2024-01",
            "completion_date": "2025-12",
            "url": "https://clinicaltrials.gov/study/NCT06615206"
        },
        ...
    ]
}
```

### DrugSearchTool

Search FDA drug labels.

```python
from evoagentx.tools.drugbank_tool import DrugSearchTool

tool = DrugSearchTool()

drugs = tool.search_label(
    query="pembrolizumab",
    max_results=3
)

# Returns:
[
    {
        "brand_name": "KEYTRUDA",
        "generic_name": "PEMBROLIZUMAB",
        "manufacturer": "Merck Sharp & Dohme LLC",
        "route": "INTRAVENOUS",
        "substance_name": "PEMBROLIZUMAB",
        "indications": "...",
        "warnings": "...",
        "dosage": "...",
        "contraindications": "...",
        "adverse_reactions": "...",
        "drug_interactions": "..."
    },
    ...
]
```

### DrugInteractionTool

Check drug-drug interactions via FDA FAERS.

```python
from evoagentx.tools.drugbank_tool import DrugInteractionTool

tool = DrugInteractionTool()

result = tool(drug1="warfarin", drug2="aspirin")

# Returns formatted string with:
# - Total co-reported events
# - Most frequent reactions
# - Disclaimer about causality
```

### RxNormTool

Drug normalization via NLM RxNorm.

```python
from evoagentx.tools.drugbank_tool import RxNormTool

tool = RxNormTool()

# Search
result = tool(drug_name="ibuprofen", operation="search")

# Get ingredients
result = tool(drug_name="metformin", operation="ingredients")

# Get related drugs
result = tool(drug_name="aspirin", operation="related")
```

## REST API Endpoints

When running `evoagentx serve`, the following endpoints are available:

### Health Check
```
GET /api/medical/health
GET /api/medical/health/detailed
```

### PubMed Search
```
GET /api/medical/search?q=CRISPR&max=5&sort=relevance
```

### Clinical Trials
```
GET /api/medical/trials?q=gene+therapy&status=RECRUITING&phase=PHASE3&max=5
```

### Drug Search
```
GET /api/medical/drugs?q=pembrolizumab&max=3
```

### Drug Interactions
```
GET /api/medical/interactions?drug1=warfarin&drug2=aspirin
```

### RxNorm Lookup
```
GET /api/medical/rxnorm?name=aspirin&op=search
```

### Statistics
```
GET /api/medical/stats
```

### Benchmark Info
```
GET /api/medical/benchmark
```

## EvoX Bridge API

```python
from evoagentx.bridge import EvoXBridge, MedicalEvolutionBridge

# Standard bridge
bridge = EvoXBridge()
status = bridge.get_status()
session_id = bridge.start_session("my-agent")
session = bridge.evolve_agent(agent, rounds=3)
report = bridge.generate_report()

# Medical bridge
med_bridge = MedicalEvolutionBridge()
results = med_bridge.evaluate_medical_agent(agent, test_cases)
```

## Cache API

```python
from evoagentx.tools.cache import get_cache

cache = get_cache()

# Get/Set
cache.set("pubmed", "query", data, ttl=3600)
cached = cache.get("pubmed", "query")

# Get or fetch
result = cache.get_or_fetch("pubmed", "query", fetch_fn)

# Stats
stats = cache.stats()
# {"hits": 10, "misses": 2, "hit_rate": "83.3%", ...}

# Cleanup
removed = cache.cleanup()
cache.clear()
```

## Rate Limiter API

```python
from evoagentx.tools.rate_limiter import get_limiter

limiter = get_limiter()

# Wait for rate limit
limiter.wait("pubmed")  # Blocks until safe
limiter.wait("clinicaltrials")

# Stats
stats = limiter.get_stats()
# {"pubmed": 15, "clinicaltrials": 8}
```
