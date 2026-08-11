"""Versioned offline retrieval and prompt-injection evaluation gates."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from careerpilot_api.main import create_app
from careerpilot_core import InjectionRisk, RagService
from tests.api.helpers import login_headers

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_retrieval_metrics_meet_versioned_thresholds() -> None:
    fixture = json.loads((FIXTURES / "retrieval-evaluation-v1.json").read_text())
    client = TestClient(create_app())
    headers = login_headers(client, "ada", "tenant-ada")
    profile = client.post(
        "/api/v1/profiles",
        headers=headers,
        json={
            "display_name": "Evaluation Candidate",
            "professional_summary": "A fully synthetic retrieval evaluation profile.",
        },
    ).json()
    document_ids: dict[str, str] = {}
    for document in fixture["documents"]:
        response = client.post(
            "/api/v1/documents",
            headers=headers,
            data={"profile_id": profile["profile_id"], "title": document["title"]},
            files={
                "file": (
                    document["filename"],
                    document["content"].encode(),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 201
        document_ids[document["filename"]] = response.json()["document_id"]

    recalls: list[float] = []
    precisions: list[float] = []
    reciprocal_ranks: list[float] = []
    grounding: list[float] = []
    citations: list[float] = []
    for case in fixture["queries"]:
        result = client.post(
            "/api/v1/retrieval/search",
            headers=headers,
            json={"query": case["query"], "limit": 3},
        ).json()
        passages = result["passages"]
        relevant = [
            index
            for index, passage in enumerate(passages, start=1)
            if passage["citation"]["filename"] == case["relevant_filename"]
        ]
        recalls.append(float(bool(relevant)))
        precisions.append(len(relevant) / max(len(passages), 1))
        reciprocal_ranks.append(1 / relevant[0] if relevant else 0.0)
        grounding.append(
            float(
                any(case["expected_text"] in passage["content"] for passage in passages)
            )
        )
        citations.append(
            float(
                any(
                    passage["citation"]["document_id"]
                    == document_ids[case["relevant_filename"]]
                    for passage in passages
                )
            )
        )

    metrics = {
        "recall_at_3": sum(recalls) / len(recalls),
        "precision_at_3": sum(precisions) / len(precisions),
        "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks),
        "grounding": sum(grounding) / len(grounding),
        "citation_correctness": sum(citations) / len(citations),
    }
    for metric, threshold in fixture["thresholds"].items():
        assert metrics[metric] >= threshold, metrics


def test_prompt_injection_corpus_is_versioned_and_labeled() -> None:
    fixture = json.loads((FIXTURES / "prompt-injection-corpus-v1.json").read_text())
    for text in fixture["suspected"]:
        assert RagService._risk_for(text) is InjectionRisk.SUSPECTED  # noqa: SLF001
    for text in fixture["benign"]:
        assert RagService._risk_for(text) is InjectionRisk.NONE_DETECTED  # noqa: SLF001
