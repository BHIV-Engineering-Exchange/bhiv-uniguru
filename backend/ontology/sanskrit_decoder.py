"""Isha decoder adapter over Sanskar's immutable Sanskrit source documents."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

from memory.constitutional_semantic_memory import stable_hash
from ontology.sanskrit.evidence import EvidenceType
from ontology.sanskrit.provenance import Provenance
from ontology.sanskrit.registry import SanskritRegistry
from ontology.sanskrit.schema import SanskritConcept, sanskrit_concept_from_dict, sanskrit_concept_to_dict

DECODER_VERSION = "isha_sanskrit_decoder_v3"
REGISTRY_VERSION = "sanskar_sanskrit_sources_v1"
SOURCE_DIR = Path(__file__).resolve().parents[1] / "knowledge" / "sanskrit"
STAGES = (("śabda", "shabda"), ("dhātu", "dhatu"), ("vyākaraṇa", "vyakarana"), ("nirukta", "nirukta"), ("bīja", "beeja"), ("tattva", "tattva"), ("śakti", "shakti"), ("functional_meaning", "functional_meaning"))
_HEADERS = {"canonical name": "canonical_name", "sanskrit": "sanskrit", "transliteration": "transliteration", "śabda": "shabda", "dhātu": "dhatu", "vyākaraṇa": "vyakarana", "nirukta": "nirukta", "bīja": "beeja", "tattva": "tattva", "śakti": "shakti", "functional meaning": "functional_meaning", "cross references": "related_concepts", "canonical sources": "sources"}


def _normal(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", value or "").strip()).casefold()


def _section_map(text: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
    for index, match in enumerate(matches):
        key = _HEADERS.get(_normal(match.group(1)))
        if key:
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            sections[key] = text[match.end():end].strip()
    return sections


def _list(value: str) -> List[str]:
    return [line[2:].strip() for line in value.splitlines() if line.strip().startswith("- ")]


def _evidence_type(source: str) -> EvidenceType:
    token = _normal(source)
    if "gita" in token:
        return EvidenceType.BHAGAVAD_GITA
    if "upanishad" in token:
        return EvidenceType.UPANISHAD
    if "sutra" in token:
        return EvidenceType.PRIMARY_CANON
    return EvidenceType.TRADITION


def load_sanskar_registry() -> tuple[SanskritRegistry, Dict[str, Dict[str, Any]]]:
    registry = SanskritRegistry()
    metadata: Dict[str, Dict[str, Any]] = {}
    for path in sorted(SOURCE_DIR.glob("*.md")):
        if path.name == "README.md":
            continue
        sections = _section_map(path.read_text(encoding="utf-8"))
        required = ("canonical_name", "sanskrit", "transliteration", "shabda", "dhatu", "vyakarana", "nirukta", "functional_meaning")
        if any(not sections.get(field) for field in required):
            raise ValueError(f"Invalid Sanskar source document: {path}")
        name = sections["canonical_name"].strip().lower()
        concept = sanskrit_concept_from_dict({
            "concept_id": "sanskar:sanskrit:" + name,
            "canonical_name": name,
            "sanskrit": sections["sanskrit"], "transliteration": sections["transliteration"],
            "shabda": sections["shabda"], "dhatu": sections["dhatu"], "vyakarana": sections["vyakarana"], "nirukta": sections["nirukta"],
            "beeja": None if sections.get("beeja", "").strip() in {"", "—"} else sections["beeja"],
            "tattva": sections.get("tattva") or None, "shakti": sections.get("shakti") or None,
            "functional_meaning": sections["functional_meaning"], "related_concepts": [item.lower() for item in _list(sections.get("related_concepts", ""))],
            "ontology_version": REGISTRY_VERSION, "semantic_version": DECODER_VERSION,
        })
        registry.register(concept)
        metadata[concept.concept_id] = {"path": str(path.relative_to(Path(__file__).resolve().parents[1]).as_posix()), "sources": _list(sections.get("sources", "")), "content_hash": stable_hash(path.read_text(encoding="utf-8"))}
    return registry, metadata


def _resolve(query: str, registry: SanskritRegistry) -> Optional[SanskritConcept]:
    needle = _normal(query)
    matches = []
    for concept in registry.list_concepts():
        aliases = (concept.canonical_name, concept.sanskrit, concept.transliteration, concept.transliteration.replace("ṣ", "sh").replace("ā", "a").replace("ṛ", "r"))
        if needle in {_normal(alias) for alias in aliases}:
            matches.append(concept)
    return matches[0] if len(matches) == 1 else None


def _provenance(concept: SanskritConcept, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"source_id": stable_hash({"concept": concept.concept_id, "source": source})[:16], "evidence_type": _evidence_type(source).value, "provenance": Provenance(source_text=source). __dict__} for source in metadata["sources"]]


def _graph(concept: SanskritConcept, registry: SanskritRegistry, metadata: Dict[str, Any]) -> Dict[str, Any]:
    nodes = [{"id": concept.concept_id, "type": "concept", "label": concept.canonical_name, "address": metadata["path"], "provenance": metadata["path"]}]
    edges = []
    known = {row.concept_id for row in registry.list_concepts()}
    for related in sorted(concept.related_concepts):
        target = "sanskar:sanskrit:" + related
        if target in known:
            nodes.append({"id": target, "type": "concept", "label": related, "address": "backend/knowledge/sanskrit/" + related + ".md"})
            edges.append({"from": concept.concept_id, "to": target, "type": "cross_reference", "evidence_type": EvidenceType.DERIVED.value, "provenance": metadata["path"]})
    if any(edge["from"] not in {node["id"] for node in nodes} or edge["to"] not in {node["id"] for node in nodes} for edge in edges):
        raise ValueError("Sanskrit graph consistency validation failed")
    return {"graph_id": "UNIGURU_CURRICULUM_KNOWLEDGE_GRAPH_V2", "schema_version": "2.0.0", "nodes": nodes, "edges": edges, "metadata": {"adapter": "isha_sanskrit_source_graph", "consistency_valid": True, "source_snapshot_hash": metadata["content_hash"]}}


def decode_sanskrit_concept(query: str) -> Dict[str, Any]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    registry, metadata_by_id = load_sanskar_registry()
    concept = _resolve(query, registry)
    if concept is None:
        result = {"canonical_concept": None, "pipeline": [], "cross_text_synthesis": {"status": "NO_CANONICAL_EVIDENCE", "claims": []}, "knowledge_graph": {"nodes": [], "edges": [], "metadata": {"consistency_valid": True}}, "provenance": {"registry_version": REGISTRY_VERSION, "lineage": [], "replay_safe": True}, "governed_response": {"evidence_classification": {"classification": "UNVERIFIED", "evidence_types": [], "notes": "No Sanskar canonical source document matched this query."}, "research_classification": "UNVERIFIED", "governance_state": "no_inference"}}
        result["result_hash"] = stable_hash(result)
        return result
    metadata = metadata_by_id[concept.concept_id]
    canonical = sanskrit_concept_to_dict(concept)
    pipeline = [{"stage": stage, "schema_field": field, "value": canonical[field], "evidence": _provenance(concept, metadata), "classification": [item["evidence_type"] for item in _provenance(concept, metadata)], "lineage": {"concept_id": concept.concept_id, "source_path": metadata["path"], "content_hash": metadata["content_hash"]}} for stage, field in STAGES]
    cross_claims = [{"target": related, "claim": f"{concept.canonical_name} is cross-referenced with {related} by the Sanskar source document.", "classification": EvidenceType.DERIVED.value, "source_path": metadata["path"], "status": "DERIVED_FROM_CANONICAL_CROSS_REFERENCE"} for related in sorted(concept.related_concepts)]
    result = {"canonical_concept": canonical, "pipeline": pipeline, "cross_references": cross_claims, "cross_text_synthesis": {"status": "SOURCE_REFERENCES_ONLY", "canonical_claims": [{"claim": concept.functional_meaning, "classification": [item["evidence_type"] for item in _provenance(concept, metadata)], "source_path": metadata["path"]}], "derived_interpretations": cross_claims, "conflicts": [], "uncertainty": "The supplied source documents list canonical texts but do not contain passage-level excerpts; no cross-text semantic merge is asserted."}, "knowledge_graph": _graph(concept, registry, metadata), "functional_meaning": {"summary": concept.functional_meaning, "classification": "SOURCE_SCOPED_CANONICAL_TEXT"}, "provenance": {"registry_version": REGISTRY_VERSION, "schema_version": DECODER_VERSION, "source_documents": _provenance(concept, metadata), "lineage": {"concept_id": concept.concept_id, "source_path": metadata["path"], "content_hash": metadata["content_hash"]}, "replay_safe": True}, "governed_response": {"evidence_classification": {"classification": "SOURCE_SCOPED", "evidence_types": sorted({item["evidence_type"] for item in _provenance(concept, metadata)}), "notes": "Evidence types are derived from the canonical source names supplied by Sanskar."}, "research_classification": "civilizational_knowledge", "governance_state": "read_only_observation"}}
    result["result_hash"] = stable_hash(result)
    return result
