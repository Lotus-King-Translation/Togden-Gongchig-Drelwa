# Provisional source and reference provenance

The project was generated from Lotus-King-Translation/tibetan-text-project-template at f6431c25c7c9fa852c404b8cd3e0e3cdeae1178f.

All legacy materials are pinned to [Gongchig-Drelwa commit 063eb57](https://github.com/Lotus-King-Translation/Gongchig-Drelwa/tree/063eb57bc01767fe1a33d8db50074ca936086f56), branch `transifex`, directory `wip` in the supplied URL. Hashes are in intake-manifest.json and ../editions/REGISTER.csv.

The governing electronic transcript is intake/root/001.txt. The duplicate 001_v2.txt is byte-identical; neither is an independent witness. Both have SHA256 0855bf2bdd2e375270d61b7c95fa8e741c1feff175d647ecf294f611ad37fe2c. The physical exemplar and transcription history have not been authenticated.

## Tokenization recovery

The archived generator inserts ASCII spaces between tokens, `་␣` inside affixed forms, and ` ` for original spaces. The inverse is, in order:

```python
text.replace(' ', '').replace('་␣', '').replace(' ', ' ')
```

The old exporters remove only `␣`, leaving false tshegs, e.g. གས་␣ར becomes གས་ར instead of གསར. They must not be used to construct this source.

Correct inversion matches the raw line after outer whitespace removal in 4,497/4,499 cases. At U00176, the raw transcript begins with ་ and the PO does not. At U01173, two spaces after རྡོ༽༽ become one in PO. The raw transcript is retained at both loci. There are also 13 outer-whitespace differences. No exact PO-to-original reconstruction is claimed.

`anchors.json` links every original line to its stable anchor and original Transifex UUID, stores raw_exact, a reading projection with only outer whitespace stripped, the decoded PO comparison, and the rough English reference. No Unicode normalization, spelling correction, punctuation repair, or doctrinal emendation is applied.

The x/×/✖ marks at 29 anchors, slash at U02253, and Tibetan labels རྡོ༽༽ / ལྷན༽༽ are in the underlying transcript. They are preserved; their interpretation is a translation/source note, not tokenizer cleanup.

## Human reference

The PO header credits Mikko Kotila (2024) and Tenzin Norgyal (2025), with Tenzin Norgyal as last translator. The English contains 44,002 whitespace-delimited words across 4,482 nonempty entries; 17 entries are blank. These credits describe the supplied artifact, not per-entry authorship or independent verification. The upstream README displays a CC BY-NC-SA license badge but supplies no fuller license instrument here; preserve its attribution and do not invent a different license.

## Scope

Front matter U00001–U00069; seven sections U00070–U00969, U00970–U01215, U01216–U01685, U01686–U02319, U02320–U03196, U03197–U03907, U03908–U04414; closing U04415–U04499, with compiler's colophon U04488–U04499.

No scan proofreading or independent-witness collation was performed. The source is provisional by explicit owner instruction.
