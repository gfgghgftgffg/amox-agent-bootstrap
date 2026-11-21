# de-ai

Rewrites a document so it stops reading like machine translation or generated text. Takes `.docx`, `.md` or `.txt`, Chinese or English, and returns the same format.

No language model writes the prose. The text is pushed through machine translation across language families to break its original word order, then through regex rules that shave what translation leaves behind: trailing `, ensuring` clauses, stacked modal passives, stock connectives, sentences that all run the same length. Each block produces several candidates, and the script keeps the one that moved furthest from the source without losing a number, a citation or an identifier.

## Install

```bash
pip install -r scripts/requirements.txt
```

English documents also need `torch`, `transformers` and a cached GPT-2, about 3GB together. Where the Hugging Face Hub is unreachable, fetch it once through a mirror:

```bash
HF_ENDPOINT=https://hf-mirror.com python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('gpt2')"
```

After that it loads offline.

## Run

```bash
# Chinese in, Chinese out
python scripts/pipeline.py --input in.md --out out.md --src-lang zh --dst-lang zh

# English in, English out
python scripts/pipeline.py --input in.docx --out out.docx --src-lang en --dst-lang en

# Chinese in, English out
python scripts/pipeline.py --input in.txt --out out.txt --src-lang zh --dst-lang en
```

A dry run lists the blocks it would touch and the ones it would skip:

```bash
python scripts/pipeline.py --input in.docx --out out.docx --src-lang auto --dst-lang same --dry-run
```

As an agent skill, drop the directory into your skills path next to the prompt template and call it explicitly; it is excluded from automatic model selection on purpose.

## The chains

Four fixed jumps through two intermediate languages, ending back in the source language:

```
source --[iciba]-->   German   --[qq]--> French  --[youdao]--> source language
source --[qq]-->      Japanese --[iciba]--> German --[youdao]--> source language
source --[iciba]-->   Russian  --[qq]--> German  --[iciba]-->  source language
source --[reverso]--> German   --[qq]--> bridge  --[iciba]-->  source language
```

The intermediate language matters more than the engine. Chinese or English translated straight to English keeps clause order and modifier position almost intact; passing through Japanese or Russian rearranges them.

The last hop is restricted to `youdao` and `iciba`. Reverso as a final hop keeps European academic phrasing, so it only appears in the fallback pool.

## Picking engines

Translation runs through the free endpoints that [`translators`](https://github.com/UlionTse/translators) wraps, and which ones answer depends on where you are. Inside mainland China usually `iciba`, `qqTranSmart`, `youdao` and `baidu`; elsewhere usually `reverso`, `bing`, `google` and `yandex`.

Each hop carries a tier1 list (the engines the original experiment used) and a tier2 list (everything else). Before a run, every hop is probed once and the first reachable engine wins; a hop only drops to tier2 when tier1 is unreachable, and the run prints which happened:

```
chain2 zh->ja      uses qqTranSmart  [tier1]
chain3 de->en      uses baidu        [tier2]  <- downgraded
```

A `[tier2]` means the validated engine was down, and the output may be worse. To reorder or substitute engines, override `chain_templates` in a config file. Each hop is `[language, [tier1...], [tier2...]]`, and `null` means the document's own target language:

```json
{
  "chain_templates": [
    [["de", ["reverso"], ["bing", "google"]],
     ["fr", ["qqTranSmart"], ["bing"]],
     [null, ["iciba"], ["youdao", "reverso"]]]
  ]
}
```

## Tuning the rewrite

Every rule fires per hit, at a probability you set. Copy `projects/rewrite.example.json`, edit, and pass it with `--config`:

```json
{
  "seed": 42,
  "en": {
    "connector_swap": 1.0,
    "gerund_tail": 0.85,
    "modal_passive": 0.7,
    "split_long": 0.8,
    "starter_dedup": 0.9
  },
  "zh": {
    "frame_delete": 0.9,
    "connector_swap": 0.8,
    "tail_swap": 0.8,
    "verbify": 0.7,
    "passive_rewrite": 0.7,
    "highfreq_trim": 0.6,
    "split_long": 0.8,
    "redundant_trim": 0.9,
    "starter_dedup": 0.9
  },
  "zh_highfreq_words": ["进一步", "显著", "充分", "全面", "极大", "深入", "有效", "关键", "核心"],
  "forbidden": [],
  "selection": { "min_sim": { "en": 0.99, "zh": 0.75 }, "min_divergence": 0.10 }
}
```

`0` turns a rule off, and anything under `0.3` rarely fires. `seed` fixes the draw so a rerun reproduces the same document. `max_per_word` caps how often one connective may be swapped, and `ordinal_series` pins the numbering style so `First` never meets `Secondly`. The English rules cover `, -ing` tails, the nine fixed modal passives, connective swaps, long-sentence splits and runs of identical sentence openings. The Chinese rules cover stock frames like `随着…的发展` and `综上所述`, light verbs (`进行了分析` → `分析了`), passives, high-frequency modifiers, trailing connectives (`，从而`, `，使得`), long sentences and repeated openings.

Two settings are worth knowing beyond the probabilities. `forbidden` lists words that invalidate any candidate containing them, which is how you block a mistranslation you have already seen. `selection.min_divergence` is how far a candidate must move, measured as 3-gram overlap with the source, before it counts as a real rewrite.

Term restoration and citation repair ignore all of this; they always run in full.

## Terms

Identifiers are protected without any configuration. The script pulls camel-case names, all-caps acronyms, `ns:Action` identifiers, subscript keys, version numbers and repeated product names out of the document, and discards any candidate that loses one. This check runs when source and target language match, since identifiers are legitimately translated across languages.

Replacement is opt-in because it is a global regex, and a wrong table damages the document. A table is a list of `[regex, replacement]` pairs:

```json
[
  ["\\bkms:\\s*Decrypt\\b", "kms:Decrypt"],
  ["\\breplay memory\\b", "replay cache"]
]
```

```bash
python scripts/pipeline.py --input in.docx --out out.docx --terms projects/terms.example.json
```

Start from `projects/terms.example.json`. A validated Kerberos and AWS table lives in `projects/terms.kerberos-aws.json`. Run without `--terms` and nothing is replaced; the run says so.

## Output

```
out.docx                    rewritten document, metadata scrubbed
out.docx.work/report.md     per-block table, unrewritten reasons, skip list
out.docx.work/result.json   every candidate, its scores, validation problems, final text
out.docx.work/units/        raw translation per block per chain, reused on rerun
```

A candidate is discarded before ranking if it loses a number, a citation or a protected identifier, breaks a term count, contains a forbidden word, or changes length outside a band: 0.70–1.45 words for English, 0.75–1.40 characters for Chinese, or 0.30–1.05 English words per Chinese character across languages. That length band is there because free endpoints sometimes drop the tail of a long paragraph while leaving numbers and citations intact; length is the only signal left when that happens.

The score in the report ranks candidates within one block and nothing else. It is not comparable between documents, and it is not a detector reading.

## Formats

| Extension | Read | Write | Skipped |
|---|---|---|---|
| `.docx` | python-docx | paragraph styles kept, runs merged | headings, captions, references, monospace paragraphs, short labels |
| `.md` `.markdown` | plain text, blocks split on blank lines | written back as-is | headings, code fences, tables, block quotes, link definitions, indented code |
| `.txt` | plain text, blocks split on blank lines | written back as-is | very short blocks |

Markdown fences are tracked line by line, so anything inside one, tables included, is left alone. Legacy `.doc` is not supported; re-save it as `.docx` first.

## When it stops

The block list is finite, each hop gets three attempts, the chain count is fixed by `--level` at 1, 3 or 4, and there are no `while` loops in the code. PDF export times out at 600 seconds for LibreOffice and 300 for Word.

Every block ends in one of six states. Four are written back (`replaced`, `replaced-low-sim`, `replaced-min-change`, `replaced-worse`) and two keep the original text (`all-candidates-failed-validation`, `all-chains-failed`). All six appear in the report.

Exit codes: `0` all blocks replaced, `1` nothing to rewrite, `2` some blocks kept or PDF export failed, `3` no usable chain, which means `chain_templates` needs editing.

When an agent drives this, it runs at most two rounds: `standard` first, then `deep` or a new seed on the blocks that failed. If you drive it, the same limit applies; a third pass over the same block rarely changes anything.

## What to know before running it

Document text goes to the translation endpoints listed above. Do not point this at confidential material.

A `.docx` write merges the runs inside a paragraph, so mid-paragraph bold, italics and superscript citation numbers are lost. Check the formatting after export. Markdown and plain text are unaffected.

A full-document rewrite also touches blocks that were fine, and can leave them worse. The report says which blocks barely moved or scored worse than the original; read them.

PDF export uses LibreOffice, or Microsoft Word on Windows. Everything else needs no external program.

## License

MIT
