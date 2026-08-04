# REVIEW PACKET — UniGuru Native Sanskrit Decoder

Status: validated locally

## Scope

The native decoder accepts a Sanskrit concept, resolves an exact registry match, and renders the governed sequence: śabda → dhātu → vyākaraṇa → nirukta → bīja → tattva → śakti → functional meaning. It then exposes related concepts as graph edges and returns a deterministic replay key.

## Sanskar source integration

The supplied `uniguru_ai-main.zip` is the canonical Sanskar input. Its Sanskrit ontology contracts were incorporated at `backend/ontology/sanskrit/`:

- immutable `SanskritConcept` schema
- immutable `SanskritRegistry`
- evidence taxonomy
- provenance type

The runtime validates each resolved entry through this schema before it is emitted. Unknown concepts have an empty pipeline and an explicit `UNVERIFIED` / `no_inference` response; no generated etymology is returned.

## Runtime contract

`POST /runtime/sanskrit/decode` accepts `{ "query": string, "emit_proof": boolean }` and returns the decoder payload, a deterministic trace ID, evidence classification, provenance, graph, replay key, and response hash.

## Validation

`pytest backend/tests/test_sanskrit_decoder.py -q` — 3 passed.

Coverage includes Devanagari/Latin alias replay (`धर्म` and `dharma`), ordered eight-layer decoding, graph root identity, the HTTP endpoint, and unknown-term non-inference.
