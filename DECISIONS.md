# Project-owner decisions

## D01 — Direct translation, 2026-10-01

The owner requested a new Lotus-King-Translation/Togden-Gongchig-Drelwa repository from the new Tibetan template, explicitly instructed “skip the golden edition phase, and go straight to translating,” and requested the whole text translated to the template's standard using the supplied rough human translation as reference.

This authorizes the provisional-source exception in AGENTS.md. There is no golden edition and no claim of witness collation. The complete work, including closing material, is one bounded working-draft deliverable; parallel ranges are production partitions, not separately released chapters. This implements the requested whole-text scope without claiming chapter release gates have passed.

## Implementation of D01

- Use the unchanged upstream `root/001.txt` as governing electronic transcript. It is aligned to all 4,499 PO UUIDs and avoids tokenizer artifacts. This is an operational source choice, not owner certification of the transcript.
- Preserve every acquired original with its hash and upstream commit. PO English remains attributed reference material, not an approved translation.
- Fix anchors U00001–U04499. Preserve source spelling, punctuation, labels, and unresolved x/×/✖ marks. Strip only outer line whitespace in the reading projection; retain it in `raw_exact` and the archived original.
- Use the active 222-row glossary without changing assignments or promoting proposals.
- The initial deliverable is an annotated LLM working draft for human editing. Structural validation and translator self-check do not constitute independent semantic QC.
- Pairs use the standard schema, identity/order, role and format rules. Provisional provenance uses `source:` in place of `golden:` as documented in FORMAT.md.
