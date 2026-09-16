"""
Tests — UniGuru Knowledge Enrichment & Retrieval Convergence
Validates knowledge object builder, civilizational graph expansion,
and provenance chain integrity.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
GRAPH_EXPANSION_FILE = BACKEND_DIR / "knowledge" / "civilizational_graph_expansion.json"
SANSKRIT_KB_DIR = BACKEND_DIR / "knowledge" / "sanskrit"


# ---------------------------------------------------------------------------
# 1. KB inventory — new concepts present
# ---------------------------------------------------------------------------

def test_mantra_md_exists_in_sanskrit_kb():
    assert (SANSKRIT_KB_DIR / "mantra.md").exists()


def test_yantra_md_exists_in_sanskrit_kb():
    assert (SANSKRIT_KB_DIR / "yantra.md").exists()


def test_mantra_md_has_required_sections():
    text = (SANSKRIT_KB_DIR / "mantra.md").read_text(encoding="utf-8")
    for section in ("## Dhātu", "## Nirukta", "## Bīja", "## Tattva", "## Śakti",
                    "## Functional Meaning", "## Related Chakras", "## Canonical Sources"):
        assert section in text, f"Missing section: {section}"


def test_yantra_md_has_required_sections():
    text = (SANSKRIT_KB_DIR / "yantra.md").read_text(encoding="utf-8")
    for section in ("## Dhātu", "## Nirukta", "## Bīja", "## Tattva", "## Śakti",
                    "## Functional Meaning", "## Related Chakras", "## Canonical Sources"):
        assert section in text, f"Missing section: {section}"


def test_mantra_experimental_hypotheses_are_marked():
    text = (SANSKRIT_KB_DIR / "mantra.md").read_text(encoding="utf-8")
    assert "[EXPERIMENTAL" in text


def test_yantra_experimental_hypotheses_are_marked():
    text = (SANSKRIT_KB_DIR / "yantra.md").read_text(encoding="utf-8")
    assert "[EXPERIMENTAL" in text


# ---------------------------------------------------------------------------
# 2. Civilizational graph expansion
# ---------------------------------------------------------------------------

def test_graph_expansion_file_exists():
    assert GRAPH_EXPANSION_FILE.exists()


def test_graph_expansion_schema_version():
    data = json.loads(GRAPH_EXPANSION_FILE.read_text(encoding="utf-8"))
    assert data["schema_version"] == "UNIGURU_CIVILIZATIONAL_GRAPH_EXPANSION_V1"


def test_graph_expansion_has_edges():
    data = json.loads(GRAPH_EXPANSION_FILE.read_text(encoding="utf-8"))
    assert len(data["edges"]) >= 20


def test_graph_expansion_all_edges_have_required_fields():
    data = json.loads(GRAPH_EXPANSION_FILE.read_text(encoding="utf-8"))
    for edge in data["edges"]:
        for field in ("from", "to", "type", "evidence_type", "source"):
            assert field in edge, f"Edge missing field '{field}': {edge}"


def test_graph_expansion_no_invented_associations():
    """All edges must have a source document reference."""
    data = json.loads(GRAPH_EXPANSION_FILE.read_text(encoding="utf-8"))
    for edge in data["edges"]:
        assert edge.get("source"), f"Edge has no source: {edge}"
        assert "backend/knowledge" in edge["source"] or "masterdb" in edge["source"]


def test_graph_expansion_mantra_yantra_cross_reference():
    data = json.loads(GRAPH_EXPANSION_FILE.read_text(encoding="utf-8"))
    edges = data["edges"]
    mantra_to_yantra = any(
        e["from"] == "sanskar:sanskrit:mantra" and e["to"] == "sanskar:sanskrit:yantra"
        for e in edges
    )
    yantra_to_mantra = any(
        e["from"] == "sanskar:sanskrit:yantra" and e["to"] == "sanskar:sanskrit:mantra"
        for e in edges
    )
    assert mantra_to_yantra and yantra_to_mantra


def test_graph_expansion_darsana_cross_references_present():
    data = json.loads(GRAPH_EXPANSION_FILE.read_text(encoding="utf-8"))
    darsanas = data.get("darsana_cross_references", {})
    for school in ("advaita", "samkhya", "yoga", "mimamsa", "kashmir_shaivism"):
        assert school in darsanas, f"Missing darsana: {school}"


def test_graph_expansion_darsana_all_have_primary_shastra():
    data = json.loads(GRAPH_EXPANSION_FILE.read_text(encoding="utf-8"))
    for school, info in data.get("darsana_cross_references", {}).items():
        assert info.get("primary_shastra"), f"Darsana '{school}' missing primary_shastra"
        assert info.get("authority_tier") == "CANONICAL"


# ---------------------------------------------------------------------------
# 3. Knowledge object builder
# ---------------------------------------------------------------------------

def test_knowledge_object_builder_returns_object_for_dharma():
    from convergence.knowledge_object_builder import build_knowledge_object
    obj = build_knowledge_object("sanskar:sanskrit:dharma")
    assert obj["schema_version"] == "UNIGURU_CANONICAL_KNOWLEDGE_OBJECT_V1"
    assert obj["canonical_name"] == "dharma"
    assert obj["dhatu"]
    assert obj["functional_meaning"]


def test_knowledge_object_has_provenance():
    from convergence.knowledge_object_builder import build_knowledge_object
    obj = build_knowledge_object("sanskar:sanskrit:karma")
    prov = obj["provenance"]
    assert prov["source_path"]
    assert prov["content_hash"]
    assert prov["authority_tier"] == "CANONICAL"


def test_knowledge_object_has_retrieval_lineage():
    from convergence.knowledge_object_builder import build_knowledge_object
    obj = build_knowledge_object("sanskar:sanskrit:shakti")
    lineage = obj["retrieval_lineage"]
    assert "canonical_source" in lineage
    assert "kosha_records" in lineage
    assert "graph_edges" in lineage
    assert isinstance(lineage["decoder_coverage_pct"], float)


def test_knowledge_object_has_object_hash():
    from convergence.knowledge_object_builder import build_knowledge_object
    obj = build_knowledge_object("sanskar:sanskrit:dharma")
    assert len(obj["object_hash"]) == 64


def test_knowledge_object_hash_is_deterministic():
    from convergence.knowledge_object_builder import build_knowledge_object
    o1 = build_knowledge_object("sanskar:sanskrit:dharma")
    o2 = build_knowledge_object("sanskar:sanskrit:dharma")
    assert o1["object_hash"] == o2["object_hash"]


def test_knowledge_object_replay_safe():
    from convergence.knowledge_object_builder import build_knowledge_object
    obj = build_knowledge_object("sanskar:sanskrit:yoga")
    assert obj["replay_safe"] is True


def test_knowledge_object_not_found_returns_status():
    from convergence.knowledge_object_builder import build_knowledge_object
    obj = build_knowledge_object("nonexistent_concept_xyz")
    assert obj["status"] == "NOT_FOUND"


def test_knowledge_object_for_mantra():
    from convergence.knowledge_object_builder import build_knowledge_object
    obj = build_knowledge_object("sanskar:sanskrit:mantra")
    assert obj.get("status") != "NOT_FOUND"
    assert obj["canonical_name"] == "mantra"


def test_knowledge_object_for_yantra():
    from convergence.knowledge_object_builder import build_knowledge_object
    obj = build_knowledge_object("sanskar:sanskrit:yantra")
    assert obj.get("status") != "NOT_FOUND"
    assert obj["canonical_name"] == "yantra"


# ---------------------------------------------------------------------------
# 4. Graph expansion edges retrieval
# ---------------------------------------------------------------------------

def test_get_graph_expansion_edges_for_dharma():
    from convergence.knowledge_object_builder import get_graph_expansion_edges
    edges = get_graph_expansion_edges("sanskar:sanskrit:dharma")
    assert len(edges) >= 2


def test_get_graph_expansion_edges_for_mantra():
    from convergence.knowledge_object_builder import get_graph_expansion_edges
    edges = get_graph_expansion_edges("sanskar:sanskrit:mantra")
    assert len(edges) >= 2


# ---------------------------------------------------------------------------
# 5. Provenance chain validation
# ---------------------------------------------------------------------------

def test_provenance_chain_valid_for_dharma():
    from convergence.knowledge_object_builder import validate_provenance_chain
    result = validate_provenance_chain("sanskar:sanskrit:dharma")
    assert result["valid"] is True
    assert result["source_exists"] is True
    assert result["content_hash_present"] is True
    assert result["replay_safe"] is True


def test_provenance_chain_valid_for_karma():
    from convergence.knowledge_object_builder import validate_provenance_chain
    result = validate_provenance_chain("sanskar:sanskrit:karma")
    assert result["valid"] is True


def test_provenance_chain_invalid_for_unknown():
    from convergence.knowledge_object_builder import validate_provenance_chain
    result = validate_provenance_chain("nonexistent_xyz")
    assert result["valid"] is False


# ---------------------------------------------------------------------------
# 6. All-concepts coverage
# ---------------------------------------------------------------------------

def test_all_concepts_have_valid_provenance():
    from convergence.knowledge_object_builder import build_knowledge_objects_for_all_concepts
    results = build_knowledge_objects_for_all_concepts()
    assert len(results) >= 21
    for r in results:
        assert r["replay_safe"] is True
        assert r["object_hash"]


def test_coverage_pct_above_threshold_for_core_concepts():
    from convergence.knowledge_object_builder import build_knowledge_object
    for concept in ("dharma", "karma", "shakti"):
        obj = build_knowledge_object(f"sanskar:sanskrit:{concept}")
        pct = obj.get("retrieval_lineage", {}).get("decoder_coverage_pct", 0.0)
        assert pct >= 50.0, f"{concept} coverage {pct}% below 50%"
