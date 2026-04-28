# EvoAgentX Medical AI — Examples Gallery

## Quick Examples

### 1. PubMed Search
```python
from evoagentx.tools.pubmed_tool import PubMedSearchTool

tool = PubMedSearchTool()
results = tool(query="CRISPR gene therapy", max_results=5)
print(results)
```

### 2. Clinical Trials Search
```python
from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool

tool = ClinicalTrialsSearchTool()
results = tool(query="CAR-T cell therapy", status="RECRUITING", max_results=5)
print(results)
```

### 3. Drug Information
```python
from evoagentx.tools.drugbank_tool import DrugSearchTool, DrugInteractionTool

# Search drug
drug_tool = DrugSearchTool()
info = drug_tool(query="pembrolizumab", max_results=1)
print(info)

# Check interactions
interaction_tool = DrugInteractionTool()
result = interaction_tool(drug1="warfarin", drug2="aspirin")
print(result)
```

### 4. End-to-End Pipeline
```python
from evoagentx.tools.pubmed_tool import PubMedSearchTool
from evoagentx.tools.clinicaltrials_tool import ClinicalTrialsSearchTool
from evoagentx.tools.drugbank_tool import DrugSearchTool

# Search all databases
pubmed = PubMedSearchTool()
trials = ClinicalTrialsSearchTool()
drugs = DrugSearchTool()

query = "rare disease gene therapy"

lit = pubmed.search(query, max_results=5)
trials_data = trials.search(query, max_results=5)
drug_data = drugs.search_label("zolgensma", max_results=1)

# Generate report
print(f"## Literature: {lit['total_count']} articles")
print(f"## Trials: {trials_data['total_count']} trials")
print(f"## Drugs: {len(drug_data)} found")
```

### 5. Async Concurrent Search
```python
import asyncio
from evoagentx.tools.async_medical import AsyncMedicalSearcher

async def main():
    searcher = AsyncMedicalSearcher()
    results = await searcher.search_all("CRISPR gene therapy")
    
    print(f"PubMed: {results['pubmed']['total_count']} articles")
    print(f"Trials: {results['trials']['total_count']} trials")

asyncio.run(main())
```

### 6. EvoX Evolution
```python
from evoagentx.bridge import EvoXBridge

bridge = EvoXBridge()
print(bridge.get_status())

session_id = bridge.start_session("my-agent")
print(f"Session: {session_id}")
```

### 7. Medical Benchmark
```python
from evoagentx.benchmark.medical_benchmark import MedicalBenchmark

bench = MedicalBenchmark()
print(f"Categories: {bench.list_categories()}")
print(f"Total questions: {len(bench.questions)}")

# Evaluate an agent
def my_agent(question):
    return "A"  # Dummy agent

results = bench.evaluate(my_agent, category="medqa", n=3)
print(f"Accuracy: {results.accuracy:.1%}")
```

### 8. Cache Usage
```python
from evoagentx.tools.cache import get_cache

cache = get_cache()

# Cache a result
cache.set("pubmed", "test query", {"results": [...]})

# Get cached result
cached = cache.get("pubmed", "test query")
print(f"Cached: {cached}")

# Get or fetch
result = cache.get_or_fetch(
    "pubmed", "new query",
    lambda: pubmed.search("new query")
)
```

### 9. Health Check
```python
from evoagentx.tools.health import get_health, get_detailed_health

# Basic health
health = get_health()
print(f"Status: {health['status']}")

# Detailed health
detailed = get_detailed_health()
for api, status in detailed['apis'].items():
    print(f"  {api}: {status['status']}")
```

### 10. CLI Usage
```bash
# Setup
python evoagentx/cli.py setup

# Status
python evoagentx/cli.py status

# Search
python evoagentx/cli.py search "gene therapy" --max 5
python evoagentx/cli.py drugs pembrolizumab
python evoagentx/cli.py trials "CAR-T" --status RECRUITING

# Demo
python evoagentx/cli.py demo medical
python evoagentx/cli.py demo evox
python evoagentx/cli.py demo all

# Serve
python evoagentx/cli.py serve --port 8000
```
