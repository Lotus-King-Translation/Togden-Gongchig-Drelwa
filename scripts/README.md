# Project tools

All scripts require Python 3 and only its standard library.

- source_io.py: read-only reconstruction of 4,499 anchors from immutable original text and PO files; verifies originals, UUID alignment, glossary and standard hashes.
- assemble_draft.py: initial assembly from translations/batches JSONL. It preserves source strings and coherent grouping. `--partial` makes unfinished coverage explicit; it does not count those anchors as translated. Do not use it to overwrite post-assembly canonical edits.
- validate_paired.py: checks source identity, complete ordered object coverage, pair symmetry, structural metadata, notes, canonical hashes and `--final` signoff.
- test_validation.py: positive synthetic fixture plus deliberate corruption tests; synthetic English exists only in a temporary directory and is never publication content.
- checkpoint.py: explicit staged commit/push with remote-SHA verification.

The archived scripts under source/intake/scripts are historical evidence and are never executed in this workflow.
