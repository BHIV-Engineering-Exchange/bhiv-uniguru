# Reviewer Notes — Code Packet (Sprint: Sanskrit Decoder Phase 2)

This code packet contains the core files modified in Phase 2 for reviewer inspection.

## Critical Files Included in Packet

1. `sanskrit_decoder.py`: The central civilizational knowledge engine implementation.
2. `uniguru_runtime_api.py`: FastAPI service exposing `/runtime/sanskrit/decode` and `/v2/runtime/sanskrit/decode`.
3. `test_sanskrit_decoder.py`: Test suite verifying decoder correctness, 23 concepts, coverage metrics, and v2 endpoints.

## Summary of Code Changes

### 1. Robust Alias & Transliteration Resolution (`sanskrit_decoder.py`)
- Standardized diacritic stripping (`unicodedata.normalize("NFD")`) and case folding.
- Built alias sets covering Devanagari script, IAST, simple ASCII transliterations, diacritic-free forms, and singular/plural variations (`lokas` <-> `loka`, `koshas` <-> `kosha`, `chakras` <-> `chakra`, `prakrti` <-> `prakriti`, `samskara` <-> `samkara`).

### 2. Multi-Source Retrieval (`sanskrit_decoder.py`)
- Searches across `KOSHA_DIR` JSON files, `kosha_entries.jsonl`, and Gurukul knowledge markdown records (`backend/knowledge/gurukul/`).
- Computes deterministic token overlap scoring and attaches exact provenance lineage metadata.

### 3. Civilizational Knowledge Graph Construction (`sanskrit_decoder.py`)
- Extracts entities from 34 knowledge layers: `related_shastras`, `related_deities`, `related_lokas`, `related_koshas`, `related_chakras`, `related_yantras`, `related_vidyas`, and `retrieved_evidence`.
- Constructs typed directed edges (`referenced_in_shastra`, `related_deity`, `related_loka`, `related_kosha`, `related_chakra`, `related_yantra`, `related_vidya`, `retrieved_evidence`).
- Validates graph integrity: guarantees 0 orphaned nodes and directed edge endpoint existence.

### 4. API & Integration Layer (`uniguru_runtime_api.py`)
- Added `@app.post("/v2/runtime/sanskrit/decode")` endpoint.
- Returns `UNIGURU_SANSKRIT_DECODER_RESPONSE_V1` payload with complete 34-layer civilizational knowledge object, knowledge graph, and governed response.

## File Responsibilities Map

| File | Primary Responsibility |
| --- | --- |
| `backend/ontology/sanskrit_decoder.py` | Core decoding, retrieval, layer populating, graph building |
| `backend/service/uniguru_runtime_api.py` | API routing and HTTP request/response handling |
| `backend/tests/test_sanskrit_decoder.py` | Automated testing for concept coverage, graph safety, and endpoints |
| `backend/knowledge/sanskrit/*.md` | Source-backed canonical 34-layer concept records |
