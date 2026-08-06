# REVIEW PACKET — Native Sanskrit Knowledge Decoder
**Sprint:** Sanskrit Knowledge Decoder (Sprint 3)
**Owner:** Isha Singh — UniGuru Runtime Owner
**Date:** 2026
**Status:** COMPLETE (local) | PARTIAL (live ecosystem — blocked by Vijay deployment)

---

## What This Sprint Delivers

A native Sanskrit Knowledge Decoder built into UniGuru that decodes Sanskrit concepts through their own epistemology — not translation, not dictionary lookup, not RAG. Every concept is decoded through 8 canonical layers sourced from Sanskar's immutable knowledge documents.

---

## Canonical Execution Pipeline

```
User Query (Sanskrit or transliteration)
    ↓
LanguageAdapter.normalize_query()
    ↓
decode_sanskrit_concept()  [ontology/sanskrit_decoder.py]
    ↓
load_sanskar_registry()  — loads 6 .md source documents
    ↓
_resolve()  — matches query to canonical concept
    ↓
8-Stage Pipeline:
  śabda → dhātu → vyākaraṇa → nirukta → bīja → tattva → śakti → functional_meaning
    ↓
_graph()  — builds knowledge graph with cross-references
    ↓
_provenance()  — evidence classification per source
    ↓
stable_hash(result)  — deterministic result_hash
    ↓
POST /v2/runtime/sanskrit/decode  — API response
    ↓
execute_ecosystem_runtime()  — TANTRA ecosystem wiring
    ↓
Bucket proof + InsightFlow telemetry + GC + MDU
    ↓
Governed Response
```

---

## Concepts Supported

| Concept | Sanskrit | Transliteration | Sources |
|---|---|---|---|
| Dharma | धर्म | Dharma | Bhagavad Gita, Manusmriti, Mahabharata |
| Karma | कर्म | Karma | Bhagavad Gita, Upanishads |
| Yoga | योग | Yoga | Yoga Sutras of Patanjali, Bhagavad Gita |
| Moksha | मोक्ष | Mokṣa | Upanishads, Bhagavad Gita |
| Atman | आत्मन् | Ātman | Upanishads, Bhagavad Gita |
| Brahman | ब्रह्मन् | Brahman | Upanishads, Brahma Sutras |

---

## Critical Files (3-file execution path)

1. `backend/ontology/sanskrit_decoder.py` — full decoder implementation
2. `backend/service/uniguru_runtime_api.py` — API endpoint `POST /v2/runtime/sanskrit/decode`
3. `backend/service/ecosystem_runtime.py` — TANTRA ecosystem wiring via `_attach_sanskrit_decoder()`

---

## Evidence

- Proof logs: `review_packets/proof_logs/isha_sanskrit_dharma_v1.json`
- Ecosystem execution: `review_packets/integration_proof/ecosystem_execution_isha_sanskrit_dharma_v1.json`
- Replay verification: `review_packets/integration_proof/replay_verification_isha_sanskrit_dharma_v1.json`
- Bucket proof: `review_packets/integration_proof/bucket_isha_sanskrit_dharma_v1.json`
- Test suite: `backend/tests/test_sanskrit_decoder.py`, `backend/tests/test_sanskrit_ecosystem_integration.py`

---

## Blockers (not Isha's lane)

| Blocker | Owner | Impact |
|---|---|---|
| InsightFlow not deployed | Vijay | `live_emitted: false` for InsightFlow |
| PRANA not deployed | Vijay | No PRANA trust verification |
| KARMA not deployed | Vijay | No KARMA capability consumption |
| GC endpoint missing | GC team | `live: false` for governance validation |
| MDU_API_KEY missing | MDU team | `live: false` for schema/provenance validation |

All integration clients are wired and will activate automatically when endpoints are provided.
