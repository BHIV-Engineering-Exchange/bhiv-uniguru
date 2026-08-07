# Provenance Validation Report — Sanskrit Knowledge Decoder Phase 2

## Provenance Architecture

The UniGuru Sanskrit Knowledge Enrichment Engine enforces strict provenance tracking across all decoded concepts. Provenance metadata is generated deterministically at decode time and attached to every claim and graph node.

## Lineage Protocol & Metadata

Every claim in the 34-layer civilizational knowledge object includes:
- `source_id`: 16-character SHA-256 hash derived from concept ID and source reference.
- `evidence_type`: Formally classified evidence category (`VEDA`, `UPANISHAD`, `BHAGAVAD_GITA`, `PRIMARY_CANON`, `PANINI`, `NIRUKTA`, `COMMENTARY`, `TRADITION`, `DERIVED`).
- `source_path`: Relative repository path to canonical markdown file.
- `content_hash`: Cryptographic hash of the source document text.
- `retrieval_system`: `sanskrit_lexical_records` or `uniguru_kosha`.

## Evidence Classification Rules

```python
if "gita" in token or "bhagavad" in token: -> EvidenceType.BHAGAVAD_GITA
if "upanishad" in token or "taittiriya" in token: -> EvidenceType.UPANISHAD
if "veda" in token or "rigveda" in token: -> EvidenceType.VEDA
if "panini" in token or "ashtadhyayi" in token: -> EvidenceType.PANINI
if "nirukta" in token or "yaska" in token: -> EvidenceType.NIRUKTA
if "bhasya" in token or "sankara" in token: -> EvidenceType.COMMENTARY
```

## MDU Intelligence Data Universe Integration

- **Canonical Dataset ID**: `BHIV-DS-UNIGURU-RUNTIME-001`
- **Replay Events Dataset ID**: `BHIV-DS-REPLAY-SEMANTIC-EVENTS-001`
- **Lineage Chain Dataset ID**: `BHIV-DS-LINEAGE-CHAIN-001`
- **Schema Compatibility**: Verified live/mocked via `MDUClient.validate_schema()` and `MDUClient.validate_provenance()`.

## Audit & Verification Logs

Machine-readable proof logs validating lineage preservation across executions:
- `review_packets/proof_logs/sanskrit_decoder_proof_dharma_v2.json`
- `review_packets/proof_logs/sanskrit_decoder_proof_lokas_v2.json`
- `review_packets/proof_logs/sanskrit_decoder_proof_koshas_v2.json`
- `review_packets/proof_logs/sanskrit_decoder_proof_chakras_v2.json`
