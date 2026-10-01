# Togden-Gongchig-Drelwa

Togden Rinpoche's commentary on the Gongchig, prepared from the [Lotus King Tibetan text template](https://github.com/Lotus-King-Translation/tibetan-text-project-template).

The owner explicitly requested direct translation, skipping the golden-edition phase. The Tibetan is a **fixed provisional electronic transcript**, not a collated golden edition. The complete annotated English working draft was translated against that source under the template's [translation standard](guidelines/tibetan_translation_standard_v2.md) and unchanged [222-entry glossary](glossary/expanded_tibetan_english_glossary.csv).

## Reading and project state

- [Current status](PROJECT-STATUS.md) and [translation handoff](translations/HANDOFF.md)
- [Read the English translation](paired/translation.md), [Tibetan source](paired/source.md), or [bilingual reading](paired/bilingual.md)
- [Translation run and limitations](translations/RUN.md), [review notes](translations/notes.json), and [proposed terminology](translations/proposals/)
- [Source provenance and markup recovery](source/PROVENANCE.md)
- [Owner decisions and scope](DECISIONS.md)
- [Paired format](FORMAT.md)

The legacy human translation is retained as attributed reference material, with original PO files and exact UUID alignment. The source contains 4,499 anchors; the reference has 4,482 nonempty entries and 17 empty entries. All 17 gaps were addressed from Tibetan. The complete draft has 970 coherent pairs and 350 source-linked review notes; 61 range-specific terminology proposals remain unapproved. The active 222-row glossary is unchanged.

Agents must read [AGENTS.md](AGENTS.md) first.

## Validation

Python 3, standard library only:

```sh
python3 scripts/source_io.py
python3 scripts/validate_paired.py
python3 scripts/test_validation.py
```

Final draft validation additionally requires `--final` and a hash-bound draft signoff. Mechanical checks establish source preservation, coverage and structural consistency; they do not certify semantic accuracy or constitute independent human review.

The 26-test structural suite and final-mode validation pass. All three translator self-checks are complete. Independent semantic QC and human editorial review have not been performed.
