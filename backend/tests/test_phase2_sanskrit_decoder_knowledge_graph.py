"""
Phase 2: Advanced Integration & Security Hardening
Isha Singh — UniGuru Native Sanskrit Knowledge Decoder And
Civilizational Knowledge Graph (UniGuru Platform – Foundation Sprint 1)

Unit test coverage for:
- Production monitoring (registry observability, coverage metrics, schema versioning)
- Error boundary safety (invalid input, unknown concepts, graph consistency)
- E2E integration verification (decoder pipeline, graph traversal, API endpoints)
- API contract boundaries (field contracts, auth, validation)
- Deterministic execution (result_hash stability, traversal_hash stability)
- Knowledge graph integrity (node/edge provenance, typed node expansion)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("UNIGURU_API_AUTH_REQUIRED", "false")

CORE_CONCEPTS = ["dharma", "karma", "atman", "brahman", "prana", "shakti", "maya", "yajna"]
DEVANAGARI_MAP = {"dharma": "धर्म", "karma": "कर्म", "atman": "आत्मन्", "prana": "प्राण"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def registry_and_metadata():
    from ontology.sanskrit_decoder import load_sanskar_registry
    return load_sanskar_registry()


@pytest.fixture(scope="module")
def client():
    from service.uniguru_runtime_api import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Production Monitoring — registry observability and coverage metrics
# ---------------------------------------------------------------------------

def test_registry_loads_minimum_21_concepts(registry_and_metadata):
    registry, _ = registry_and_metadata
    assert len(registry.list_concepts()) >= 21


def test_registry_exposes_all_core_concepts(registry_and_metadata):
    registry, _ = registry_and_metadata
    ids = {c.concept_id for c in registry.list_concepts()}
    for name in CORE_CONCEPTS:
        assert f"sanskar:sanskrit:{name}" in ids, f"Missing core concept: {name}"


def test_decoder_coverage_pct_is_at_least_85_for_dharma():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    result = decode_sanskrit_concept("dharma")
    cov = result["civilizational_knowledge"]["coverage"]["coverage_pct"]
    assert cov >= 85.0, f"Coverage too low: {cov}"


def test_decoder_schema_version_is_v3():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    result = decode_sanskrit_concept("dharma")
    assert result["civilizational_knowledge"]["schema_version"] == "UNIGURU_CIVILIZATIONAL_KNOWLEDGE_OBJECT_V3"


def test_decoder_registry_version_is_in_provenance():
    from ontology.sanskrit_decoder import decode_sanskrit_concept, REGISTRY_VERSION
    result = decode_sanskrit_concept("karma")
    assert result["provenance"]["registry_version"] == REGISTRY_VERSION


def test_decoder_exposes_total_and_backed_layer_counts():
    from ontology.sanskrit_decoder import decode_sanskrit_concept, KNOWLEDGE_LAYERS
    result = decode_sanskrit_concept("dharma")
    cov = result["civilizational_knowledge"]["coverage"]
    assert cov["total_layers"] == len(KNOWLEDGE_LAYERS)
    assert cov["evidence_backed_layers"] >= 1
    assert 0.0 <= cov["coverage_pct"] <= 100.0


def test_knowledge_graph_metadata_exposes_node_and_edge_counts():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    result = decode_sanskrit_concept("dharma")
    meta = result["knowledge_graph"]["metadata"]
    assert "node_count" in meta
    assert "edge_count" in meta
    assert meta["node_count"] >= 1


# ---------------------------------------------------------------------------
# 2. Error Boundary Safety
# ---------------------------------------------------------------------------

def test_empty_string_query_raises_value_error():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    with pytest.raises(ValueError):
        decode_sanskrit_concept("")


def test_whitespace_only_query_raises_value_error():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    with pytest.raises(ValueError):
        decode_sanskrit_concept("   ")


def test_unknown_concept_returns_unverified_without_inference():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    result = decode_sanskrit_concept("अनिर्धारित")
    assert result["canonical_concept"] is None
    assert result["pipeline"] == []
    assert result["governed_response"]["evidence_classification"]["classification"] == "UNVERIFIED"
    assert result["governed_response"]["governance_state"] == "no_inference"
    assert result["knowledge_graph"]["nodes"] == []
    assert result["knowledge_graph"]["edges"] == []


def test_unknown_concept_has_result_hash():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    result = decode_sanskrit_concept("xyz_unknown_concept_999")
    assert "result_hash" in result
    assert result["result_hash"]


def test_graph_consistency_valid_is_always_true():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    for concept in CORE_CONCEPTS[:4]:
        result = decode_sanskrit_concept(concept)
        assert result["knowledge_graph"]["metadata"]["consistency_valid"] is True


def test_decoder_api_rejects_empty_query(client):
    resp = client.post("/runtime/sanskrit/decode", json={"query": "   ", "emit_proof": False})
    assert resp.status_code == 422


def test_decoder_api_rejects_missing_query(client):
    resp = client.post("/runtime/sanskrit/decode", json={"emit_proof": False})
    assert resp.status_code == 422


def test_graph_traverse_api_rejects_depth_above_6(client):
    resp = client.post(
        "/v2/runtime/sanskrit/graph/traverse",
        json={"start": "dharma", "max_depth": 7, "emit_proof": False},
    )
    assert resp.status_code == 422


def test_graph_traverse_api_rejects_empty_start(client):
    resp = client.post(
        "/v2/runtime/sanskrit/graph/traverse",
        json={"start": "   ", "max_depth": 2, "emit_proof": False},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 3. E2E Integration Verification
# ---------------------------------------------------------------------------

def test_decoder_pipeline_has_all_8_stages():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    result = decode_sanskrit_concept("dharma")
    stages = [s["stage"] for s in result["pipeline"]]
    assert stages == ["śabda", "dhātu", "vyākaraṇa", "nirukta", "bīja", "tattva", "śakti", "functional_meaning"]


def test_decoder_pipeline_stages_all_have_evidence():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    result = decode_sanskrit_concept("dharma")
    for stage in result["pipeline"]:
        assert stage["evidence"], f"Stage {stage['stage']} has no evidence"
        assert stage["lineage"]["concept_id"] == "sanskar:sanskrit:dharma"


def test_devanagari_and_iast_produce_identical_result_hash():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    for iast, devanagari in DEVANAGARI_MAP.items():
        r_iast = decode_sanskrit_concept(iast)
        r_dev = decode_sanskrit_concept(devanagari)
        assert r_iast["result_hash"] == r_dev["result_hash"], f"Hash mismatch for {iast}"


def test_decoder_api_returns_source_scoped_classification(client):
    resp = client.post("/runtime/sanskrit/decode", json={"query": "dharma", "emit_proof": False})
    assert resp.status_code == 200
    body = resp.json()
    assert body["decoder_result"]["governed_response"]["evidence_classification"]["classification"] == "SOURCE_SCOPED"
    assert len(body["decoder_result"]["governed_response"]["evidence_classification"]["evidence_types"]) > 0


def test_decoder_v2_alias_returns_same_payload(client):
    r1 = client.post("/runtime/sanskrit/decode", json={"query": "lokas", "emit_proof": False})
    r2 = client.post("/v2/runtime/sanskrit/decode", json={"query": "lokas", "emit_proof": False})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["decoder_result"]["result_hash"] == r2.json()["decoder_result"]["result_hash"]


def test_graph_traverse_api_returns_replay_safe_traversal(client):
    resp = client.post(
        "/v2/runtime/sanskrit/graph/traverse",
        json={"start": "dharma", "edge_types": ["canonical_cross_reference"], "max_depth": 2, "emit_proof": False},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["replay_safe"] is True
    tr = body["traversal_result"]
    assert tr["start"] == "dharma"
    assert tr["path"][0]["node_label"] == "dharma"
    assert tr["traversal_metadata"]["replay_safe"] is True


def test_graph_traverse_api_returns_response_hash(client):
    resp = client.post(
        "/v2/runtime/sanskrit/graph/traverse",
        json={"start": "karma", "max_depth": 1, "emit_proof": False},
    )
    assert resp.status_code == 200
    assert "response_hash" in resp.json()


def test_fallback_registry_builds_when_source_dir_absent(monkeypatch):
    from ontology.sanskrit_decoder import load_sanskar_registry
    monkeypatch.setattr("ontology.sanskrit_decoder.SOURCE_DIR", Path("c:/does/not/exist"))
    registry, metadata = load_sanskar_registry()
    assert len(registry.list_concepts()) >= 10
    assert "sanskar:sanskrit:dharma" in metadata
    assert metadata["sanskar:sanskrit:dharma"]["retrieval_system"] == "uniguru_ecosystem_adapter"


# ---------------------------------------------------------------------------
# 4. API Contract Boundaries
# ---------------------------------------------------------------------------

def test_decoder_api_response_has_all_required_top_level_fields(client):
    resp = client.post("/runtime/sanskrit/decode", json={"query": "karma", "emit_proof": False})
    assert resp.status_code == 200
    body = resp.json()
    for field in ("trace_id", "decoder_result", "governed_response", "replay", "schema_version", "response_hash"):
        assert field in body, f"Missing top-level field: {field}"


def test_decoder_api_replay_field_is_safe(client):
    resp = client.post("/runtime/sanskrit/decode", json={"query": "karma", "emit_proof": False})
    assert resp.status_code == 200
    replay = resp.json()["replay"]
    assert replay["replay_safe"] is True
    assert "replay_key" in replay


def test_decoder_api_schema_version_is_v1(client):
    resp = client.post("/runtime/sanskrit/decode", json={"query": "dharma", "emit_proof": False})
    assert resp.status_code == 200
    assert resp.json()["schema_version"] == "UNIGURU_SANSKRIT_DECODER_RESPONSE_V1"


def test_graph_traverse_api_response_has_required_fields(client):
    resp = client.post(
        "/v2/runtime/sanskrit/graph/traverse",
        json={"start": "prana", "max_depth": 1, "emit_proof": False},
    )
    assert resp.status_code == 200
    body = resp.json()
    for field in ("trace_id", "traversal_result", "schema_version", "replay_safe", "response_hash"):
        assert field in body, f"Missing field: {field}"


def test_decoder_api_requires_no_auth(client):
    resp = client.post("/runtime/sanskrit/decode", json={"query": "dharma", "emit_proof": False})
    assert resp.status_code == 200


def test_graph_traverse_api_requires_no_auth(client):
    resp = client.post(
        "/v2/runtime/sanskrit/graph/traverse",
        json={"start": "dharma", "max_depth": 1, "emit_proof": False},
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 5. Deterministic Execution — result_hash and traversal_hash stability
# ---------------------------------------------------------------------------

def test_result_hash_is_stable_across_repeated_calls():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    for concept in CORE_CONCEPTS[:4]:
        r1 = decode_sanskrit_concept(concept)
        r2 = decode_sanskrit_concept(concept)
        assert r1["result_hash"] == r2["result_hash"], f"result_hash unstable for {concept}"


def test_traversal_hash_is_stable_across_repeated_calls(registry_and_metadata):
    from ontology.sanskrit_decoder import traverse_concept_graph
    registry, metadata_by_id = registry_and_metadata
    r1 = traverse_concept_graph("dharma", ["canonical_cross_reference"], 2, registry, metadata_by_id)
    r2 = traverse_concept_graph("dharma", ["canonical_cross_reference"], 2, registry, metadata_by_id)
    assert r1["traversal_metadata"]["traversal_hash"] == r2["traversal_metadata"]["traversal_hash"]


def test_canonical_object_id_format_is_stable():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    r1 = decode_sanskrit_concept("dharma")
    r2 = decode_sanskrit_concept("dharma")
    assert r1["canonical_concept"]["concept_id"] == r2["canonical_concept"]["concept_id"]
    assert r1["canonical_concept"]["concept_id"] == "sanskar:sanskrit:dharma"


def test_provenance_content_hash_is_stable():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    r1 = decode_sanskrit_concept("karma")
    r2 = decode_sanskrit_concept("karma")
    h1 = r1["provenance"]["lineage"]["content_hash"]
    h2 = r2["provenance"]["lineage"]["content_hash"]
    assert h1 == h2


def test_replay_safe_is_always_true_in_provenance():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    for concept in CORE_CONCEPTS[:4]:
        result = decode_sanskrit_concept(concept)
        assert result["provenance"]["replay_safe"] is True


# ---------------------------------------------------------------------------
# 6. Knowledge Graph Integrity — node/edge provenance and typed node expansion
# ---------------------------------------------------------------------------

def test_all_graph_edges_reference_existing_nodes():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    result = decode_sanskrit_concept("dharma")
    graph = result["knowledge_graph"]
    node_ids = {n["id"] for n in graph["nodes"]}
    for edge in graph["edges"]:
        assert edge["from"] in node_ids, f"Edge 'from' node missing: {edge['from']}"
        assert edge["to"] in node_ids, f"Edge 'to' node missing: {edge['to']}"


def test_all_graph_nodes_have_address_or_provenance():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    result = decode_sanskrit_concept("dharma")
    for node in result["knowledge_graph"]["nodes"]:
        has_location = "provenance" in node or "address" in node
        assert has_location, f"Node {node['id']} missing both provenance and address"


def test_all_graph_edges_have_evidence_type():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    result = decode_sanskrit_concept("dharma")
    for edge in result["knowledge_graph"]["edges"]:
        assert "evidence_type" in edge, f"Edge {edge} missing evidence_type"


def test_graph_traversal_path_frames_have_required_fields(registry_and_metadata):
    from ontology.sanskrit_decoder import traverse_concept_graph
    registry, metadata_by_id = registry_and_metadata
    result = traverse_concept_graph("prana", None, 3, registry, metadata_by_id)
    for frame in result["path"]:
        for field in ("hop", "node_id", "node_label", "node_type", "provenance"):
            assert field in frame, f"Path frame missing field: {field}"


def test_graph_traversal_typed_nodes_prana_kosha_chakra_bija(registry_and_metadata):
    from ontology.sanskrit_decoder import traverse_concept_graph
    registry, metadata_by_id = registry_and_metadata
    result = traverse_concept_graph("prana", None, 3, registry, metadata_by_id)
    path_types = {f["node_type"] for f in result["path"]}
    assert "sanskrit_concept" in path_types
    assert "kosha" in path_types
    assert "chakra" in path_types
    assert "bija" in path_types


def test_graph_traversal_sub_graph_edges_have_from_type_and_to_type(registry_and_metadata):
    from ontology.sanskrit_decoder import traverse_concept_graph
    registry, metadata_by_id = registry_and_metadata
    result = traverse_concept_graph("prana", None, 3, registry, metadata_by_id)
    for edge in result["sub_graph"]["edges"]:
        assert "from_type" in edge, f"Edge missing from_type: {edge}"
        assert "to_type" in edge, f"Edge missing to_type: {edge}"
        assert "provenance" in edge, f"Edge missing provenance: {edge}"


def test_cross_references_are_derived_classification():
    from ontology.sanskrit_decoder import decode_sanskrit_concept
    result = decode_sanskrit_concept("dharma")
    for ref in result["cross_references"]:
        assert ref["classification"] == "DERIVED"
        assert ref["status"] == "DERIVED_FROM_CANONICAL_CROSS_REFERENCE"
