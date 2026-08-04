# Sanskrit Decoder API Contract

`POST /runtime/sanskrit/decode` is a source-scoped inspection route. It returns a Sanskar-schema concept, eight schema-backed semantic layers, claim/source evidence types, provenance, cross-reference graph, replay key, and response hash.

`POST /runtime/ecosystem/execute` is the governed integration route. For a query that resolves in Sanskar’s canonical source documents, it attaches `pipeline_summary.sanskrit_decoder` and continues through existing Vijay validation, Bucket, InsightFlow, MDU, TANTRA, and replay infrastructure.

Unknown Sanskrit terms return `UNVERIFIED` and `no_inference`; they do not receive generated semantic content.
