#!/usr/bin/env python3
"""Positive and deliberate-corruption tests; synthetic English is never a deliverable."""
import json
import shutil
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from assemble_draft import assemble
from source_io import ROOT,detokenize
from validate_paired import validate

class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.tmp.name)
        for name in ['source','glossary','guidelines']:
            shutil.copytree(ROOT/name,cls.root/name)
        for name in ['paired','translations/batches']:
            (cls.root/name).mkdir(parents=True,exist_ok=True)
        assemble(cls.root,partial=True)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    @contextmanager
    def mutate(self,path,change):
        p=self.root/path;original=p.read_bytes()
        p.write_text(change(p.read_text()))
        try:yield
        finally:p.write_bytes(original)

    def rejected(self,path,change):
        with self.mutate(path,change):
            with self.assertRaises((ValueError,KeyError)):validate(self.root)

    def test_positive_partial(self):
        result=validate(self.root)
        self.assertEqual(result['anchors'],4499)
        self.assertEqual(result['coverage'],{'unprocessed':4499})

    def test_detokenization_removes_inserted_tsheg(self):
        self.assertEqual(detokenize('བློ་ གས་␣ར་ དགའ་བ་␣འི་'), 'བློ་གསར་དགའ་བའི་')
        self.assertEqual(detokenize('། །'), '། །')

    def test_source_mutation(self):
        self.rejected('paired/source.md',lambda s:s.replace('ཐུབ་བསྟན་','ཐུབ་བསྟན་ནོ་',1))

    def test_missing_format(self):
        self.rejected('paired/source.md',lambda s:s.replace(' | format: prose','',1))

    def test_unsupported_format(self):
        self.rejected('paired/source.md',lambda s:s.replace('format: prose','format: heading',1))

    def test_duplicate_format(self):
        self.rejected('paired/source.md',lambda s:s.replace('format: prose','format: prose | format: verse',1))

    def test_missing_pair(self):
        self.rejected('paired/translation.md',lambda s:s.replace('<!-- pair: TGD-000002 -->','',1))

    def test_duplicate_pair(self):
        self.rejected('paired/translation.md',lambda s:s.replace('TGD-000002','TGD-000001',1))

    def test_order_mismatch(self):
        self.rejected('paired/translation.md',lambda s:s.replace('TGD-000001','SWAP',1).replace('TGD-000002','TGD-000001',1).replace('SWAP','TGD-000002',1))

    def test_unknown_source(self):
        self.rejected('paired/source.md',lambda s:s.replace('source: U00001','source: U99999',1))

    def test_duplicate_source_coverage(self):
        self.rejected('paired/source.md',lambda s:s.replace('source: U00002','source: U00001',1))

    def test_wrong_edition(self):
        self.rejected('paired/translation.md',lambda s:s.replace('source-edition: provisional-source-v0.1.0','source-edition: unset',1))

    def test_blank_english(self):
        self.rejected('paired/translation.md',lambda s:s.replace('[Not yet translated: U00001.]','',1))

    def test_unrecorded_english_change(self):
        self.rejected('paired/translation.md',lambda s:s.replace('[Not yet translated: U00001.]','An unrecorded change.',1))

    def test_undefined_note(self):
        self.rejected('paired/translation.md',lambda s:s.replace('[Not yet translated: U00001.]','Text.[^missing]',1))

    def test_archival_hash(self):
        self.rejected('source/intake/root/001.txt',lambda s:s+'\n')

    def test_source_reference_alignment_mutation(self):
        self.rejected('source/anchors.json',lambda s:s.replace('Summer Drum Sound','Unsupported replacement',1))

    def test_glossary_mutation(self):
        self.rejected('glossary/expanded_tibetan_english_glossary.csv',lambda s:s.replace('Ordinary mind','Mind',1))

    def test_final_rejects_unprocessed(self):
        with self.assertRaisesRegex(ValueError,'Unprocessed'):validate(self.root,final=True)

class FinalGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.tmp.name)
        for name in ['source','glossary','guidelines']:
            shutil.copytree(ROOT/name,cls.root/name)
        for name in ['paired','translations/batches']:
            (cls.root/name).mkdir(parents=True,exist_ok=True)
        anchors=json.loads((cls.root/'source/anchors.json').read_text())
        rows=[]
        for a in anchors:
            n=a['index'];notes=[];english='Synthetic structural test content.'
            if any(c in a['tibetan'] for c in 'x×✖'):
                nid='TEST-'+a['anchor'];english+='[^'+nid+']'
                notes=[dict(id=nid,anchors=[a['anchor']],tibetan=a['tibetan'],category='source reading',problem='Synthetic placeholder test.',treatment='Test only.',uncertainty='Not a translation.',review_action='Test only.')]
            rows.append(dict(start=n,end=n,format='prose',role='main_text',english=english,notes=notes))
        (cls.root/'translations/batches/fixture.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n')
        assemble(cls.root)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_unsigned_final_rejected_and_signed_final_accepted(self):
        self.assertEqual(validate(self.root)['anchors'],4499)
        with self.assertRaisesRegex(ValueError,'signoff'):validate(self.root,final=True)
        manifest=json.loads((self.root/'paired/manifest.json').read_text())
        signoff={k:manifest[k] for k in ['source_sha256','translation_sha256','notes_sha256']}
        signoff.update(release_kind='annotated-working-draft',human_certification=False,structural_validation=True,negative_tests=True)
        p=self.root/'translations/release-signoff.json';p.write_text(json.dumps(signoff))
        try:
            self.assertTrue(validate(self.root,final=True)['final_mode'])
            signoff['translation_sha256']='stale';p.write_text(json.dumps(signoff))
            with self.assertRaisesRegex(ValueError,'Stale'):validate(self.root,final=True)
        finally:p.unlink()

    def test_lost_required_note(self):
        p=self.root/'paired/translation.md';original=p.read_text()
        import re
        changed=re.sub(r'\[\^TEST-U[0-9]+\]','',original,count=1)
        p.write_text(changed)
        try:
            with self.assertRaisesRegex(ValueError,'note/reference'):validate(self.root)
        finally:p.write_text(original)

    def test_closing_material_loss(self):
        p=self.root/'paired/source.md';original=p.read_text()
        p.write_text(original[:original.index('<!-- pair: TGD-004499')])
        try:
            with self.assertRaises(ValueError):validate(self.root)
        finally:p.write_text(original)

if __name__=='__main__':unittest.main()
