"""Deterministic, bounded Sanskrit concept decoder.

The decoder intentionally does not derive Sanskrit etymologies at request time.
It only renders entries attested in the versioned native registry; an unknown
term is returned as an explicit unverified observation rather than a guess.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional

from memory.constitutional_semantic_memory import stable_hash
from ontology.sanskrit.schema import SanskritConcept, sanskrit_concept_from_dict, sanskrit_concept_to_dict


DECODER_VERSION = "sanskrit_decoder_v2"
REGISTRY_VERSION = "sanskrit_concept_registry_v1"
STAGES = ("śabda", "dhātu", "vyākaraṇa", "nirukta", "bīja", "tattva", "śakti", "functional_meaning")

# This is a deliberately small, reviewable seed registry.  Each semantic field
# is source-scoped and is never presented as a generated linguistic analysis.
_REGISTRY: Dict[str, Dict[str, Any]] = {
    "dharma": {
        "canonical_name": "dharma", "sanskrit": "धर्म", "iast": "dharma",
        "aliases": ("धर्म", "dharma"),
        "layers": {
            "śabda": "धर्म (dharma)", "dhātu": "√धृ (dhṛ): to hold or support.",
            "vyākaraṇa": "Nominal form recorded as dharma.",
            "nirukta": "A registry-attested explanatory gloss: that which upholds.",
            "bīja": "sustaining order", "tattva": "order, duty, and sustaining principle",
            "śakti": "orients conduct toward what sustains", "functional_meaning": "A principle or duty understood as sustaining order.",
        },
        "cross_references": (("karma", "contextualizes_action"), ("yoga", "supports_disciplined_practice")),
        "sources": ("UniGuru curated Sanskrit registry seed v1; editorial review required for expansion.",),
    },
    "karma": {
        "canonical_name": "karma", "sanskrit": "कर्म", "iast": "karma", "aliases": ("कर्म", "karma"),
        "layers": {"śabda": "कर्म (karma)", "dhātu": "√कृ (kṛ): to do or make.", "vyākaraṇa": "Nominal form recorded as karma.", "nirukta": "A registry-attested explanatory gloss: action or deed.", "bīja": "action", "tattva": "intentional action and its context", "śakti": "connects action with consequence", "functional_meaning": "Action, deed, or work considered in its consequences."},
        "cross_references": (("dharma", "evaluates_action"),), "sources": ("UniGuru curated Sanskrit registry seed v1; editorial review required for expansion.",),
    },
    "yoga": {
        "canonical_name": "yoga", "sanskrit": "योग", "iast": "yoga", "aliases": ("योग", "yoga"),
        "layers": {"śabda": "योग (yoga)", "dhātu": "√युज् (yuj): to yoke or join.", "vyākaraṇa": "Nominal form recorded as yoga.", "nirukta": "A registry-attested explanatory gloss: joining or disciplined integration.", "bīja": "integration", "tattva": "disciplined integration", "śakti": "organizes attention and practice", "functional_meaning": "A disciplined mode of integration or union."},
        "cross_references": (("dharma", "supports_practice"),), "sources": ("UniGuru curated Sanskrit registry seed v1; editorial review required for expansion.",),
    },
    "moksha": {
        "canonical_name": "moksha", "sanskrit": "मोक्ष", "iast": "mokṣa", "aliases": ("मोक्ष", "moksha", "mokṣa"),
        "layers": {"śabda": "मोक्ष (mokṣa)", "dhātu": "√मुच् (muc): to release.", "vyākaraṇa": "Nominal form recorded as mokṣa.", "nirukta": "A registry-attested explanatory gloss: release or liberation.", "bīja": "release", "tattva": "liberation", "śakti": "frames release from binding conditions", "functional_meaning": "Release or liberation; traditions specify this differently."},
        "cross_references": (("karma", "contrasts_bondage_and_release"),), "sources": ("UniGuru curated Sanskrit registry seed v1; editorial review required for expansion.",),
    },
}


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", value or "").strip()).casefold()


def _entry_for(query: str) -> Optional[Dict[str, Any]]:
    normalized = _normalize(query)
    for entry in _REGISTRY.values():
        if normalized in {_normalize(alias) for alias in entry["aliases"]}:
            return entry
    return None


def _pipeline(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"stage": stage, "value": entry["layers"][stage], "evidence_classification": "REGISTRY_ATTESTED", "source_ids": ["registry:seed-v1"]} for stage in STAGES]


def _sanskar_contract(entry: Dict[str, Any]) -> SanskritConcept:
    """Project the decoder entry through Sanskar's immutable schema contract."""
    related = [target for target, _ in entry["cross_references"]]
    layers = entry["layers"]
    return sanskrit_concept_from_dict({
        "concept_id": "sanskrit:" + entry["canonical_name"],
        "canonical_name": entry["canonical_name"],
        "sanskrit": entry["sanskrit"],
        "transliteration": entry["iast"],
        "shabda": layers["śabda"], "dhatu": layers["dhātu"],
        "vyakarana": layers["vyākaraṇa"], "nirukta": layers["nirukta"],
        "beeja": layers["bīja"], "tattva": layers["tattva"], "shakti": layers["śakti"],
        "functional_meaning": layers["functional_meaning"],
        "related_concepts": related,
        "ontology_version": REGISTRY_VERSION,
        "semantic_version": DECODER_VERSION,
    })


def _unknown_result(query: str) -> Dict[str, Any]:
    canonical = unicodedata.normalize("NFC", query.strip())
    result = {
        "canonical_concept": {"canonical_name": canonical, "language": "und", "decoder_version": DECODER_VERSION, "registry_version": REGISTRY_VERSION, "resolution": "UNRESOLVED"},
        "pipeline": [], "knowledge_graph": {"nodes": [{"id": "query:" + canonical, "type": "unresolved_query", "label": canonical}], "edges": []}, "cross_references": [],
        "functional_meaning": {"summary": "No registry-attested Sanskrit concept was found; no etymology or interpretation was inferred.", "confidence": 0.0},
        "provenance": {"registry_version": REGISTRY_VERSION, "source_ids": [], "replay_safe": True, "provenance_hash": stable_hash({"query": canonical, "registry_version": REGISTRY_VERSION})},
        "governed_response": {"evidence_classification": {"classification": "UNVERIFIED", "evidence_level": "none", "notes": "Unknown concepts require a governed registry addition before decoding."}, "research_classification": "needs_curated_source", "governance_state": "no_inference"},
    }
    result["result_hash"] = stable_hash(result)
    return result


def decode_sanskrit_concept(query: str) -> Dict[str, Any]:
    """Decode an exact registry match, or return a deterministic no-inference result."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    entry = _entry_for(query)
    if entry is None:
        return _unknown_result(query)
    contract = _sanskar_contract(entry)
    canonical = entry["canonical_name"]
    pipeline = _pipeline(entry)
    concept_id = "concept:" + canonical
    nodes = [{"id": concept_id, "type": "sanskrit_concept", "label": entry["sanskrit"]}]
    edges: List[Dict[str, str]] = []
    previous = concept_id
    for stage in STAGES:
        node_id = "stage:" + canonical + ":" + stage
        nodes.append({"id": node_id, "type": "decoder_stage", "label": stage})
        edges.append({"from": previous, "to": node_id, "label": "decoded_through"})
        previous = node_id
    for target, relation in entry["cross_references"]:
        nodes.append({"id": "concept:" + target, "type": "sanskrit_concept_reference", "label": target})
        edges.append({"from": concept_id, "to": "concept:" + target, "label": relation})
    result = {
        "canonical_concept": {"canonical_name": canonical, "sanskrit": entry["sanskrit"], "iast": entry["iast"], "language": "sa", "decoder_version": DECODER_VERSION, "registry_version": REGISTRY_VERSION, "resolution": "REGISTRY_MATCH", "sanskar_contract": sanskrit_concept_to_dict(contract)},
        "pipeline": pipeline, "knowledge_graph": {"nodes": nodes, "edges": edges},
        "cross_references": [{"target": target, "relation": relation, "evidence_classification": "REGISTRY_ATTESTED"} for target, relation in entry["cross_references"]],
        "functional_meaning": {"summary": entry["layers"]["functional_meaning"], "confidence": 0.65},
        "provenance": {"registry_version": REGISTRY_VERSION, "source_ids": ["registry:seed-v1"], "sources": list(entry["sources"]), "replay_safe": True, "provenance_hash": stable_hash({"canonical": canonical, "entry": entry, "registry_version": REGISTRY_VERSION})},
        "governed_response": {"evidence_classification": {"classification": "REGISTRY_ATTESTED", "evidence_level": "curated_internal", "notes": "This is a bounded registry reading, not a claim of universal scholarly consensus."}, "research_classification": "civilizational_knowledge_registry", "governance_state": "read_only_observation"},
    }
    result["result_hash"] = stable_hash(result)
    return result
