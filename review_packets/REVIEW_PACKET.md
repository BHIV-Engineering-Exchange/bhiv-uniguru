# UniGuru Sanskrit Decoder — Isha Sprint Review Packet

## Implemented locally

- Sanskar source corpus ingested at `backend/knowledge/sanskrit/` (six concepts).
- Decoder uses Sanskar’s `SanskritConcept`, `SanskritRegistry`, `EvidenceType`, and `Provenance` contracts.
- Exact Sanskrit/transliteration resolution, eight-layer decoding, source-scoped explanations, cross-references, provenance, and graph consistency validation.
- Existing Vijay ecosystem runtime now attaches a canonical Sanskrit result, then emits Bucket, InsightFlow, MDU/TANTRA, and replay evidence.

## Evidence

- `integration_proof/ecosystem_execution_isha_sanskrit_dharma_v1.json`
- `integration_proof/bucket_isha_sanskrit_dharma_v1.json`
- `integration_proof/replay_verification_isha_sanskrit_dharma_v1.json`
- Focused validation: `7 passed`.

## Boundaries

The supplied Sanskar corpus has named source references but no passage-level excerpts, edition, translator, chapter, or verse locations. The runtime preserves those fields as unavailable and does not fabricate them. Production deployment validation is not represented by the local proof artifacts.
