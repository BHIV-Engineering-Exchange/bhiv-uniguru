from __future__ import annotations

from fastapi.testclient import TestClient

from ontology.sanskrit_decoder import decode_sanskrit_concept
from service.uniguru_runtime_api import app


def test_decode_sanskrit_concept_builds_deterministic_pipeline():
    result = decode_sanskrit_concept("धर्म")
    replay = decode_sanskrit_concept("dharma")

    assert result["canonical_concept"]["canonical_name"] == "dharma"
    assert [layer["stage"] for layer in result["pipeline"]] == ["śabda", "dhātu", "vyākaraṇa", "nirukta", "bīja", "tattva", "śakti", "functional_meaning"]
    assert result["knowledge_graph"]["nodes"][0]["id"] == "concept:dharma"
    assert result["governed_response"]["evidence_classification"]["classification"] == "REGISTRY_ATTESTED"
    assert result["provenance"]["replay_safe"] is True
    assert result["result_hash"] == replay["result_hash"]


def test_unknown_concept_is_explicitly_unverified_without_inference():
    result = decode_sanskrit_concept("अनिर्धारित")

    assert result["pipeline"] == []
    assert result["governed_response"]["evidence_classification"]["classification"] == "UNVERIFIED"
    assert result["governed_response"]["governance_state"] == "no_inference"


def test_sanskrit_runtime_endpoint_returns_decoded_payload():
    client = TestClient(app)
    response = client.post("/runtime/sanskrit/decode", json={"query": "धर्म", "emit_proof": False})

    assert response.status_code == 200
    payload = response.json()
    assert payload["trace_id"].startswith("sanskrit_")
    assert payload["decoder_result"]["pipeline"][0]["stage"] == "śabda"
    assert payload["governed_response"]["evidence_classification"]["classification"] == "REGISTRY_ATTESTED"
    assert payload["replay"]["replay_safe"] is True
