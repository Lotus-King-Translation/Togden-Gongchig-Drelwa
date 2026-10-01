#!/usr/bin/env python3
"""Validate exact source coverage, pair structure, annotations and draft release gates."""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from source_io import ROOT, sha, validate_intake

PAIR = re.compile(r'<!-- pair: ([^|>]+)(.*?) -->')
FORMATS = {'prose','verse','h1','h2','h3'}
REQUIRED_BOUNDARIES = [69,969,1215,1685,2319,3196,3907,4414,4487]

def front_matter(text):
    if not text.startswith('---\n'):
        raise ValueError('Missing front matter')
    end=text.find('\n---\n',4)
    if end<0:
        raise ValueError('Unterminated front matter')
    values={}
    for line in text[4:end].splitlines():
        key,sep,value=line.partition(':')
        if not sep or key in values:
            raise ValueError('Invalid/duplicate front matter')
        values[key.strip()]=value.strip()
    return values,end+5

def parse(text, source_side):
    fm,offset=front_matter(text)
    content,sep,footer=text[offset:].partition('<!-- translation-notes -->')
    if source_side and sep:
        raise ValueError('Translation notes on source side')
    matches=list(PAIR.finditer(content))
    if not matches or content[:matches[0].start()].strip():
        raise ValueError('No pairs or unpaired leading content')
    rows=[];seen=set()
    for i,m in enumerate(matches):
        pid=m.group(1).strip()
        if not re.fullmatch('TGD-[0-9]{6}',pid) or pid in seen:
            raise ValueError('Invalid/duplicate pair ID: '+pid)
        seen.add(pid);md={}
        for item in m.group(2).split('|'):
            if not item.strip():continue
            key,colon,value=item.strip().partition(':')
            if not colon or key.strip() in md:
                raise ValueError('Invalid/duplicate pair metadata')
            md[key.strip()]=value.strip()
        if source_side:
            if set(md)!={'source','role','format'} or md['format'] not in FORMATS:
                raise ValueError('Invalid source metadata: '+pid)
        elif md:
            raise ValueError('English must inherit source metadata: '+pid)
        body=content[m.end():matches[i+1].start() if i+1<len(matches) else len(content)].strip()
        if not body or '<!-- pair:' in body:
            raise ValueError('Empty/malformed pair: '+pid)
        rows.append(dict(id=pid,metadata=md,body=body))
    return fm,rows,footer

def validate(root=ROOT, final=False):
    anchors=validate_intake(root)
    by_id={r['anchor']:r for r in anchors}
    sp=root/'paired/source.md';tp=root/'paired/translation.md'
    sf,srows,sfooter=parse(sp.read_text(),True)
    tf,trows,tfooter=parse(tp.read_text(),False)
    for fm in (sf,tf):
        if fm.get('schema')!='paired-text/2' or fm.get('text-id')!='TGD':
            raise ValueError('Wrong schema/text identity')
    if sf.get('edition')!='provisional-source-v0.1.0' or sf.get('source-status')!='provisional':
        raise ValueError('Wrong source edition/status')
    if tf.get('source-edition')!=sf['edition'] or tf.get('translation-edition')!='annotated-working-draft-v0.1.0':
        raise ValueError('Wrong translation/source edition')
    if sf.get('language')!='bo' or tf.get('language')!='en':raise ValueError('Wrong languages')
    if [r['id'] for r in srows]!=[r['id'] for r in trows]:
        raise ValueError('Pair identity/order mismatch')
    manifest=json.loads((root/'paired/manifest.json').read_text())
    if len(manifest['pairs'])!=len(srows):raise ValueError('Manifest pair count mismatch')
    coverage=[]
    for sr,tr,expected in zip(srows,trows,manifest['pairs']):
        md=sr['metadata'];ids=md['source'].split()
        if not ids or any(i not in by_id for i in ids):raise ValueError('Unknown/empty source-object reference')
        numbers=[by_id[i]['index'] for i in ids]
        if numbers!=list(range(numbers[0],numbers[-1]+1)):raise ValueError('Source objects not contiguous')
        if any(numbers[0]<=b<numbers[-1] for b in REQUIRED_BOUNDARIES):raise ValueError('Pair crosses chapter/closing boundary')
        if sr['id']!=f'TGD-{numbers[0]:06}':raise ValueError('Pair identity not tied to initial anchor')
        if sr['body']!='\n'.join(by_id[i]['tibetan'] for i in ids):raise ValueError('Source text differs from fixed transcript')
        for key,value in [('id',sr['id']),('source',ids),('format',md['format']),('role',md['role'])]:
            if expected[key]!=value:raise ValueError('Manifest/source structural mismatch: '+sr['id'])
        if any(c in sr['body'] for c in ['␣',' ']):raise ValueError('Tokenizer markup remains')
        if expected['status']=='translated' and re.search('[x×✖]',sr['body']) and not expected['note_ids']:
            raise ValueError('Source placeholder lacks review note: '+sr['id'])
        if final and (expected['status']!='translated' or 'Not yet translated:' in tr['body']):
            raise ValueError('Unprocessed source in final draft')
        coverage.extend(dict(anchor=i,pair_id=sr['id'],status=expected['status'],
                             has_review_note=bool(expected['note_ids'])) for i in ids)
    if [r['anchor'] for r in coverage]!=[r['anchor'] for r in anchors]:
        raise ValueError('Omitted, duplicated or reordered source objects')
    if coverage!=json.loads((root/'translations/coverage.json').read_text()):raise ValueError('Coverage record differs')
    notes=json.loads((root/'translations/notes.json').read_text())
    note_map={n['id']:n for n in notes}
    if len(note_map)!=len(notes):raise ValueError('Duplicate note ID')
    definitions=re.findall(r'^\[\^([^\]]+)\]:',tfooter,re.M)
    if sorted(definitions)!=sorted(note_map):raise ValueError('Footnote definitions differ')
    all_refs=set()
    for tr,expected in zip(trows,manifest['pairs']):
        refs=set(re.findall(r'\[\^([^\]]+)\]',tr['body']))
        if refs!=set(expected['note_ids']):raise ValueError('Required note/reference lost: '+tr['id'])
        all_refs.update(refs)
        for nid in refs:
            if nid not in note_map:raise ValueError('Undefined note: '+nid)
            note=note_map[nid]
            if note['pair_id']!=tr['id'] or not set(note['anchors'])<=set(expected['source']):
                raise ValueError('Incorrect note source allocation')
    if all_refs!=set(note_map):raise ValueError('Orphan note')
    for path,key in [(sp,'source_sha256'),(tp,'translation_sha256'),(root/'translations/notes.json','notes_sha256')]:
        if sha(path)!=manifest[key]:raise ValueError('Unrecorded canonical mutation: '+str(path.name))
    if final:
        signoff_path=root/'translations/release-signoff.json'
        if not signoff_path.exists():raise ValueError('Final mode requires explicit draft signoff')
        signoff=json.loads(signoff_path.read_text())
        if signoff.get('release_kind')!='annotated-working-draft' or signoff.get('human_certification') is not False:
            raise ValueError('Missing/invalid draft signoff scope')
        for key in ['source_sha256','translation_sha256','notes_sha256']:
            if signoff.get(key)!=manifest[key]:raise ValueError('Stale signoff')
        if not signoff.get('structural_validation') or not signoff.get('negative_tests'):
            raise ValueError('Incomplete signoff')
    result=dict(pairs=len(srows),anchors=len(coverage),notes=len(notes),
                coverage=dict(Counter(r['status'] for r in coverage)),
                formats=dict(Counter(r['metadata']['format'] for r in srows)),
                source_edition=sf['edition'],translation_edition=tf['translation-edition'],
                independent_semantic_qc=False,final_mode=final)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--final',action='store_true')
    args=parser.parse_args()
    try:
        print(json.dumps(validate(final=args.final),indent=2))
    except (OSError,ValueError,KeyError) as exc:
        print('PAIRED VALIDATION FAILED: '+str(exc),file=sys.stderr)
        sys.exit(1)
