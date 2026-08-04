# Execution Flow

1. The runtime receives a Sanskrit query through the FastAPI endpoint.
2. The decoder builds a canonical concept object and a deterministic pipeline over the stages śabda → dhātu → vyākaraṇa → nirukta → bīja → tattva → śakti → functional meaning.
3. The result is emitted as a provenance-backed, replay-safe payload with a stable hash.
4. The response is returned to the caller and optionally written to the proof log directory.
