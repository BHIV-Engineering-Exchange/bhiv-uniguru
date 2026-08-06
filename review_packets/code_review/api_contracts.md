# API Contracts — Sanskrit Decoder Sprint

## POST /v2/runtime/sanskrit/decode

**Request**
```json
{
  "query": "धर्म",
  "emit_proof": true,
  "trace_id": null
}
```

**Response**
```json
{
  "trace_id": "sanskrit_<16-char-hash>",
  "decoder_result": {
    "canonical_concept": {
      "concept_id": "sanskar:sanskrit:dharma",
      "canonical_name": "dharma",
      "sanskrit": "धर्म",
      "transliteration": "Dharma",
      "shabda": "धर्म",
      "dhatu": "धृ (Dhṛ)\nMeaning: To uphold, sustain, support.",
      "vyakarana": "Derived from the verbal root धृ.",
      "nirukta": "That which upholds or sustains.",
      "beeja": null,
      "tattva": "Principle of sustaining cosmic order.",
      "shakti": "Preservation and righteous order.",
      "functional_meaning": "Represents the sustaining principle governing righteous conduct and universal order.",
      "related_concepts": ["karma", "moksha", "yoga"],
      "ontology_version": "sanskar_sanskrit_sources_v1",
      "semantic_version": "isha_sanskrit_decoder_v3"
    },
    "pipeline": [
      { "stage": "śabda", "schema_field": "shabda", "value": "धर्म", "evidence": [...], "classification": ["BHAGAVAD_GITA"], "lineage": {...} },
      { "stage": "dhātu", ... },
      { "stage": "vyākaraṇa", ... },
      { "stage": "nirukta", ... },
      { "stage": "bīja", ... },
      { "stage": "tattva", ... },
      { "stage": "śakti", ... },
      { "stage": "functional_meaning", ... }
    ],
    "knowledge_graph": {
      "graph_id": "UNIGURU_CURRICULUM_KNOWLEDGE_GRAPH_V2",
      "schema_version": "2.0.0",
      "nodes": [...],
      "edges": [...],
      "metadata": { "consistency_valid": true }
    },
    "provenance": {
      "registry_version": "sanskar_sanskrit_sources_v1",
      "schema_version": "isha_sanskrit_decoder_v3",
      "source_documents": [...],
      "lineage": { "concept_id": "...", "source_path": "...", "content_hash": "..." },
      "replay_safe": true
    },
    "governed_response": {
      "evidence_classification": {
        "classification": "SOURCE_SCOPED",
        "evidence_types": ["BHAGAVAD_GITA", "TRADITION"],
        "notes": "Evidence types are derived from the canonical source names supplied by Sanskar."
      },
      "research_classification": "civilizational_knowledge",
      "governance_state": "read_only_observation"
    },
    "result_hash": "<sha256-deterministic>"
  },
  "replay": {
    "replay_key": "<result_hash>",
    "replay_safe": true,
    "input_trace_id_accepted": true
  },
  "schema_version": "UNIGURU_SANSKRIT_DECODER_RESPONSE_V1",
  "response_hash": "<sha256-deterministic>"
}
```

**Unknown concept response**
```json
{
  "decoder_result": {
    "canonical_concept": null,
    "pipeline": [],
    "governed_response": {
      "evidence_classification": { "classification": "UNVERIFIED" },
      "governance_state": "no_inference"
    },
    "result_hash": "<hash>"
  }
}
```

---

## POST /v2/runtime/ecosystem/execute

Runs full ecosystem pipeline including Sanskrit decoder enrichment.

**Request**
```json
{ "query": "धर्म", "emit_proof": true, "trace_id": null }
```

**Key response fields**
```json
{
  "trace_id": "ecosystem_<12-char-hash>",
  "answer": "Represents the sustaining principle governing righteous conduct and universal order.",
  "verification_status": "PARTIAL_VERIFIED_SAMPLE",
  "execution_hash": "<deterministic-sha256>",
  "pipeline_summary": {
    "domain": "sanskrit",
    "sanskrit_decoder": { "result_hash": "...", "canonical_concept": {...} }
  },
  "tantra_ecosystem_fabric": {
    "live": true,
    "status": "ingested",
    "insightcore_auth": true,
    "trace_id": "..."
  }
}
```

---

## POST /v2/runtime/ecosystem/replay

Runs pipeline twice with same trace_id and verifies all deterministic fields are stable.

**Response**
```json
{
  "replay_verified": true,
  "checks": {
    "trace_id_stable": true,
    "vijay_runtime_hash_stable": true,
    "sanskrit_decoder_result_stable": true,
    ...
  }
}
```

---

## GET /health/ecosystem

Verifies live connectivity to InsightCore and other TANTRA services.

**Response (InsightCore live)**
```json
{
  "status": "ok",
  "services": {
    "insightcore": { "live": true, "token_obtained": true },
    "insightbridge": { "configured": true },
    "insightflow": { "enabled": "false", "configured": false },
    "mdu": { "enabled": "false", "configured": false },
    "gc": { "enabled": "false", "configured": false }
  }
}
```

---

## InsightCore — POST /auth/issue

**URL:** `https://insightcore-8tdt.onrender.com/auth/issue`
**Swagger:** `https://insightcore-8tdt.onrender.com/docs#/default/issue_token_auth_issue_post`

**Request**
```json
{ "client_id": "bridge-agent", "client_secret": "bridge_secret_123" }
```

**Response**
```json
{ "token": "<jwt>" }
```

---

## InsightBridge — POST /ingest

**URL:** `https://insightbridge-phase-4-2-integration-demo.onrender.com/ingest`

**Request**
```json
{
  "telemetry_data": {
    "request_id": "<trace_id>",
    "path": "/ask",
    "method": "POST",
    "status_code": 200,
    "latency_ms": 0
  },
  "metadata": {
    "user_id": "uniguru-runtime",
    "event_type": "UNIGURU_CURRICULUM_QUERY",
    "verification_status": "PARTIAL_VERIFIED_SAMPLE",
    "system": "uniguru"
  }
}
```
