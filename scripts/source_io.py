"""Read immutable legacy evidence; no third-party dependency or normalization."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_po(path):
    rows, row, key = [], {}, None
    for line in path.read_text(encoding='utf-8').splitlines() + ['']:
        if not line:
            if row.get('msgctxt'):
                rows.append(row)
            row, key = {}, None
        elif line.startswith(('msgctxt ', 'msgid ', 'msgstr ')):
            key, value = line.split(' ', 1)
            row[key] = ast.literal_eval(value)
        elif line.startswith('"') and key:
            row[key] += ast.literal_eval(line)
        elif not line.startswith('#'):
            raise ValueError('Unsupported PO syntax: ' + line)
    return rows

def detokenize(text):
    # U+0F0B preceding U+2423 was inserted by the legacy generator.
    return text.replace(' ', '').replace('་␣', '').replace(' ', ' ')

def reconstruct(root=ROOT):
    intake = root / 'source/intake'
    en = read_po(intake / 'wip/en/001.po')
    bo = read_po(intake / 'wip/bo/001.po')
    raw = (intake / 'root/001.txt').read_text(encoding='utf-8').splitlines()
    if not len(raw) == len(en) == len(bo) == 4499:
        raise ValueError('Legacy source/reference count differs')
    if len(set(r['msgctxt'] for r in en)) != len(en):
        raise ValueError('Duplicate legacy UUID')
    rows = []
    for n, (a, b, line) in enumerate(zip(en, bo, raw), 1):
        if (a['msgctxt'], a['msgid']) != (b['msgctxt'], b['msgid']):
            raise ValueError(f'PO alignment differs at U{n:05}')
        rows.append(dict(anchor=f'U{n:05}', index=n, context=a['msgctxt'],
                         tibetan=line.strip(), decoded=detokenize(a['msgid']),
                         reference=a['msgstr'], bo_reference=b['msgstr'],
                         raw_line=n, raw_exact=line))
    return rows

def validate_intake(root=ROOT):
    manifest = json.loads((root/'source/intake-manifest.json').read_text())
    for path, digest in manifest['files'].items():
        if sha(root/path) != digest:
            raise ValueError('Archival hash mismatch: ' + path)
    for path, key in [('glossary/expanded_tibetan_english_glossary.csv','glossary_sha256'),
                      ('guidelines/tibetan_translation_standard_v2.md','guideline_sha256')]:
        if sha(root/path) != manifest[key]:
            raise ValueError('Governing policy hash mismatch: ' + path)
    expected = reconstruct(root)
    stored = json.loads((root/'source/anchors.json').read_text())
    if expected != stored:
        raise ValueError('Anchored source/reference differs from archival reconstruction')
    residual = [r['anchor'] for r in expected if r['tibetan'] != r['decoded']]
    if residual != ['U00176', 'U01173']:
        raise ValueError('Unexpected detokenization difference')
    return stored

if __name__ == '__main__':
    rows = validate_intake()
    print(f'INTAKE VALID: {len(rows)} anchors, exact archival hashes and PO UUID alignment')
    print('PO/raw residual differences preserved: U00176 U01173')
