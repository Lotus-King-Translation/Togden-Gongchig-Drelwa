#!/usr/bin/env python3
"""Initial draft assembly from reviewed batch records; never run over released edits."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path
from source_io import ROOT, sha, validate_intake

BOUNDARIES = [69, 969, 1215, 1685, 2319, 3196, 3907, 4414, 4487]
FORMATS = {'prose','verse','h1','h2','h3'}
NOTE_FIELDS = ['id','anchors','tibetan','category','problem','treatment','uncertainty','review_action']

def assemble(root=ROOT, partial=False):
    anchors = validate_intake(root)
    records = []
    for path in sorted((root/'translations/batches').glob('**/*.jsonl')):
        for line in path.read_text().splitlines():
            if line.strip():
                record = json.loads(line)
                record['batch_file'] = str(path.relative_to(root))
                records.append(record)
    records.sort(key=lambda r:r['start'])
    expanded, cursor = [], 1
    for row in records:
        if row['start'] < cursor or row['end'] < row['start'] or row['end'] > 4499:
            raise ValueError(f'Overlapping/invalid range: {row}')
        if row['start'] != cursor:
            if not partial:
                raise ValueError(f'Missing translation at {cursor}')
            expanded.extend(unprocessed(i) for i in range(cursor,row['start']))
        if row['format'] not in FORMATS:
            raise ValueError('Invalid format')
        if any(row['start'] <= b < row['end'] for b in BOUNDARIES):
            raise ValueError(f'Pair crosses section boundary: {row["start"]}')
        if not row['english'].strip():
            raise ValueError('Blank English')
        expanded.append(row)
        cursor = row['end']+1
    if cursor <= 4499:
        if not partial:
            raise ValueError(f'Missing translation at {cursor}')
        expanded.extend(unprocessed(i) for i in range(cursor,4500))
    source = ['---','schema: paired-text/2','text-id: TGD','edition: provisional-source-v0.1.0',
              'source-status: provisional','language: bo','---','']
    translation = ['---','schema: paired-text/2','text-id: TGD','source-edition: provisional-source-v0.1.0',
                   'translation-edition: annotated-working-draft-v0.1.0','language: en',
                   'status: working-draft','---','']
    pairs, notes, note_ids, coverage = [], [], set(), []
    for row in expanded:
        start,end = row['start'],row['end']
        pid = f'TGD-{start:06d}'
        ids = [r['anchor'] for r in anchors[start-1:end]]
        st = '\n'.join(r['tibetan'] for r in anchors[start-1:end])
        source.extend([f'<!-- pair: {pid} | source: {" ".join(ids)} | role: {row["role"]} | format: {row["format"]} -->',st,''])
        translation.extend([f'<!-- pair: {pid} -->',row['english'].strip(),''])
        for note in row.get('notes',[]):
            if any(k not in note for k in NOTE_FIELDS):
                raise ValueError(f'Incomplete note at {pid}: {note}')
            if note['id'] in note_ids:
                raise ValueError('Duplicate note ID: '+note['id'])
            if '[^'+note['id']+']' not in row['english']:
                raise ValueError(f'Unlinked note at {pid}: {note["id"]}')
            if not set(note['anchors']) <= set(ids):
                raise ValueError(f'Note anchors outside pair at {pid}')
            note_ids.add(note['id'])
            notes.append(dict(note,pair_id=pid))
        status = row.get('status','translated')
        pairs.append(dict(id=pid,source=ids,format=row['format'],role=row['role'],status=status,
                          batch_file=row.get('batch_file'),note_ids=[n['id'] for n in row.get('notes',[])]))
        coverage.extend(dict(anchor=i,pair_id=pid,status=status,
                             has_review_note=bool(row.get('notes'))) for i in ids)
    if notes:
        translation.extend(['<!-- translation-notes -->',''])
    for note in notes:
        fields = [f'Anchors: {", ".join(note["anchors"])}.',f'Exact Tibetan: {note["tibetan"]}',
                  f'Category: {note["category"]}.',f'Issue: {note["problem"]}',
                  f'Working treatment: {note["treatment"]}',f'Uncertainty: {note["uncertainty"]}',
                  f'Review action: {note["review_action"]}']
        translation.extend([f'[^'+note['id']+']: '+' '.join(str(x).replace('\n',' ') for x in fields),''])
    (root/'paired/source.md').write_text('\n'.join(source))
    (root/'paired/translation.md').write_text('\n'.join(translation))
    (root/'translations/notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
    (root/'translations/coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
    manifest=dict(schema='paired-text/2',source_edition='provisional-source-v0.1.0',
                  source_commit='8d7a583020ffc3dee6a4e56f6cecc35a18e09436',
                  pairs=pairs,source_sha256=sha(root/'paired/source.md'),
                  translation_sha256=sha(root/'paired/translation.md'),
                  notes_sha256=sha(root/'translations/notes.json'),
                  glossary_sha256=sha(root/'glossary/expanded_tibetan_english_glossary.csv'),
                  coverage_counts=dict(Counter(r['status'] for r in coverage)),
                  format_counts=dict(Counter(r['format'] for r in pairs)),
                  independent_qc=False)
    (root/'paired/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ['coverage_counts','format_counts']},indent=2))
    print(f'{len(pairs)} pairs; {len(notes)} notes')

def unprocessed(index):
    return dict(start=index,end=index,format='prose',role='main_text',
                english='[Not yet translated: U%05d.]'%index,notes=[],status='unprocessed')

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--partial',action='store_true')
    args=p.parse_args()
    assemble(partial=args.partial)
