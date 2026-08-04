# API Contracts
## UniGuru Sanskrit Decoder Runtime

**Base URL (local):** `http://127.0.0.1:8010`
**Base URL (production):** `https://uniguru-v2.onrender.com` *(after Render deployment)*
**Schema Version:** `UNIGURU_RUNTIME_RESPONSE_CONTRACT_V1`

---

## POST `/runtime/sanskrit/decode`

Native Sanskrit decoder endpoint that returns a deterministic pipeline, knowledge-graph payload, and provenance-backed governance response for a given Sanskrit concept.

### Request

```json
{
  "query": "string (1–2000 chars, non-whitespace-only)",
  "emit_proof": true
}
```

### Response (200 OK)

```json
{
  "trace_id": "sanskrit_252268d55366e0ec",
  "decoder_result": {
    "canonical_concept": {
      "canonical_name": "धर्म",
      "language": "sa",
      "decoder_version": "sanskrit_decoder_v1"
    },
    "pipeline": [
      { "stage": "śabda", "evidence": "phonological form preserved" },
      { "stage": "dhātu", "evidence": "root-significance inferred" }
    ],
    "knowledge_graph": {
      "nodes": [
        { "id": "concept:धर्म", "type": "concept", "label": "धर्म" }
      ],
      "edges": [
        { "from": "concept:धर्म", "to": "pipeline:धर्म", "label": "decoded_by" }
      ]
    },
    "governed_response": {
      "evidence_classification": {
        "classification": "PROVENANCE_BACKED",
        "evidence_level": "high"
      }
    }
  },
  "governed_response": {
    "evidence_classification": {
      "classification": "PROVENANCE_BACKED",
      "evidence_level": "high"
    }
  },
  "schema_version": "UNIGURU_SANSKRIT_DECODER_RESPONSE_V1"
}
```

### Error Responses

| Code | Condition |
|------|-----------|
| `422` | `query` is empty, whitespace-only, or exceeds 2000 characters |
| `500` | Internal decoder error |

---

## GET `/health`

```json
{
  "status": "ok",
  "service": "uniguru-ecosystem-runtime",
  "schema_version": "UNIGURU_RUNTIME_RESPONSE_CONTRACT_V1",
  "capabilities": ["runtime_execute", "ecosystem_execute", "ecosystem_replay", "mitra_governed_ask"]
}
```

## GET `/ready`

```json
{
  "status": "ready",
  "proof_dir": "/path/to/review_packets/integration_proof",
  "masterdb_present": true
}
```

## GET `/metrics`

Prometheus-format text:
```
# HELP uniguru_ecosystem_runtime_info Ecosystem runtime capability metadata
# TYPE uniguru_ecosystem_runtime_info gauge
uniguru_ecosystem_runtime_info{service="uniguru",capability="bhiv_ecosystem"} 1
# HELP uniguru_ecosystem_runtime_ready Runtime readiness flag
# TYPE uniguru_ecosystem_runtime_ready gauge
uniguru_ecosystem_runtime_ready 1
```

---

## Environment Variables (Production Deployment)

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `UNIGURU_API_AUTH_REQUIRED` | No | `true` | Enable/disable bearer token auth |
| `UNIGURU_API_TOKEN` | If auth=true | — | Production bearer token |
| `UNIGURU_BUCKET_TELEMETRY_ENABLED` | No | `false` | Enable HTTP Bucket telemetry |
| `UNIGURU_BUCKET_TELEMETRY_ENDPOINT` | If bucket=true | — | Bucket collector URL |
| `UNIGURU_BUCKET_TELEMETRY_TOKEN` | If bucket=true | — | Bucket bearer token |
| `UNIGURU_HOST` | No | `0.0.0.0` | Bind address |
| `UNIGURU_PORT` | No | `8000` | Bind port |
