from __future__ import annotations

from fastapi.testclient import TestClient

from ontology.sanskrit_decoder import decode_sanskrit_concept, load_sanskar_registry
from service.uniguru_runtime_api import app


def test_sanskar_source_retrieval_supports_all_supplied_concepts():
    registry, _ = load_sanskar_registry()
    assert len(registry.list_concepts()) == 6
    result = decode_sanskrit_concept("धर्म")
    replay = decode_sanskrit_concept("dharma")
    assert result["canonical_concept"]["concept_id"] == "sanskar:sanskrit:dharma"
    assert result["result_hash"] == replay["result_hash"]
    assert [layer["stage"] for layer in result["pipeline"]] == ["śabda", "dhātu", "vyākaraṇa", "nirukta", "bīja", "tattva", "śakti", "functional_meaning"]
    assert result["provenance"]["source_documents"]
    assert result["knowledge_graph"]["metadata"]["consistency_valid"] is True


def test_unknown_concept_is_explicitly_unverified_without_inference():
    result = decode_sanskrit_concept("अनिर्धारित")
    assert result["pipeline"] == []
    assert result["governed_response"]["evidence_classification"]["classification"] == "UNVERIFIED"
    assert result["governed_response"]["governance_state"] == "no_inference"


def test_sanskrit_runtime_endpoint_validates_and_returns_source_scoped_payload():
    client = TestClient(app)
    response = client.post("/runtime/sanskrit/decode", json={"query": "धर्म", "emit_proof": False})
    assert response.status_code == 200
    payload = response.json()
    assert payload["decoder_result"]["pipeline"][0]["stage"] == "śabda"
    assert "BHAGAVAD_GITA" in payload["governed_response"]["evidence_classification"]["evidence_types"]
    assert client.post("/runtime/sanskrit/decode", json={"query": "   ", "emit_proof": False}).status_code == 422
