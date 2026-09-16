"""
Canonical Knowledge Object Builder
UniGuru Knowledge Enrichment & Retrieval Convergence

Builds structured knowledge objects from existing canonical sources
(MASTERDB, AKASHIC, Kosha, Sanskrit KB, Knowledge Graph) with full
source, provenance, version, and retrieval lineage.

Does NOT create a parallel corpus. Retrieves from existing UniGuru
sources only.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
KOSHA_DIR = BACKEND_DIR / "data" / "kosha"
SANSKRIT_KB_DIR = BACKEND_DIR / "knowledge" / "sanskrit"
GRAPH_EXPANSION_FILE = BACKEND_DIR / "knowledge" / "civilizational_graph_expansion.json"
MASTERDB_DATASET = PROJECT_ROOT / "masterdb" / "balbharti" / "canonical_dataset.json"

SCHEMA_VERSION = "UNIGURU_CANONICAL_KNOWLEDGE_OBJECT_V1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _load_json(path: Path) -> Optional[Any]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _provenance_record(
    source: str,
    source_path: str,
    content_hash: str,
    retrieval_method: str,
    authority_tier: str = "CANONICAL",
) -> Dict[str, Any]:
    return {
        "source": source,
        "source_path": source_path,
        "content_hash": content_hash,
        "retrieval_method": retrieval_method,
        "authority_tier": authority_tier,
        "retrieved_at": _utc_now(),
    }


def build_knowledge_object(concept_id: str) -> Dict[str, Any]:
    """Build a structured knowledge object for a Sanskrit concept.

    Retrieves from:
    1. Sanskrit KB markdown (canonical source)
    2. Kosha entries (derived retrieval)
    3. Civilizational graph expansion (derived relationships)
    4. MASTERDB (curriculum canonical source)

    Returns a structured object with source, provenance, version,
    and retrieval lineage preserved.
    """
    from ontology.sanskrit_decoder import load_sanskar_registry, decode_sanskrit_concept

    registry, metadata_by_id = load_sanskar_registry()

    # Resolve concept
    concept = None
    for c in registry.list_concepts():
        if c.concept_id == concept_id or c.canonical_name.lower() == concept_id.lower():
            concept = c
            break

    if concept is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "concept_id": concept_id,
            "status": "NOT_FOUND",
            "provenance": [],
            "retrieval_lineage": [],
        }

    metadata = metadata_by_id.get(concept.concept_id, {})
    source_path = metadata.get("path", "")
    content_hash = metadata.get("content_hash", "")

    # 1. Canonical source provenance
    canonical_provenance = _provenance_record(
        source=source_path,
        source_path=source_path,
        content_hash=content_hash,
        retrieval_method="sanskrit_kb_markdown",
        authority_tier="CANONICAL",
    )

    # 2. Kosha retrieval evidence
    kosha_records: List[Dict[str, Any]] = []
    if KOSHA_DIR.exists():
        for path in sorted(KOSHA_DIR.glob("*.json")):
            raw = _load_json(path)
            if not isinstance(raw, dict):
                continue
            content = str(raw.get("content") or raw.get("clean_content") or "")
            if concept.canonical_name.lower() in content.lower():
                kosha_records.append({
                    "knowledge_id": raw.get("knowledge_id", path.stem),
                    "source": raw.get("source", path.name),
                    "content_preview": content[:200],
                    "confidence": float(raw.get("confidence", 0.0)),
                    "provenance": _provenance_record(
                        source=str(raw.get("source", path.name)),
                        source_path=str(path.relative_to(BACKEND_DIR).as_posix()),
                        content_hash=_sha256(content),
                        retrieval_method="kosha_json_retrieval",
                        authority_tier="DERIVED",
                    ),
                })

    # 3. Graph expansion edges for this concept
    graph_data = _load_json(GRAPH_EXPANSION_FILE) or {}
    graph_edges = [
        e for e in graph_data.get("edges", [])
        if e.get("from") == concept.concept_id or e.get("to") == concept.concept_id
    ]

    # 4. Decoder result (full civilizational knowledge object)
    decoder_result = decode_sanskrit_concept(concept.canonical_name)

    # Build the structured knowledge object
    obj: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "concept_id": concept.concept_id,
        "canonical_name": concept.canonical_name,
        "sanskrit": concept.sanskrit,
        "transliteration": concept.transliteration,
        "dhatu": concept.dhatu,
        "vyakarana": concept.vyakarana,
        "nirukta": concept.nirukta,
        "bija": concept.beeja,
        "tattva": concept.tattva,
        "shakti": concept.shakti,
        "functional_meaning": concept.functional_meaning,
        "related_concepts": concept.related_concepts,
        "source": {
            "primary": source_path,
            "authority_tier": "CANONICAL",
            "registry_version": metadata.get("retrieval_system", "uniguru_ecosystem_adapter"),
        },
        "provenance": canonical_provenance,
        "retrieval_lineage": {
            "canonical_source": canonical_provenance,
            "kosha_records": kosha_records,
            "graph_edges": graph_edges,
            "decoder_coverage_pct": (
                decoder_result.get("civilizational_knowledge", {})
                .get("coverage", {})
                .get("coverage_pct", 0.0)
            ),
        },
        "civilizational_knowledge": decoder_result.get("civilizational_knowledge"),
        "knowledge_graph": decoder_result.get("knowledge_graph"),
        "graph_expansion_edges": graph_edges,
        "version": {
            "schema": SCHEMA_VERSION,
            "decoder": decoder_result.get("provenance", {}).get("schema_version"),
            "registry": decoder_result.get("provenance", {}).get("registry_version"),
        },
        "replay_safe": True,
        "generated_at": _utc_now(),
    }

    obj["object_hash"] = _sha256(
        json.dumps(
            {
                "concept_id": obj["concept_id"],
                "canonical_name": obj["canonical_name"],
                "dhatu": obj["dhatu"],
                "functional_meaning": obj["functional_meaning"],
                "source": obj["source"],
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )

    return obj


def build_knowledge_objects_for_all_concepts() -> List[Dict[str, Any]]:
    """Build knowledge objects for all registered Sanskrit concepts."""
    from ontology.sanskrit_decoder import load_sanskar_registry

    registry, _ = load_sanskar_registry()
    results = []
    for concept in registry.list_concepts():
        obj = build_knowledge_object(concept.concept_id)
        results.append({
            "concept_id": obj["concept_id"],
            "canonical_name": obj["canonical_name"],
            "status": obj.get("status", "OK"),
            "coverage_pct": obj.get("retrieval_lineage", {}).get("decoder_coverage_pct", 0.0),
            "kosha_records_found": len(obj.get("retrieval_lineage", {}).get("kosha_records", [])),
            "graph_edges_found": len(obj.get("graph_expansion_edges", [])),
            "object_hash": obj.get("object_hash"),
            "replay_safe": obj.get("replay_safe", True),
        })
    return results


def get_graph_expansion_edges(concept_id: str) -> List[Dict[str, Any]]:
    """Return all civilizational graph expansion edges for a concept."""
    graph_data = _load_json(GRAPH_EXPANSION_FILE) or {}
    return [
        e for e in graph_data.get("edges", [])
        if e.get("from") == concept_id or e.get("to") == concept_id
    ]


def validate_provenance_chain(concept_id: str) -> Dict[str, Any]:
    """Validate that the provenance chain for a concept is intact."""
    obj = build_knowledge_object(concept_id)
    if obj.get("status") == "NOT_FOUND":
        return {"valid": False, "reason": "concept_not_found", "concept_id": concept_id}

    provenance = obj.get("provenance", {})
    source_path = provenance.get("source_path", "")
    full_path = BACKEND_DIR / source_path if source_path else None

    source_exists = bool(full_path and full_path.exists())
    content_hash_present = bool(provenance.get("content_hash"))
    object_hash_present = bool(obj.get("object_hash"))
    replay_safe = bool(obj.get("replay_safe"))

    valid = source_exists and content_hash_present and object_hash_present and replay_safe

    return {
        "valid": valid,
        "concept_id": concept_id,
        "source_exists": source_exists,
        "content_hash_present": content_hash_present,
        "object_hash_present": object_hash_present,
        "replay_safe": replay_safe,
        "source_path": source_path,
        "object_hash": obj.get("object_hash"),
    }
