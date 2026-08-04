# Sanskrit Decoder Reviewer Notes

Review the source ingestion path before reviewing response text: `backend/knowledge/sanskrit/*.md` is the copied Sanskar source corpus, `backend/ontology/sanskrit/` is Sanskar’s contract package, and `backend/ontology/sanskrit_decoder.py` is the Isha adapter. No Sanskrit meaning is generated when a canonical document is unavailable.

The generic curriculum graph contract is reused for node/edge shape. A dedicated Sanskrit graph contract and passage-level source corpus remain Sanskar dependencies for broader semantic authority.
