"""
Phase 4 — Custom LLM-as-judge evaluators for CollegeGPT RAG eval (no RAGAS)
Place this in: backend/evalutations/evaluators.py

Each function matches LangSmith's evaluate() target signature:
    evaluator(inputs, outputs, reference_outputs) -> dict

- inputs           = the dataset example's input,  e.g. {"question": ...}
- outputs          = what evaluate_college_gpt() returned,
                      e.g. {"answer": ..., "contexts": [...]}
- reference_outputs = the dataset example's output, e.g. {"ground_truth": ...}

Each returns {"key": <metric name>, "score": float 0-1, "comment": str}
— LangSmith records "key"/"score" per example and shows "comment" as
the reasoning, visible per-row in the Experiment UI.

Uses a separate GROQ_API_REFERENCE key, same as generate_testset.py,
so judge calls don't compete with your RAG app's own rate limit.

Note on self-bias: ideally the judge model differs from the model
being evaluated (your RAG app also runs openai/gpt-oss-20b via Groq).
JUDGE_MODEL is kept configurable below — swap it to a different Groq
model if you want a cleaner separation; left as the same model for
now to keep one less moving part while you're learning the pipeline.
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

if "GROQ_API_REFERENCE" not in os.environ:
    raise KeyError("GROQ_API_REFERENCE key not found in environment or .env file.")

JUDGE_MODEL = "openai/gpt-oss-20b"

judge_llm = ChatGroq(
    model=JUDGE_MODEL,
    api_key=os.environ["GROQ_API_REFERENCE"],
    temperature=0.0,  # deterministic scoring, not creative generation
    max_tokens=256,
)


def _call_judge(system_prompt: str, user_prompt: str) -> dict:
    """Send a judge prompt, parse the required {"score": float, "reasoning": str}
    JSON response. Returns a safe fallback if parsing fails, instead of
    crashing the whole eval run over one bad judge response."""
    response = judge_llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )
    raw = response.content.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:].strip()
        raw = raw.strip("` \n")
    try:
        parsed = json.loads(raw)
        return {
            "score": float(parsed.get("score", 0.0)),
            "reasoning": parsed.get("reasoning", ""),
        }
    except (json.JSONDecodeError, ValueError, TypeError):
        return {"score": 0.0, "reasoning": f"Judge response unparseable: {raw[:200]}"}


# ---------------------------------------------------------------------------
# 1. Faithfulness — is the answer actually grounded in the retrieved context,
#    or did the model hallucinate/add claims the context doesn't support?
# ---------------------------------------------------------------------------
FAITHFULNESS_PROMPT = """You are judging whether an AI-generated answer is faithful \
to the given context — i.e. every claim in the answer is supported by the context, \
with no hallucinated or unsupported information added.

Respond with ONLY valid JSON, no other text:
{"score": <0.0 to 1.0>, "reasoning": "<one sentence>"}

Scoring:
- 1.0 = every claim in the answer is directly supported by the context
- 0.5 = the answer is partially supported, with some unsupported additions
- 0.0 = the answer contains claims not supported by the context, or contradicts it
"""


def faithfulness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    context = "\n\n".join(outputs.get("contexts", []))
    answer = outputs.get("answer", "")
    user_prompt = f"Context:\n{context}\n\nAnswer:\n{answer}"
    result = _call_judge(FAITHFULNESS_PROMPT, user_prompt)
    return {"key": "faithfulness", "score": result["score"], "comment": result["reasoning"]}


# ---------------------------------------------------------------------------
# 2. Answer Relevancy — does the answer actually address the question asked,
#    regardless of whether it's factually correct?
# ---------------------------------------------------------------------------
ANSWER_RELEVANCY_PROMPT = """You are judging whether an AI-generated answer actually \
addresses the question that was asked — not whether it's factually correct, just \
whether it's on-topic, direct, and doesn't dodge or ramble off-topic.

Respond with ONLY valid JSON, no other text:
{"score": <0.0 to 1.0>, "reasoning": "<one sentence>"}

Scoring:
- 1.0 = directly and completely addresses the question
- 0.5 = partially addresses it, or includes irrelevant padding
- 0.0 = does not address the question at all
"""


def answer_relevancy_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    question = inputs.get("question", "")
    answer = outputs.get("answer", "")
    user_prompt = f"Question:\n{question}\n\nAnswer:\n{answer}"
    result = _call_judge(ANSWER_RELEVANCY_PROMPT, user_prompt)
    return {"key": "answer_relevancy", "score": result["score"], "comment": result["reasoning"]}


def context_precision_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """Measure lexical retrieval precision without making another LLM call."""
    import re

    stop_words = {
        "about", "after", "also", "and", "are", "because", "from", "have",
        "into", "that", "the", "their", "there", "these", "this", "those",
        "was", "were", "what", "when", "which", "with", "would",
    }

    def content_tokens(value: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9]+", value.lower())
            if len(token) > 2 and token not in stop_words
        }

    retrieved_tokens = content_tokens("\n\n".join(outputs.get("contexts", [])))
    reference_tokens = content_tokens(reference_outputs.get("context", ""))
    overlap = retrieved_tokens & reference_tokens
    score = len(overlap) / len(retrieved_tokens) if retrieved_tokens else 0.0

    return {
        "key": "context_precision",
        "score": round(score, 4),
        "comment": (
            f"{len(overlap)} of {len(retrieved_tokens)} retrieved content terms "
            "also appear in the reference context."
        ),
    }


# Convenience list for passing straight into langsmith's evaluate(evaluators=...)
ALL_EVALUATORS = [faithfulness_evaluator, answer_relevancy_evaluator, context_precision_evaluator]