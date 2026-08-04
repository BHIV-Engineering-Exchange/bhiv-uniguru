# Sanskrit Integration Summary

The decoder is not only a standalone API. `backend/service/ecosystem_runtime.py` invokes it when a query has an exact Sanskar source-backed canonical match, preserves the decoder lineage in `pipeline_summary.sanskrit_decoder`, and sends the result through existing Bucket, InsightFlow, TANTRA, MDU, and replay paths.

The integration remains source-scoped: the supplied Sanskar documents provide concept records and named canonical sources, but not passage-level excerpts. Cross-text output therefore records references and uncertainty rather than inventing a merged reading.
