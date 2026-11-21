# de-ai

Rewrite a document so it stops reading like machine translation or generated text.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

Takes `.docx`, `.md` or `.txt`, Chinese or English, and returns the same format. The prose is produced by machine translation across language families plus regex rules, never by a language model.

## Features

- Four translation chains through two intermediate languages, so the original word order does not survive
- Deterministic cleanup for the leftovers translation leaves: `, -ing` tails, modal passives, stock connectives, uniform sentence length, repeated sentence openings
- Several candidates per block, ranked by how far they moved without losing a number, a citation or an identifier
- Engine failover that adapts to whichever translation endpoints your network can reach
- Per-project rule probabilities and term tables in plain JSON
- Reads and writes Word, Markdown and plain text; no external program needed except for PDF export

## Requirements

Python 3.9 or newer.

```bash
pip install -r scripts/requirements.txt
```

English documents also need `torch`, `transformers` and a cached GPT-2, about 3GB together.

> [!TIP]
> Where the Hugging Face Hub is unreachable, fetch the model once through a mirror. It is cached afterwards and loads offline.
>
> ```bash
> HF_ENDPOINT=https://hf-mirror.com python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('gpt2')"
> ```

## Quick start

```bash
# Chinese in, Chinese out
python scripts/pipeline.py --input in.md --out out.md --src-lang zh --dst-lang zh

# English in, English out
python scripts/pipeline.py --input in.docx --out out.docx --src-lang en --dst-lang en

# Chinese in, English out
python scripts/pipeline.py --input in.txt --out out.txt --src-lang zh --dst-lang en
```

List what it would touch before touching it:

```bash
python scripts/pipeline.py --input in.docx --out out.docx --src-lang auto --dst-lang same --dry-run
```

To use it as an agent skill, drop this directory into your skills path and copy the prompt template from `pi/prompts/de-ai.md` in this repository alongside it, then invoke it explicitly. It is excluded from automatic model selection on purpose.

## How it works

Four fixed jumps, each through two intermediate languages, ending back in the source language:

```
source --[iciba]-->   German   --[qq]--> French  --[youdao]--> source language
source --[qq]-->      Japanese --[iciba]--> German --[youdao]--> source language
source --[iciba]-->   Russian  --[qq]--> German  --[iciba]-->  source language
source --[reverso]--> German   --[qq]--> bridge  --[iciba]-->  source language
```

The intermediate language does the work, not the engine. Chinese or English translated straight to English keeps clause order and modifier position nearly intact; routing through Japanese or Russian rearranges them.

After translation, each candidate goes through the cleanup rules, then a validation pass. A candidate is dropped if it loses a number, a citation or a protected identifier, breaks a term count, contains a forbidden word, or changes length outside a band: 0.70–1.45 words for English, 0.75–1.40 characters for Chinese, or 0.30–1.05 English words per Chinese character across languages. That band catches translation endpoints silently dropping the tail of a long paragraph.

The surviving candidate ranked furthest from the source wins the block.

## Choosing translation engines

Translation runs through the free endpoints wrapped by [`translators`](https://github.com/UlionTse/translators), and which answer depends on where you run it. Inside mainland China usually `iciba`, `qqTranSmart`, `youdao` and `baidu`; elsewhere usually `reverso`, `bing`, `google` and `yandex`.

Each hop carries a tier1 list, the engines the original experiment validated, and a tier2 fallback list. Every hop is probed once before the run and the first reachable engine wins:

```
chain2 zh->ja      uses qqTranSmart  [tier1]
chain3 de->en      uses baidu        [tier2]  <- downgraded
```

> [!NOTE]
> A `[tier2]` line means the validated engine was unreachable, and the output may read worse. The last hop is restricted to `youdao` and `iciba` because reverso as a final hop leaves European academic phrasing behind.

To reorder or substitute engines, override `chain_templates` in a config file. Each hop is `[language, [tier1...], [tier2...]]`, and `null` means the document's own target language:

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

Every rule fires per hit, at a probability you set. Start from `projects/rewrite.example.json` and pass your copy with `--config`:

```json
{
  "seed": 42,
  "max_per_word": 2,
  "ordinal_series": "auto",
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

`0` turns a rule off, and anything under `0.3` rarely fires. `seed` fixes the draw so a rerun reproduces the same document. `max_per_word` caps how often one connective may be swapped, and `ordinal_series` pins the numbering style so `First` never meets `Secondly`.

The English rules cover `, -ing` tails, the nine fixed modal passives, connective swaps, long-sentence splits and runs of identical sentence openings. The Chinese rules cover stock frames (`随着…的发展`, `综上所述`), light verbs (`进行了分析` → `分析了`), passives, high-frequency modifiers, trailing connectives (`，从而`, `，使得`), long sentences and repeated openings.

Two settings go beyond probabilities. `forbidden` lists words that invalidate any candidate containing them, which is how you block a mistranslation you have already seen. `selection.min_divergence` sets how far a candidate must move, measured as 3-gram overlap with the source, before it counts as a real rewrite.

Term restoration and citation repair ignore all of this and always run in full.

## Terminology

Identifiers are protected without configuration. The script extracts camel-case names, all-caps acronyms, `ns:Action` identifiers, subscript keys, version numbers and repeated product names, then discards any candidate that loses one. This check runs when source and target language match, since identifiers are legitimately translated across languages.

Replacement is opt-in, because it is a global regex and a wrong table damages the document. A table is a list of `[regex, replacement]` pairs:

```json
[
  ["\\bkms:\\s*Decrypt\\b", "kms:Decrypt"],
  ["\\breplay memory\\b", "replay cache"]
]
```

```bash
python scripts/pipeline.py --input in.docx --out out.docx --terms projects/terms.example.json
```

> [!TIP]
> Start from `projects/terms.example.json`. A validated Kerberos and AWS table lives in `projects/terms.kerberos-aws.json`, which shows what a real table looks like for a technical paper.

Run without `--terms` and nothing is replaced; the run prints a reminder.

## CLI

| Flag | Meaning |
|---|---|
| `--input`, `--docx` | Input file: `.docx`, `.md`, `.markdown`, `.txt` |
| `--out`, `--out-docx` | Output file; the extension decides the format |
| `--src-lang auto\|en\|zh` | Default `auto`, decided per block from a CJK ratio |
| `--dst-lang same\|en\|zh` | `same` keeps the source language |
| `--level light\|standard\|deep` | 1, 3 or 4 chains; default `standard` |
| `--config <json>` | Probabilities, seed and chain templates |
| `--terms <json>` | Term table |
| `--seed N` | Fix the draw to reproduce a run |
| `--dry-run` | Print the plan without rewriting |
| `--skip-preflight` | Skip engine probing |
| `--out-pdf <pdf>` | `.docx` input only; LibreOffice first, Word as a Windows fallback |

Exit codes: `0` all blocks replaced, `1` nothing to rewrite, `2` some blocks kept their original text or PDF export failed, `3` no usable chain, which means `chain_templates` needs editing.

## Output

```
out.docx                    rewritten document, metadata scrubbed
out.docx.work/report.md     per-block table, unrewritten reasons, skip list
out.docx.work/result.json   every candidate, its scores, validation problems, final text
out.docx.work/units/        raw translation per block per chain, reused on rerun
```

Each block ends in one of six states. Four are written back (`replaced`, `replaced-low-sim`, `replaced-min-change`, `replaced-worse`) and two keep the original text (`all-candidates-failed-validation`, `all-chains-failed`). All six appear in the report.

The score in `report.md` ranks candidates within a block and nothing else. It is not comparable between documents, and it is not a detector reading.

## Supported formats

| Extension | Read | Write | Skipped |
|---|---|---|---|
| `.docx` | python-docx | paragraph styles kept, runs merged | headings, captions, references, monospace paragraphs, short labels |
| `.md` `.markdown` | plain text, blocks split on blank lines | written back as-is | headings, code fences, tables, block quotes, link definitions, indented code |
| `.txt` | plain text, blocks split on blank lines | written back as-is | very short blocks |

Markdown fences are tracked line by line, so anything inside one, tables included, is left alone. Legacy `.doc` is not supported; re-save it as `.docx` first.

## Project layout

```
pipeline.py         entry point: collect blocks, run chains, validate, pick, write back
docio.py            .docx / .md / .txt behind one interface, plus PDF export
chains.py           chain templates, per-hop engine probing and failover
rules.py            the English and Chinese rewrite rules
score.py            candidate scoring and the validation checks
config_default.json default probabilities
requirements.txt    Python dependencies

references/chains.md    why the thresholds and chains look like this
projects/               example config and term tables to copy
```

## Notes

> [!WARNING]
> Document text is sent to the third-party translation endpoints listed above. Do not point this at confidential material.

> [!NOTE]
> A `.docx` write merges the runs inside a paragraph, so mid-paragraph bold, italics and superscript citation numbers are lost. Check formatting after export. Markdown and plain text are unaffected.

> [!CAUTION]
> A full-document rewrite also touches blocks that were fine, and can leave them worse. Read the blocks the report flags as barely changed or scored worse.

The block list is finite, each hop gets three attempts, and the chain count is fixed by `--level`. PDF export times out at 600 seconds for LibreOffice and 300 for Word. When an agent drives the tool it runs at most two rounds; the same limit applies by hand, since a third pass over the same block rarely changes anything.

PDF export uses LibreOffice, or Microsoft Word on Windows. Everything else runs without an external program.
