# SELF VALIDATION — Sanskrit Decoder Sprint

- The supplied Sanskar schema is used to validate every resolved concept.
- Registry aliases replay to one canonical concept and one result hash.
- Semantic claims have `REGISTRY_ATTESTED` rather than an unsupported universal-canon label.
- Unknown terms return `UNVERIFIED`, an empty pipeline, and `no_inference`.
- The decoder result and trace key contain no wall-clock value, so replay is deterministic.
