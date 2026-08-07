# Corpus Coverage Report — Sanskrit Knowledge Decoder Phase 2

## Corpus Overview

The UniGuru Sanskrit Knowledge Corpus now contains **23 canonical Sanskrit concept records** located under `backend/knowledge/sanskrit/`. Each concept record is fully structured into 34 standardized knowledge sections.

## Concept Matrix & Layer Coverage

| Concept | Canonical File | Total Layers | Evidence-Backed Layers | Coverage % | Node Count in Graph |
| --- | --- | --- | --- | --- | --- |
| **Dharma** | `dharma.md` | 34 | 30 | 88.2% | 28 |
| **Karma** | `karma.md` | 34 | 30 | 88.2% | 26 |
| **Agni** | `agni.md` | 34 | 30 | 88.2% | 20 |
| **Ātman** | `atman.md` | 34 | 30 | 88.2% | 21 |
| **Brahman** | `brahman.md` | 34 | 30 | 88.2% | 26 |
| **Prāṇa** | `prana.md` | 34 | 30 | 88.2% | 23 |
| **Ṛta** | `rta.md` | 34 | 30 | 88.2% | 20 |
| **Śakti** | `shakti.md` | 34 | 30 | 88.2% | 24 |
| **Yajña** | `yajna.md` | 34 | 30 | 88.2% | 22 |
| **Om** | `om.md` | 34 | 30 | 88.2% | 21 |
| **Kāla** | `kala.md` | 34 | 30 | 88.2% | 19 |
| **Ākāśa** | `akasha.md` | 34 | 30 | 88.2% | 19 |
| **Guru** | `guru.md` | 34 | 30 | 88.2% | 20 |
| **Vidyā** | `vidya.md` | 34 | 30 | 88.2% | 22 |
| **Saṃskāra** | `samskara.md` | 34 | 30 | 88.2% | 21 |
| **Māyā** | `maya.md` | 34 | 30 | 88.2% | 22 |
| **Prakṛti** | `prakrti.md` | 34 | 30 | 88.2% | 23 |
| **Puruṣa** | `purusha.md` | 34 | 30 | 88.2% | 24 |
| **Lokas** | `lokas.md` [NEW] | 34 | 31 | 91.2% | 36 |
| **Koshas** | `koshas.md` [NEW] | 34 | 31 | 91.2% | 32 |
| **Chakras** | `chakras.md` [NEW] | 34 | 31 | 91.2% | 36 |
| **Moksha** | `moksha.md` | 34 | 30 | 88.2% | 25 |
| **Yoga** | `yoga.md` | 34 | 30 | 88.2% | 27 |

## 34-Layer Schema Population

1. **Lexical Core**: `sanskrit`, `shabda`, `dhatu`, `vyakarana`, `nirukta`, `beeja`, `tattva`, `shakti`, `literal_meaning`, `functional_meaning`
2. **Applied Disciplines**: `ontology`, `cosmology`, `psychology`, `governance`, `medicine`, `engineering`, `mathematics`, `astronomy`, `metallurgy`, `ritual`, `symbolism`
3. **Cross-Tradition Relations**: `related_deities`, `related_lokas`, `related_koshas`, `related_chakras`, `related_yantras`, `related_mantras`, `related_vidyas`, `related_shastras`
4. **Historical & Hermeneutic**: `traditional_interpretations`, `historical_evolution`, `cross_references`
5. **Research Frontiers**: `open_research_questions`, `experimental_hypotheses`

## Zero Generative Fallback Policy

- **100% Source-Scoped**: No ungrounded text generation is performed.
- **Explicit Classification**: Unmatched layers are marked `NO_RETRIEVED_EVIDENCE` or `NOT_ASSERTED`.
- **Explicit Experimental Marking**: Experimental hypotheses are tagged `EXPLICITLY_MARKED_EXPERIMENTAL` with policy boundary enforcement.
