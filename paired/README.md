# Paired reading

The canonical reading files are source.md and translation.md. Shared TGD pair IDs refer to coherent translation units; their markers map every original U anchor exactly once.

Source `format` is prose, verse, h1, h2 or h3. English inherits it. D01's explicit provisional-source exception uses `source:` provenance instead of `golden:`. See ../FORMAT.md.

Initial assembly uses ../scripts/assemble_draft.py on reviewed translation batches. The files are then the canonical publication surface. The manifest records structure and hashes; ../scripts/validate_paired.py rejects source loss, mismatch, unrecorded changes, broken notes and invalid release state.

An unreleased draft can contain explicit unprocessed markers. Final draft validation rejects those markers. Source-linked unresolved readings remain visible review items and are counted separately from translation coverage.
