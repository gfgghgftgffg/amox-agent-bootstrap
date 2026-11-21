---
name: de-ai
description: "Rewrite a document so it reads less like machine translation or generated text. Handles .docx, .md and .txt; Chinese or English sources, English or Chinese output. Use when asked to lower AI-detection scores, remove machine-translation tone, or rewrite a document that reads as if it were generated. Rewriting is done by cross-family machine translation plus deterministic regex, never by an LLM writing prose."
disable-model-invocation: true
license: MIT
metadata:
  version: "4.0.0"
---

# De-AI Pipeline

## What you must not do

**Never rewrite, polish or paraphrase the prose yourself.** Not one word.

Every change must come from the scripts in this skill: translation chains reorder the text, regex rules shave sentence tails and lengths. Text you generate yourself carries a language-model sampling fingerprint, which is exactly what this pipeline exists to avoid.

You do four things only: run the script, read the artifacts, decide the next step from the status table, report to the user.

## Your steps

### 0. Environment

Use the current environment's `python`. Dependencies are in `scripts/requirements.txt`; install what is missing instead of substituting an implementation.

```bash
PY=python
S="<skill-dir>/scripts/pipeline.py"
```

### 1. Confirm the input

Accepts `.docx`, `.md`, `.markdown`, `.txt`. If the user pasted text into the chat, write it to `.md` or `.txt` first.

Legacy `.doc` is not supported; ask for a `.docx` re-save.

Ask exactly one question: **Chinese output or English output**. A Chinese source defaults to Chinese output, an English source to English.

### 2. Dry run

```bash
"$PY" "$S" --input "<input>" --out "<output>" --src-lang auto --dst-lang same --dry-run
```

This probes engine availability, then writes `<output>.work/plan.json`. Check three things:

- the number of target blocks is plausible
- the skip list does not contain body prose
- the language guess is right (`auto` uses a CJK ratio; force `--src-lang` for mixed documents)

Do not continue if fewer than two chains survive; see the engine section.

### 3. Real run

```bash
"$PY" "$S" --input "<input>" --out "<output>" --src-lang auto --dst-lang same --level standard
```

`--level` is `light` (1 chain), `standard` (3 chains, default) or `deep` (4 chains). Start with `standard`; do not open with `deep`.

### 4. Read the artifacts

Read `<output>.work/report.md` first, then `<output>.work/result.json` for detail.

| Status | Meaning | What you do |
|---|---|---|
| `replaced` | Normal replacement | Nothing |
| `replaced-low-sim` | Replaced, but far from the source; possible drift | Show `orig` and `final` side by side |
| `replaced-min-change` | No chain actually moved this block | Rerun with `deep`; if it persists, say the block cannot be improved mechanically |
| `replaced-worse(+Δ)` | Written back, but the ranking score went up because every candidate was worse | Give the user both versions and let them choose |
| `all-candidates-failed-validation` | Every candidate lost numbers, citations or terms, or the translation was truncated | Inspect `candidates[].validation`: `length anomaly` means truncated by the endpoint, `term drift` means terminology drift, `numbers missing` means a dropped figure |
| `all-chains-failed` | Every chain errored | Read `detail`; usually network or rate limiting |

### 5. At most one rerun

Run the pipeline again at most once, only for `replaced-min-change`, `replaced-worse`, `all-candidates-failed-validation` and `all-chains-failed` blocks, with `--level deep` or a different `--seed`. Stop after the second round whatever the result.

`<output>.work/units/` caches translations. Rerunning with the same arguments only fills in failed or unfinished chains.

### 6. Report

Four things, nothing more:

1. Blocks processed, replaced, skipped, failed
2. A per-block table: status, chain, before `base+penalty`, after `base+penalty`, 3-gram overlap
3. Blocks that need a human and why
4. One caveat: `new_score` is a candidate ranking score, not a detector probability

## What you must not claim

- Do not promise a detection score. This pipeline contains no detector.
- Do not say a document "passed AI detection". The only evidence is the report the user gets after submitting.
- Do not turn a drop in `new_score` into a percentage drop in AI score.

## Parameters

| Flag | Meaning |
|---|---|
| `--input` / `--docx` | Input file: `.docx`, `.md`, `.markdown`, `.txt` |
| `--out` / `--out-docx` | Output file; the extension decides the format |
| `--src-lang auto\|en\|zh` | Default `auto`, decides per block from a CJK ratio |
| `--dst-lang same\|en\|zh` | `same` keeps the source language |
| `--level light\|standard\|deep` | Run 1, 3 or 4 chains |
| `--terms <json>` | Project term table, `[[regex, replacement], ...]` |
| `--config <json>` | Probabilities, seed, chain templates; see `projects/rewrite.example.json` |
| `--seed N` | Fix the randomness to reproduce a run |
| `--skip-preflight` | Skip engine probing |
| `--out-pdf <pdf>` | `.docx` input only; LibreOffice first, Word as a Windows fallback |

## Chains

Four fixed chain shapes. **Each hop has two engine tiers**: tier1 is the set validated by the original experiment, tier2 is a general fallback pool.

| Chain | Hop 1 | Hop 2 | Hop 3 (final) |
|---|---|---|---|
| 1 | DE · `iciba` | FR · `qqTranSmart` | source lang · `youdao` |
| 2 | JA · `qqTranSmart` | DE · `iciba` | source lang · `youdao` |
| 3 | RU · `iciba` | DE · `qqTranSmart` | source lang · `iciba` |
| 4 | DE · `reverso` | bridge lang · `qqTranSmart` | source lang · `iciba` |

The tier1 assignment follows the measured result: mid hops use `iciba`, `qqTranSmart` or `reverso` to break the source word order, and **the final hop uses only `youdao` or `iciba`** — `reverso` as the last hop leaves European academic phrasing, so it appears only in the tier2 final-hop pool.

tier2 pool: `baidu`, `bing`, `google`, `youdao`, `iciba`, `reverso`, `tencent`, `sogou`, `alibaba`, `caiyun`, `yandex`, `deepl`, `papago`.

Each hop prints the tier it landed on:

```
chain2 zh->ja      uses qqTranSmart  [tier1]
chain3 de->en      uses baidu        [tier2]  <- downgraded
```

**Any `[tier2]` means the validated engine was unreachable and quality may drop.** Say so when reporting.

The bridge language is the first language that is neither source nor target: EN→EN bridges through Chinese, ZH→ZH through English, ZH→EN through Japanese.

To change priorities, set `chain_templates` — each hop is `[lang, [tier1...], [tier2...]]`; the two-element form treats every engine as tier1:

```json
{
  "chain_templates": [
    [["de", ["iciba"], ["baidu", "bing"]],
     ["fr", ["qqTranSmart"], ["baidu"]],
     [null, ["youdao"], ["iciba", "reverso"]]]
  ]
}
```

## Supported formats

| Format | Read | Write | Skipped |
|---|---|---|---|
| `.docx` | python-docx | paragraph styles preserved, runs merged | heading styles, captions, references, monospace paragraphs, short labels |
| `.md` / `.markdown` | plain text, blank-line blocks | written back as-is | headings, code fences, tables, block quotes, link definitions, indented code |
| `.txt` | plain text, blank-line blocks | written back as-is | only very short blocks |

Markdown fences are tracked per line, so anything inside a fence — tables included — is left alone. The output extension may differ from the input.

## Probability config

Every rule fires per hit according to `config_default.json`; a fixed seed makes runs reproducible. Override per project in `projects/<project>/rewrite.json`:

```json
{
  "seed": 42,
  "en": { "connector_swap": 1.0, "gerund_tail": 0.85, "modal_passive": 0.7, "split_long": 0.8, "starter_dedup": 0.9 },
  "zh": { "frame_delete": 0.9, "connector_swap": 0.8, "tail_swap": 0.8, "verbify": 0.7,
          "passive_rewrite": 0.7, "highfreq_trim": 0.6, "split_long": 0.8,
          "redundant_trim": 0.9, "starter_dedup": 0.9 },
  "zh_highfreq_words": ["进一步", "显著", "充分", "全面", "极大", "深入", "有效", "关键", "核心"],
  "forbidden": ["回放缓存"],
  "selection": { "min_sim": { "en": 0.99, "zh": 0.75 }, "min_divergence": 0.10 }
}
```

- `0` disables a rule; below `0.3` it rarely fires.
- Term restoration and citation repair are never randomised; they always run in full.
- Ordinals stay in one series: `First/Second/Last`, `Firstly/Secondly/Finally` or `To begin with/Next/Finally` — never `First` followed by `Secondly`. The Chinese equivalents behave the same way.
- Filler connectives are not deleted; one is swapped for another from the same class, at most `max_per_word` times per word.
- A word in `forbidden` invalidates any candidate containing it; use it to block known mistranslations.
- `min_divergence` is the floor for "this candidate actually changed something" (3-gram overlap with the source). Candidates below it rank last; if all of them are, the status becomes `replaced-min-change`.

## Terminology

Two layers, neither requiring a filled-in table.

**Automatic protection (always on).** Camel-case names (`GetObject`), all-caps acronyms (`TLS`, `KMS`), `ns:Action` (`kms:Decrypt`), subscript keys (`K_c,tgs`), version numbers (`1.3`) and multi-word product names repeated at least twice (`AWS Transfer Family`) are extracted from the whole document. A candidate that loses any of them is discarded. The check runs only when source and target language match, since identifiers are legitimately translated across languages.

**Term replacement (opt-in).** Nothing is replaced by default, because replacement is a global regex and a wrong table damages the document:

```json
[["\\bkms:\\s*Decrypt\\b", "kms:Decrypt"], ["\\breplay memory\\b", "replay cache"]]
```

Templates: `projects/terms.example.json`, plus a validated Kerberos/AWS table at `projects/terms.kerberos-aws.json`.

## Validation (a candidate failing any check is discarded)

The number set, the citation set and uppercase identifiers (`KMS`, `kms:Decrypt`, `K_C`) must survive; with an English target, every term-table replacement must keep its original count; nothing from `forbidden` may appear; length ratio must stay within 0.70–1.45 words for English and 0.75–1.40 characters for Chinese.

The length ratio is the guard against silent truncation: free translation endpoints drop the tail of long paragraphs while numbers and citations survive, so length is the only signal left.

## Artifacts

```
<out>                rewritten document, metadata scrubbed
<out>.work/units/    raw translation and error per block per chain
<out>.work/result.json   every candidate, score, validation problem, final text
<out>.work/report.md     per-block table, unrewritten reasons, skip list
```

## Stop conditions

### Code level (bounded, cannot hang)

| Condition | Behaviour |
|---|---|
| Block list exhausted | Normal exit, writes `result.json` and `report.md` |
| 3 failed attempts per hop | Chain abandoned, error recorded, next chain continues |
| Chain cap | 1 / 3 / 4 per `level`; the script never adds chains |
| Engine probing | One request per (engine, source, target) combination |
| PDF export | 600 s timeout for LibreOffice, 300 s for Word |
| `while` loops in the code | None |

### Block level (every block has one terminal state)

Written back: `replaced`, `replaced-low-sim`, `replaced-min-change`, `replaced-worse`.
Kept as-is: `all-candidates-failed-validation`, `all-chains-failed`.

Both outcomes appear in the report; nothing is skipped silently.

### Agent level (the important one)

**At most two rounds.** First round `standard`; second round `deep` or a new `--seed`, restricted to the failing blocks. Stop and report after the second round regardless of outcome.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Every target block replaced |
| 1 | No rewritable block (check `--min-words` or the input format) |
| 2 | Some blocks kept their original text, or PDF export failed |
| 3 | No usable chain; configure `chain_templates` |

### When a human can sign off

1. Exit code 0.
2. No `all-chains-failed`; no `all-candidates-failed-validation` unless accepted.
3. Every `replaced-min-change` and `replaced-worse` block reviewed.
4. The whole document read once — rewriting touches every block, including ones that were fine.

## Known limits

- A `.docx` write merges runs inside a paragraph, so mid-paragraph bold, italics and superscript citation numbers are lost. Review formatting after export. `.md` and `.txt` are unaffected.
- Chinese `的` stacking, over-long attributives and parallelism density are measured but never rewritten automatically; the numbers sit in `features` in `result.json`.
- Free endpoints rate-limit. Run long documents in batches; rerunning with the same arguments resumes.
- The English score is a heuristic with no calibrated weights; calibration would need paired human annotations.
- A full-document rewrite also changes blocks that were fine before, and can make them worse. Read the result.
- Legacy `.doc` is unsupported; re-save as `.docx`.

## Portability

`--out-pdf` shells out to LibreOffice (Windows, macOS, Linux), falling back to Word COM on Windows. Nothing else needs an external program.

English documents need `torch` and `transformers` plus a cached `gpt2` (about 3GB). Behind the Great Firewall, pre-fetch once with `HF_ENDPOINT=https://hf-mirror.com`.

Document text is sent to the third-party translation endpoints listed above. Do not run this on confidential material.
