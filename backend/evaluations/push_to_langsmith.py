"""
Phase 2 — Push synthetic testset into LangSmith as a Dataset (no RAGAS)
Place this in: backend/evalutations/push_to_langsmith.py

Reads eval_set.json (from generate_testset.py) and uploads it as a
LangSmith Dataset under a FIXED name, so later eval runs (run_eval.py)
can always find the same dataset and you get comparable experiments
across changes, instead of a new one-off dataset every run.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client
from langsmith.schemas import DataType

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

if not os.getenv("LANGSMITH_API_KEY"):
    raise KeyError("LANGSMITH_API_KEY not found in environment or .env file.")

os.environ["LANGSMITH_TRACING"] = "true"

client = Client()

json_file = Path(__file__).resolve().parent / "eval_set.json"
if not json_file.exists():
    json_file = Path("eval_set.json")

with open(json_file, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print(f"Loaded {len(raw_data)} evaluation records from file.")

# Fixed name, not a per-run UUID — reused across every push so run_eval.py
# and the LangSmith UI always point at the same growing/updating dataset.
DATASET_NAME = "CollegeGPT_Gold_Set"

if client.has_dataset(dataset_name=DATASET_NAME):
    dataset = client.read_dataset(dataset_name=DATASET_NAME)
    print(f"Dataset '{DATASET_NAME}' already exists — adding examples to it.")
else:
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Custom generated QA pairs extracted directly from college textbook uploads.",
        data_type=DataType.kv,
    )
    print(f"Created new dataset '{DATASET_NAME}'.")

inputs = [{"question": row["question"]} for row in raw_data]
outputs = [
    {"ground_truth": row["ground_truth"], "context": row["context"]}
    for row in raw_data
]
metadata = [{"source": row["source"], "page": row["page"]} for row in raw_data]

print(f"Uploading {len(inputs)} formatted records to LangSmith dataset: '{DATASET_NAME}'...")

client.create_examples(
    inputs=inputs,
    outputs=outputs,
    metadata=metadata,
    dataset_id=dataset.id,
)

print("Successfully uploaded dataset! You can view it in your LangSmith dashboard.")