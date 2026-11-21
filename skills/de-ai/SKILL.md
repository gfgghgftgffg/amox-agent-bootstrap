---
name: de-ai
description: "Rewrite a document so it reads less like machine translation or generated text. Handles .docx, .md and .txt, Chinese or English, output in either language. Use when asked to lower AI-detection scores, remove machine-translation tone, or rewrite text that reads as generated. Rewriting runs through machine translation and regex rules; no model writes the prose."
disable-model-invocation: true
license: MIT
metadata:
  version: "4.1.0"
---

# De-AI Pipeline

Rewrites a document by pushing it through machine translation across language families, which breaks the original word order, then through regex rules that shave the leftovers: trailing `, ensuring` clauses, modal passives, stock connectives, uniform sentence length. Every change comes from these scripts. Text you write yourself carries a language-model sampling fingerprint, which is the thing this pipeline exists to remove, so the division of labour is: the scripts produce the prose, you run them, read the artifacts and report.

## Environment

Use the current environment's `python`. Dependencies are in `scripts/requirements.txt`; install what is missing rather than substituting an implementation.

```bash
PY=python
S="<skill-dir>/scripts/pipeline.py"
```

## Steps

### 1. Confirm the input

Accepts `.docx`, `.md`, `.markdown`, `.txt`. If the user pasted text into the chat, write it to `.md` or `.txt` first. Legacy `.doc` needs a re-save as `.docx`.

Ask one question: Chinese output or English output. A Chinese source defaults to Chinese, an English source to English.

### 2. Dry run

```bash
"$PY" "$S" --input "<input>" --out "<output>" --src-lang auto --dst-lang same --dry-run
```

This probes engine availability and writes `<output>.work/plan.json`. Check the target count, look for body prose in the skip list, and confirm the language guess; `auto` decides from a CJK ratio, so force `--src-lang` on mixed documents. If fewer than two chains survive the probe, fix that before continuing.

### 3. Real run

```bash
"$PY" "$S" --input "<input>" --out "<output>" --src-lang auto --dst-lang same --level standard
```

`--level` sets the chain count: `light` 1, `standard` 3, `deep` 4. Start with `standard`.

### 4. Read the artifacts

`<output>.work/report.md` first, then `<output>.work/result.json` for detail.

| Status | Meaning | Action |
|---|---|---|
| `replaced` | Normal replacement | None |
| `replaced-low-sim` | Replaced, but far from the source; possible drift | Show `orig` and `final` side by side |
| `replaced-min-change` | No chain moved this block | Rerun with `deep`; if it persists, say the block cannot be improved mechanically |
| `replaced-worse(+Δ)` | Written back, but the ranking score rose because every candidate was worse | Give both versions and let the user choose |
| `all-candidates-failed-validation` | Candidates lost numbers, citations or terms, or the translation was truncated | Read `candidates[].validation`: `length anomaly` means truncation, `term drift` means terminology moved, `numbers missing` means a figure was dropped |
| `all-chains-failed` | Every chain errored | Read `detail`; usually network or rate limiting |

### 5. One rerun at most

Rerun once, only for `replaced-min-change`, `replaced-worse`, `all-candidates-failed-validation` and `all-chains-failed` blocks, with `--level deep` or a new `--seed`. Stop after the second round whatever happens.

`<output>.work/units/` caches translations, so a rerun with the same arguments only fills in failed or unfinished chains.

### 6. Report

Give four things: how many blocks were processed, replaced, skipped and failed; a per-block table with status, chain, before and after scores, and 3-gram overlap; the blocks that need a human and why; and the note that `new_score` ranks candidates within a block rather than measuring detection.

That score is not a detector reading, and no pass over a document proves anything about how a detector will rate it. The only evidence is the report the user gets after submitting. Say that once, plainly, and do not repeat it through the conversation.

## Flags

| Flag | Meaning |
|---|---|
| `--input` / `--docx` | Input file: `.docx`, `.md`, `.markdown`, `.txt` |
| `--out` / `--out-docx` | Output file; the extension decides the format |
| `--src-lang auto\|en\|zh` | Default `auto`, decided per block from a CJK ratio |
| `--dst-lang same\|en\|zh` | `same` keeps the source language |
| `--level light\|standard\|deep` | 1, 3 or 4 chains |
| `--terms <json>` | Term table, `[[regex, replacement], ...]` |
| `--config <json>` | Probabilities, seed and chain templates; start from `projects/rewrite.example.json` |
| `--seed N` | Fix the draw to reproduce a run |
| `--skip-preflight` | Skip engine probing |
| `--out-pdf <pdf>` | `.docx` input only; LibreOffice first, Word as a Windows fallback |

## Chains

Four fixed shapes. Each hop offers a tier1 engine list, the set the original experiment validated, and a tier2 fallback list.

| Chain | Hop 1 | Hop 2 | Hop 3, final |
|---|---|---|---|
| 1 | DE · `iciba` | FR · `qqTranSmart` | source language · `youdao` |
| 2 | JA · `qqTranSmart` | DE · `iciba` | source language · `youdao` |
| 3 | RU · `iciba` | DE · `qqTranSmart` | source language · `iciba` |
| 4 | DE · `reverso` | bridge language · `qqTranSmart` | source language · `iciba` |

Mid hops use `iciba`, `qqTranSmart` or `reverso` to break the source word order. The final hop uses only `youdao` or `iciba`; reverso as a last hop leaves European academic phrasing, so it appears only in the tier2 final-hop pool.

The tier2 pool: `baidu`, `bing`, `google`, `youdao`, `iciba`, `reverso`, `tencent`, `sogou`, `alibaba`, `caiyun`, `yandex`, `deepl`, `papago`.

Each hop prints the engine and tier it landed on:

```
chain2 zh->ja      uses qqTranSmart  [tier1]
chain3 de->en      uses baidu        [tier2]  <- downgraded
```

A `[tier2]` means the validated engine was unreachable and the output may be worse. Mention that when reporting.

The bridge language is the first one that is neither source nor target: English to English bridges through Chinese, Chinese to Chinese through English, Chinese to English through Japanese.

Override `chain_templates` to reorder or substitute engines. Each hop is `[language, [tier1...], [tier2...]]`; the two-element form treats every engine as tier1, and `null` means the document's own target language.

## Formats

| Format | Read | Write | Skipped |
|---|---|---|---|
| `.docx` | python-docx | paragraph styles kept, runs merged | heading styles, captions, references, monospace paragraphs, short labels |
| `.md` `.markdown` | plain text, blocks split on blank lines | written back as-is | headings, code fences, tables, block quotes, link definitions, indented code |
| `.txt` | plain text, blocks split on blank lines | written back as-is | very short blocks |

Markdown fences are tracked per line, so anything inside one, tables included, is untouched. The output extension may differ from the input.

## Tuning

Every rule fires per hit at a probability set in `config_default.json`; a per-project file passed through `--config` overrides it. `0` disables a rule, and below `0.3` it rarely fires. `seed` fixes the draw so a run reproduces. `forbidden` lists words that invalidate any candidate containing them. `selection.min_divergence` sets how far a candidate must move, as 3-gram overlap with the source, to count as a real rewrite.

Term restoration and citation repair ignore these probabilities and always run in full.

Why the thresholds sit where they do is in `references/chains.md`.

The rule groups, in the order they execute: English runs punctuation, terms, connective swaps, `is responsible for`, `, -ing` tails, modal passives, long-sentence splits, repeated openings, then citation repair. Chinese runs punctuation, terms, stock-frame deletion, ordinal series, connective swaps, trailing connectives, light verbs, passives, high-frequency trimming, long-sentence splits, repeated openings, redundant words, then citation repair.

## Terms

Identifiers are protected without configuration. The script extracts camel-case names, all-caps acronyms, `ns:Action` identifiers, subscript keys, version numbers and repeated product names, and discards any candidate that loses one. This check runs only when source and target language match, since identifiers are legitimately translated across languages.

Replacement is opt-in, because it is a global regex and a wrong table damages the document:

```json
[["\\bkms:\\s*Decrypt\\b", "kms:Decrypt"], ["\\breplay memory\\b", "replay cache"]]
```

Templates live in `projects/terms.example.json`, with a validated Kerberos and AWS table at `projects/terms.kerberos-aws.json`. Without `--terms`, nothing is replaced and the run says so.

## Checks

A candidate is discarded before ranking if it loses a number, a citation or a protected identifier, breaks a term count, contains a forbidden word, or changes length outside a band: 0.70–1.45 words for English, 0.75–1.40 characters for Chinese, or 0.30–1.05 English words per Chinese character across languages. The length band exists because free endpoints sometimes drop the tail of a long paragraph while leaving numbers and citations intact.

## Artifacts

```
<out>                    rewritten document, metadata scrubbed
<out>.work/units/        raw translation and error per block per chain
<out>.work/result.json   every candidate, its scores, validation problems, final text
<out>.work/report.md     per-block table, unrewritten reasons, skip list
```

## Stopping

The block list is finite, each hop gets three attempts, the chain count is fixed by `--level`, and there are no `while` loops. PDF export times out at 600 seconds for LibreOffice and 300 for Word.

Every block ends in one of six states. Four are written back (`replaced`, `replaced-low-sim`, `replaced-min-change`, `replaced-worse`); two keep the original text (`all-candidates-failed-validation`, `all-chains-failed`). All six appear in the report. Nothing is skipped silently.

Exit codes: `0` all blocks replaced, `1` nothing to rewrite, `2` some blocks kept or PDF export failed, `3` no usable chain.

A human can sign off when the run exits `0`, no block failed, every `replaced-min-change` and `replaced-worse` block has been read, and the document has been read once end to end.

## Limits worth knowing

A `.docx` write merges runs inside a paragraph, so mid-paragraph bold, italics and superscript citation numbers are lost; check formatting after export. Markdown and plain text are unaffected.

Chinese character stacking, over-long attributives and parallelism density are measured but never rewritten, since a regex cannot find the correct boundary. The numbers sit in `features` in `result.json`.

Free endpoints rate-limit. Run long documents in batches; rerunning with the same arguments resumes.

A full-document rewrite also touches blocks that were fine, and can leave them worse. The status column says which.

English documents need `torch`, `transformers` and a cached `gpt2`, about 3GB. Behind the Great Firewall, prefetch once with `HF_ENDPOINT=https://hf-mirror.com`.

`--out-pdf` shells out to LibreOffice, falling back to Word COM on Windows. Nothing else needs an external program.

Document text goes to the third-party endpoints listed above. Do not run this on confidential material.
