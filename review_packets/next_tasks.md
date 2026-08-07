# Next Tasks & Roadmap — Sanskrit Knowledge Decoder Phase 3

Having successfully completed Phase 2 (Civilizational Knowledge Enrichment Engine), the following tasks are recommended for Phase 3:

## Phase 3 Roadmap

1. **Multi-Hop Knowledge Graph Traversal API**:
   - Implement `/v2/runtime/sanskrit/graph/traverse` endpoint allowing multi-hop graph queries (e.g., `Prāṇa -> Koshas -> Chakras -> Bīja -> Mantras`).
   - Support depth-bounded sub-graph extraction for visual UI components.

2. **Expanded Vedāṅga Grammar Integration**:
   - Enrich `vyākaraṇa` sections across all concepts with direct Pāṇini Ashtadhyayi sūtra text and rule dependency chains from `backend/knowledge/gurukul/sanskrit/grammar.md`.

3. **Audio-Acoustic Phonetic Engine**:
   - Integrate Sanskrit acoustic pronunciation metadata and bīja sound frequency maps into the `bīja` and `śabda` layers for voice synthesis interfaces.

4. **Cross-Textual Comparative Hermeneutics**:
   - Connect Darśana-specific commentary variations (Advaita, Viśiṣṭādvaita, Dvaita, Śaivadvaita, Sāṃkhya-Yoga) into structured comparative matrices per concept.
