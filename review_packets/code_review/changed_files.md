# Changed Files — Sanskrit Decoder Sprint

## New Files

| File | Purpose |
|---|---|
| `backend/ontology/sanskrit_decoder.py` | Full 8-stage Sanskrit decoder implementation |
| `backend/ontology/sanskrit/schema.py` | SanskritConcept frozen dataclass + validation |
| `backend/ontology/sanskrit/registry.py` | Immutable SanskritRegistry |
| `backend/ontology/sanskrit/evidence.py` | EvidenceType enum (10 values) |
| `backend/ontology/sanskrit/provenance.py` | Provenance dataclass with trace_id + artifact_hash |
| `backend/knowledge/sanskrit/dharma.md` | Sanskar source document |
| `backend/knowledge/sanskrit/karma.md` | Sanskar source document |
| `backend/knowledge/sanskrit/yoga.md` | Sanskar source document |
| `backend/knowledge/sanskrit/moksha.md` | Sanskar source document |
| `backend/knowledge/sanskrit/atman.md` | Sanskar source document |
| `backend/knowledge/sanskrit/brahman.md` | Sanskar source document |
| `backend/tests/test_sanskrit_decoder.py` | Decoder unit + API tests |
| `backend/tests/test_sanskrit_ecosystem_integration.py` | End-to-end ecosystem integration tests |

## Modified Files

| File | Change |
|---|---|
| `backend/integrations/tantra_ecosystem_bridge.py` | Replaced local Python imports with HTTP clients for InsightCore + InsightBridge. Added token caching, health check function. |
| `backend/integrations/tantra_sdk_adapter.py` | Removed hardcoded Windows paths. Kept env var + relative path only. |
| `backend/integrations/insightflow_client.py` | Rewrote to use Vijay's canonical `/telemetry/ingest` endpoint. Added `INSIGHTFLOW_TOKEN=flow_secret_789`. |
| `backend/integrations/mdu_client.py` | No change this sprint — already complete. |
| `backend/integrations/gc_client.py` | No change this sprint — already complete. |
| `backend/ontology/sanskrit/provenance.py` | Added `trace_id: Optional[str]` and `artifact_hash: Optional[str]` fields. |
| `backend/service/api.py` | Replaced file-backed `log_to_bucket()` with `BucketTelemetryClient.emit()`. Added `GET /health/ecosystem` endpoint. |
| `backend/service/ecosystem_runtime.py` | Added `_attach_sanskrit_decoder()`. Wired Sanskrit decoder into `execute_ecosystem_runtime()`. |
| `backend/service/uniguru_runtime_api.py` | Added `POST /runtime/sanskrit/decode` endpoint. |
| `backend/main.py` | Mounted `uniguru_runtime_api` under `/v2` so all runtime routes are reachable. |
| `uniguru/.env.production` | Added: `TANTRA_SDK_ENABLED`, `INSIGHT_CORE_URL`, `INSIGHT_CORE_CLIENT_ID`, `INSIGHT_CORE_CLIENT_SECRET`, `INSIGHT_BRIDGE_URL`, `INSIGHTFLOW_TOKEN`, `INSIGHTFLOW_BASE_URL`, `GC_ENABLED`, `MDU_ENABLED`, `TANTRA_SDK_BASE_URL`. Fixed `UNIGURU_ENGINE_URL` from localhost to deployed URL. |

## Files NOT Changed (intentionally)

| File | Reason |
|---|---|
| `backend/kosha/deterministic_pipeline.py` | Core pipeline is correct — no changes needed |
| `backend/memory/constitutional_semantic_memory.py` | `stable_hash()` is correct — no changes needed |
| `backend/ontology/snapshots/snapshot_v1.json` | Sanskrit domain node missing — blocked by Sanskar |
