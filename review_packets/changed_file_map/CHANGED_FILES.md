# Changed File Map — UniGuru Sanskrit Knowledge Decoder Phase 2

This document maps all files modified or added in Phase 2, explaining their responsibilities and system connections.

## Core Ontology & Decoder Engine

### `backend/ontology/sanskrit_decoder.py` (MODIFIED)
- **Role**: Central Sanskrit Civilizational Knowledge Decoder.
- **Key Changes**:
  - Enhanced `_resolve()` for alias matching (Devanagari, IAST, English transliteration, diacritic removal, singular/plural forms).
  - Expanded `_kosha_records()` multi-source retrieval engine across Kosha JSON/JSONL entries and Gurukul datasets.
  - Updated `_evidence_type()` classification for expanded Vedic/Upanishadic/Gītā sources.
  - Expanded `_graph()` to construct deep multi-tradition graph structures including `lokas`, `koshas`, `chakras`, `yantras`, `vidyas`, `shastras`, `deities`, and retrieved evidence nodes with 0 orphaned nodes.

---

## Canonical Knowledge Corpus (`backend/knowledge/sanskrit/`)

### [NEW] `backend/knowledge/sanskrit/lokas.md`
- **Role**: Canonical 34-layer record for Lokas (planes of existence/cosmological realms).
- **Connects to**: Cosmology, Psychology, Governance, Vāstu, Lokas graph nodes.

### [NEW] `backend/knowledge/sanskrit/koshas.md`
- **Role**: Canonical 34-layer record for Koshas (five sheaths of embodiment).
- **Connects to**: Taittirīya Upanishad, Āyurveda, Psychology, Yoga, Koshas graph nodes.

### [NEW] `backend/knowledge/sanskrit/chakras.md`
- **Role**: Canonical 34-layer record for Chakras (subtle energy vortices along Suṣumnā).
- **Connects to**: Ṣaṭ-Cakra-Nirūpaṇa, Tantra, Āyurveda, Endocrine science, Chakras graph nodes.

---

## API Service Layer & Ecosystem Integration

### `backend/service/uniguru_runtime_api.py` (MODIFIED)
- **Role**: Unified Constitutional Runtime FastAPI server.
- **Key Changes**:
  - Added `@app.post("/v2/runtime/sanskrit/decode")` route alias for explicit Phase 2 contract compliance alongside `/runtime/sanskrit/decode`.

### `backend/service/ecosystem_runtime.py` (VERIFIED/INTEGRATED)
- **Role**: TANTRA Runtime Ecosystem execution engine.
- **Connection**: Leverages `_attach_sanskrit_decoder` to attach 34-layer Sanskrit knowledge objects, Vijay replay validation, and InsightFlow observability to ecosystem queries.

---

## Testing & Validation Suite

### `backend/tests/test_sanskrit_decoder.py` (MODIFIED)
- **Role**: Unit test suite for Sanskrit decoder.
- **Key Changes**: Updated assertions for 23 concepts, tested new Lokas/Koshas/Chakras concepts, validated `/v2/runtime/sanskrit/decode` endpoint.

### `backend/tests/test_mdu_client.py` (MODIFIED)
- **Role**: MDU Client test suite.
- **Key Changes**: Added mock timestamp fields to match `DatasetResponse.from_dict` schema.

---

## Review Packets & Proof Artifacts

### `scripts/generate_phase2_proof_logs.py` (NEW)
- **Role**: Utility script generating deterministic JSON proof artifacts for concept decodes and ecosystem replay.

### `review_packets/proof_logs/` (NEW PROOF ARTIFACTS)
- Proof logs for `dharma`, `karma`, `lokas`, `koshas`, `chakras`, `prana`, `agni`, `atman`, `brahman`.

### `review_packets/integration_proof/` (NEW INTEGRATION ARTIFACTS)
- `ecosystem_execution_isha_sanskrit_dharma_v2.json`
- `replay_verification_isha_sanskrit_dharma_v2.json`
- `ecosystem_execution_latest.json`
