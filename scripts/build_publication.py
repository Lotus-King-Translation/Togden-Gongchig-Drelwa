#!/usr/bin/env python3
"""Generate reading projections from canonical paired Markdown; never changes canonical files."""
import html
import hashlib
import json
from pathlib import Path
from source_io import ROOT,sha
from validate_paired import parse,validate


def render(root, counts):
    sf,srows,_=parse((root/'paired/source.md').read_text(),True)
    tf,trows,footer=parse((root/'paired/translation.md').read_text(),False)
    notes=json.loads((root/'translations/notes.json').read_text())
    md=['# Togden-Gongchig-Drelwa — bilingual working draft','',
        '> Generated from paired/source.md and paired/translation.md. The Tibetan is provisional; annotations identify readings and usages requiring review.','']
    articles=[]
    for sr,tr in zip(srows,trows):
        pid=sr['id'];fmt=sr['metadata']['format']
        shown_source=sr['body'].replace('\n','<br>\n') if fmt=='verse' else sr['body']
        shown_english=tr['body'].replace('\n','<br>\n') if fmt=='verse' else tr['body']
        md.extend([f'<!-- {pid} -->','',shown_source,'',shown_english,''])
        tag=fmt if fmt in {'h1','h2','h3'} else 'div'
        st=html.escape(sr['body']);en=html.escape(tr['body'])
        import re
        en=re.sub(r'\[\^([^\]]+)\]',lambda m:'<sup><a href="#'+m.group(1)+'">'+m.group(1)+'</a></sup>',en)
        articles.append(f'<article id="{pid}" class="{fmt}"><a class="id" href="#{pid}">{pid}</a><div class="columns"><{tag} lang="bo">{st}</{tag}><{tag} lang="en">{en}</{tag}></div></article>')
    if footer.strip():md.extend(['## Notes','',footer.strip(),''])
    note_html=[]
    for n in notes:
        pieces=[f'<li id="{html.escape(n["id"])}"><strong>{html.escape(n["id"])}</strong> — '+html.escape(', '.join(n['anchors']))]
        for label,key in [('Tibetan','tibetan'),('Issue','problem'),('Treatment','treatment'),('Uncertainty','uncertainty'),('Review','review_action')]:
            pieces.append(f'<p><b>{label}:</b> {html.escape(str(n[key]))}</p>')
        pieces.append('</li>');note_html.append(''.join(pieces))
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Togden-Gongchig-Drelwa</title><style>
body{max-width:1400px;margin:auto;padding:2rem;background:#fcfbf8;color:#20201e;font:18px/1.6 Georgia,serif}header{border-bottom:2px solid #8d452f;margin-bottom:2rem}h1{font-size:2rem}a{color:#8d452f}.id{font:12px/1.5 system-ui,sans-serif;color:#666}.columns{display:grid;grid-template-columns:1fr 1fr;gap:2rem}article{padding:1rem 0;border-bottom:1px solid #ddd}[lang=bo]{font-family:"Noto Serif Tibetan","Kailasa","Microsoft Himalaya",serif;font-size:22px;line-height:1.9}.verse [lang=bo],.verse [lang=en]{white-space:pre-wrap}sup{font:11px system-ui,sans-serif}#notes li{margin:1.5rem 0}#notes p{margin:.3rem 0}@media(max-width:800px){.columns{grid-template-columns:1fr;gap:.75rem}body{padding:1rem}}@media print{body{background:white;font-size:11pt}.id{font-size:8pt}.columns{gap:1rem}article{break-inside:avoid}}
</style><header><h1>Togden-Gongchig-Drelwa</h1><p>Bilingual annotated working draft · Provisional Tibetan source · Golden-edition phase skipped by owner instruction.</p><p>Generated from the canonical paired files. Source-linked uncertainties and provisional terminology remain for human review.</p></header>'''
    page+='\n'.join(articles)+'<section id="notes"><h2>Review notes</h2><ol>'+''.join(note_html)+'</ol></section></html>\n'
    outputs={'paired/bilingual.md':'\n'.join(md),'paired/bilingual.html':page}
    receipt={'generated_from':['paired/source.md','paired/translation.md','translations/notes.json'],
             'input_hashes':{p:sha(root/p) for p in ['paired/source.md','paired/translation.md','translations/notes.json']},
             'output_hashes':{p:hashlib.sha256(content.encode()).hexdigest() for p,content in outputs.items()},
             'counts':counts}
    outputs['paired/publication-manifest.json']=json.dumps(receipt,indent=2)+'\n'
    return outputs,receipt

def build(root=ROOT):
    outputs,receipt=render(root,validate(root))
    for path,content in outputs.items():(root/path).write_text(content)
    return receipt

if __name__=='__main__':print(json.dumps(build()['counts'],indent=2))
