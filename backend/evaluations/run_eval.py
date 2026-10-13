"""
Phase 5 — Wire everything together and run the evaluation (no RAGAS)
Place this in: backend/evalutations/run_eval.py

Runs your RAG pipeline (rag_pipeline.evaluate_college_gpt) against the
LangSmith dataset pushed by push_to_langsmith.py, scoring each output
with the three custom LLM-judge evaluators from evaluators.py.

Results land in the LangSmith UI as a new "Experiment" under the
CollegeGPT_Gold_Set dataset — re-run this after any pipeline change
(chunking, prompt, retriever k, etc.) and compare experiments
side-by-side to see if the change actually helped.
"""

import os
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

if not os.getenv("LANGSMITH_API_KEY"):
    raise KeyError("LANGSMITH_API_KEY not found in environment or .env file.")

os.environ["LANGSMITH_TRACING"] = "true"

from rag_pipeline import evaluate_college_gpt
from evaluators import ALL_EVALUATORS

DATASET_NAME = "CollegeGPT_Gold_Set"  # must match push_to_langsmith.py

# Timestamped prefix so each run shows up as a distinct, comparable
# experiment in the LangSmith UI instead of overwriting the last one.
EXPERIMENT_PREFIX = f"collegegpt-eval-{datetime.now().strftime('%Y%m%d-%H%M')}"
EVAL_BATCH_SIZE = 5
EVAL_BATCH_PAUSE_SECONDS = 60


def main():
    client = Client()
    dataset = client.read_dataset(dataset_name=DATASET_NAME)
    examples = list(client.list_examples(dataset_id=dataset.id))
    print(
        f"Running evaluation against dataset '{DATASET_NAME}' "
        f"in {EVAL_BATCH_SIZE}-example batches ..."
    )

    results = []
    for start in range(0, len(examples), EVAL_BATCH_SIZE):
        batch_number = start // EVAL_BATCH_SIZE + 1
        batch = examples[start:start + EVAL_BATCH_SIZE]
        print(f"Starting batch {batch_number} ({len(batch)} examples) ...")
        results.append(
            evaluate(
                evaluate_college_gpt,
                data=batch,
                evaluators=ALL_EVALUATORS,
                experiment_prefix=f"{EXPERIMENT_PREFIX}-batch-{batch_number}",
                max_concurrency=1,
            )
        )

        if start + EVAL_BATCH_SIZE < len(examples):
            print(f"Waiting {EVAL_BATCH_PAUSE_SECONDS}s before the next batch ...")
            time.sleep(EVAL_BATCH_PAUSE_SECONDS)

    print(f"Done. View the experiments with prefix '{EXPERIMENT_PREFIX}' in LangSmith.")
    return results


if __name__ == "__main__":
    main()