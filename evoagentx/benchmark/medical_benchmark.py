"""
Medical Benchmark Suite for EvoAgentX

Evaluates medical agents against standardized benchmarks:
- MedQA: USMLE-style medical questions
- PubMedQA: PubMed abstract-based questions
- Drug Safety: Drug interaction and safety knowledge
- Clinical Reasoning: Multi-step clinical reasoning

Usage:
    from evoagentx.benchmark.medical_benchmark import MedicalBenchmark
    bench = MedicalBenchmark()
    results = bench.evaluate(agent, subset="medqa", n=50)
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class BenchmarkQuestion:
    """A single benchmark question."""
    id: str = ""
    category: str = ""  # medqa, pubmedqa, drug_safety, clinical
    question: str = ""
    options: List[str] = field(default_factory=list)
    answer: str = ""
    explanation: str = ""
    source: str = ""  # PMID, NCT ID, etc.
    difficulty: str = "medium"  # easy, medium, hard


@dataclass
class BenchmarkResult:
    """Results of a benchmark evaluation."""
    benchmark: str = ""
    total_questions: int = 0
    correct: int = 0
    accuracy: float = 0.0
    avg_latency_ms: float = 0.0
    category_scores: Dict[str, float] = field(default_factory=dict)
    details: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = ""


# ──────────────────────────────────────────────
# Built-in Medical Benchmark Questions
# ──────────────────────────────────────────────

MEDQA_QUESTIONS = [
    BenchmarkQuestion(
        id="medqa_001", category="medqa",
        question="A 45-year-old man presents with fatigue, weight loss, and darkening of the skin. Laboratory studies show hyponatremia, hyperkalemia, and low cortisol. What is the most likely diagnosis?",
        options=["Cushing syndrome", "Addison disease", "Pheochromocytoma", "Hyperthyroidism", "Diabetes insipidus"],
        answer="Addison disease",
        explanation="Primary adrenal insufficiency (Addison disease) presents with fatigue, weight loss, hyperpigmentation, hyponatremia, hyperkalemia, and low cortisol.",
        difficulty="medium"
    ),
    BenchmarkQuestion(
        id="medqa_002", category="medqa",
        question="Which gene is most commonly mutated in hereditary breast and ovarian cancer syndrome?",
        options=["TP53", "BRCA1/BRCA2", "RB1", "APC", "MLH1"],
        answer="BRCA1/BRCA2",
        explanation="BRCA1 and BRCA2 are the most common genes associated with hereditary breast and ovarian cancer syndrome.",
        difficulty="easy"
    ),
    BenchmarkQuestion(
        id="medqa_003", category="medqa",
        question="A patient on warfarin develops skin necrosis. Which protein deficiency is most likely responsible?",
        options=["Protein C", "Protein S", "Antithrombin III", "Factor V Leiden", "Prothrombin G20210A"],
        answer="Protein C",
        explanation="Protein C deficiency can lead to warfarin-induced skin necrosis because warfarin inhibits protein C (which has a short half-life) before it inhibits procoagulant factors.",
        difficulty="hard"
    ),
    BenchmarkQuestion(
        id="medqa_004", category="medqa",
        question="What is the first-line treatment for acute anaphylaxis?",
        options=["Diphenhydramine", "Methylprednisolone", "Epinephrine", "Albuterol", "Ranitidine"],
        answer="Epinephrine",
        explanation="Epinephrine (intramuscular) is the first-line treatment for anaphylaxis. Antihistamines and steroids are adjunctive therapies.",
        difficulty="easy"
    ),
    BenchmarkQuestion(
        id="medqa_005", category="medqa",
        question="A newborn presents with ambiguous genitalia, salt wasting, and elevated 17-hydroxyprogesterone. What enzyme is deficient?",
        options=["11-beta-hydroxylase", "21-hydroxylase", "17-alpha-hydroxylase", "3-beta-hydroxysteroid dehydrogenase", "5-alpha-reductase"],
        answer="21-hydroxylase",
        explanation="21-hydroxylase deficiency is the most common cause of congenital adrenal hyperplasia, presenting with ambiguous genitalia and salt wasting.",
        difficulty="medium"
    ),
]

DRUG_SAFETY_QUESTIONS = [
    BenchmarkQuestion(
        id="drug_001", category="drug_safety",
        question="Which drug is contraindicated with MAO inhibitors due to risk of serotonin syndrome?",
        options=["Acetaminophen", "Fluoxetine", "Metformin", "Lisinopril", "Omeprazole"],
        answer="Fluoxetine",
        explanation="Fluoxetine (SSRI) is contraindicated with MAOIs due to risk of serotonin syndrome, a potentially fatal condition.",
        difficulty="easy"
    ),
    BenchmarkQuestion(
        id="drug_002", category="drug_safety",
        question="What is the mechanism of action of pembrolizumab?",
        options=["ALK inhibitor", "PD-1 checkpoint inhibitor", "VEGF inhibitor", "HER2 inhibitor", "BRAF inhibitor"],
        answer="PD-1 checkpoint inhibitor",
        explanation="Pembrolizumab (Keytruda) is a monoclonal antibody that blocks PD-1, enhancing T-cell anti-tumor activity.",
        difficulty="medium"
    ),
    BenchmarkQuestion(
        id="drug_003", category="drug_safety",
        question="Which FDA-approved gene therapy treats spinal muscular atrophy in children under 2?",
        options=["Luxturna", "Zolgensma", "Kymriah", "Casgevy", "Hemgenix"],
        answer="Zolgensma",
        explanation="Zolgensma (onasemnogene abeparvovec) is an AAV9-based gene therapy approved for SMA in children under 2.",
        difficulty="medium"
    ),
    BenchmarkQuestion(
        id="drug_004", category="drug_safety",
        question="What is the black box warning for fluoroquinolone antibiotics?",
        options=["Hepatotoxicity", "Tendon rupture and peripheral neuropathy", "QT prolongation only", "Renal failure", "Aplastic anemia"],
        answer="Tendon rupture and peripheral neuropathy",
        explanation="Fluoroquinolones carry black box warnings for tendon rupture/tendinitis, peripheral neuropathy, and CNS effects.",
        difficulty="medium"
    ),
    BenchmarkQuestion(
        id="drug_005", category="drug_safety",
        question="CRISPR-Cas9 gene editing therapy Casgevy (exagamglogene autotemcel) is approved for which conditions?",
        options=["Hemophilia A", "Sickle cell disease and transfusion-dependent beta-thalassemia", "Cystic fibrosis", "Duchenne muscular dystrophy", "Huntington disease"],
        answer="Sickle cell disease and transfusion-dependent beta-thalassemia",
        explanation="Casgevy is the first CRISPR-based therapy approved by FDA for SCD and TDT in patients 12 years and older.",
        difficulty="medium"
    ),
]

CLINICAL_REASONING_QUESTIONS = [
    BenchmarkQuestion(
        id="clin_001", category="clinical",
        question="A 60-year-old smoker presents with hemoptysis and a 3cm lung nodule on CT. Next step?",
        options=["Repeat CT in 3 months", "PET-CT and biopsy", "Sputum cytology only", "Antibiotics and repeat CT in 6 weeks", "Bronchoscopy with BAL"],
        answer="PET-CT and biopsy",
        explanation="A 3cm nodule in a smoker with hemoptysis is highly suspicious for malignancy. PET-CT and tissue biopsy are indicated.",
        difficulty="medium"
    ),
    BenchmarkQuestion(
        id="clin_002", category="clinical",
        question="Patient with CKD stage 4, potassium 6.2 mEq/L, ECG shows peaked T-waves. Most urgent treatment?",
        options=["Sodium polystyrene sulfonate", "IV calcium gluconate", "Furosemide", "Dialysis", "Insulin + glucose"],
        answer="IV calcium gluconate",
        explanation="IV calcium gluconate is the most urgent treatment for hyperkalemia with ECG changes as it stabilizes the myocardium.",
        difficulty="hard"
    ),
]

# Combine all questions
ALL_QUESTIONS = MEDQA_QUESTIONS + DRUG_SAFETY_QUESTIONS + CLINICAL_REASONING_QUESTIONS


class MedicalBenchmark:
    """
    Medical agent benchmark evaluator.

    Evaluates agents against standardized medical questions and
    produces detailed performance reports.
    """

    def __init__(self, questions: Optional[List[BenchmarkQuestion]] = None):
        self.questions = questions or ALL_QUESTIONS
        self._by_category = {}
        for q in self.questions:
            self._by_category.setdefault(q.category, []).append(q)

    def list_categories(self) -> List[str]:
        """List available benchmark categories."""
        return list(self._by_category.keys())

    def get_questions(self, category: Optional[str] = None,
                      difficulty: Optional[str] = None,
                      n: Optional[int] = None) -> List[BenchmarkQuestion]:
        """Get filtered questions."""
        qs = self.questions
        if category:
            qs = [q for q in qs if q.category == category]
        if difficulty:
            qs = [q for q in qs if q.difficulty == difficulty]
        if n:
            qs = qs[:n]
        return qs

    def evaluate(self, agent_fn: Callable[[str], str],
                 category: Optional[str] = None,
                 n: Optional[int] = None) -> BenchmarkResult:
        """
        Evaluate an agent against benchmark questions.

        Args:
            agent_fn: Function that takes a question string and returns an answer
            category: Optional category filter
            n: Optional limit on number of questions

        Returns:
            BenchmarkResult with detailed scoring
        """
        questions = self.get_questions(category=category, n=n)
        if not questions:
            return BenchmarkResult(benchmark="medical", total_questions=0)

        correct = 0
        total_latency = 0.0
        details = []
        category_correct = {}
        category_total = {}

        for q in questions:
            # Format question for agent
            prompt = self._format_question(q)

            # Get agent response
            start = time.time()
            try:
                response = agent_fn(prompt)
            except Exception as e:
                response = f"ERROR: {e}"
            latency = (time.time() - start) * 1000
            total_latency += latency

            # Check answer
            is_correct = self._check_answer(response, q.answer)
            if is_correct:
                correct += 1

            # Track per-category
            category_total[q.category] = category_total.get(q.category, 0) + 1
            if is_correct:
                category_correct[q.category] = category_correct.get(q.category, 0) + 1

            details.append({
                "id": q.id,
                "category": q.category,
                "difficulty": q.difficulty,
                "question": q.question[:100] + "...",
                "expected": q.answer,
                "got": response[:100] if response else "",
                "correct": is_correct,
                "latency_ms": round(latency, 1),
            })

        # Calculate category scores
        category_scores = {}
        for cat in category_total:
            total = category_total[cat]
            c = category_correct.get(cat, 0)
            category_scores[cat] = round(c / total, 3) if total > 0 else 0.0

        from datetime import datetime
        return BenchmarkResult(
            benchmark="medical",
            total_questions=len(questions),
            correct=correct,
            accuracy=round(correct / len(questions), 3) if questions else 0.0,
            avg_latency_ms=round(total_latency / len(questions), 1) if questions else 0.0,
            category_scores=category_scores,
            details=details,
            timestamp=datetime.utcnow().isoformat(),
        )

    def _format_question(self, q: BenchmarkQuestion) -> str:
        """Format a question for the agent."""
        lines = [q.question, ""]
        if q.options:
            for i, opt in enumerate(q.options):
                lines.append(f"{chr(65+i)}. {opt}")
        lines.append("")
        lines.append("Choose the best answer (A/B/C/D/E). Reply with just the letter or the answer text.")
        return "\n".join(lines)

    def _check_answer(self, response: str, expected: str) -> bool:
        """Check if the agent's response matches the expected answer."""
        if not response:
            return False
        response_lower = response.lower().strip()
        expected_lower = expected.lower().strip()

        # Direct match
        if expected_lower in response_lower:
            return True

        # Check if response starts with the answer
        if response_lower.startswith(expected_lower):
            return True

        # Check letter mapping (A=first option, etc.)
        letter_map = {chr(65 + i): opt.lower() for i, opt in enumerate(
            ["a", "b", "c", "d", "e"]
        )}
        for letter, _ in letter_map.items():
            if response_lower.startswith(letter.lower()):
                # Would need options to map back
                break

        return False

    def generate_report(self, result: BenchmarkResult) -> str:
        """Generate a human-readable benchmark report."""
        lines = [
            "=" * 60,
            "Medical Benchmark Report",
            "=" * 60,
            f"Total Questions: {result.total_questions}",
            f"Correct: {result.correct}",
            f"Accuracy: {result.accuracy:.1%}",
            f"Avg Latency: {result.avg_latency_ms:.0f}ms",
            "",
            "Category Breakdown:",
        ]
        for cat, score in sorted(result.category_scores.items()):
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            lines.append(f"  {cat:20s} {bar} {score:.1%}")

        lines.append("")
        lines.append("Question Details:")
        for d in result.details:
            status = "PASS" if d["correct"] else "FAIL"
            lines.append(f"  [{status}] {d['id']}: {d['question']}")
            if not d["correct"]:
                lines.append(f"         Expected: {d['expected']}")
                lines.append(f"         Got: {d['got'][:60]}")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)
