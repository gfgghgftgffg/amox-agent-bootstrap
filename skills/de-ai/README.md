# de-ai

English | [简体中文](README.zh-CN.md)

![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)
![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)

[Install](#install) • [Quick start](#quick-start) • [How it works](#how-it-works) • [Translation chains](#translation-chains) • [Configuration](#configuration) • [CLI reference](#cli-reference) • [Output](#output)

Rewrite `.docx`, `.md`, or `.txt` documents in Chinese or English using cross-family machine translation chains and deterministic regex cleanup. All output prose comes from translation endpoints and seeded rule transforms rather than language-model generation.

> [!WARNING]
> Target paragraphs are sent to third-party translation endpoints via [`translators`](https://github.com/UlionTse/translators). Do not run this tool on confidential or restricted documents.

## Install

Requires Python 3.9 or newer.

```bash
pip install -r scripts/requirements.txt
```

English target documents also use `torch`, `transformers`, and local `gpt2` weights (roughly 3 GB total) for candidate scoring and hidden-state similarity.

> [!TIP]
> If Hugging Face Hub is unreachable on your network, cache `gpt2` once through a mirror before running offline:
>
> ```bash
> HF_ENDPOINT=https://hf-mirror.com python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; AutoTokenizer.from_pretrained('gpt2'); AutoModelForCausalLM.from_pretrained('gpt2')"
> ```

## Quick start

```bash
# Preview target and skipped blocks without translating
python scripts/pipeline.py --input in.docx --out out.docx --src-lang auto --dst-lang same --dry-run

# Rewrite Chinese Markdown and save it to a new file
python scripts/pipeline.py --input in.md --out out.md --src-lang zh --dst-lang zh

# Rewrite an English Word document
python scripts/pipeline.py --input in.docx --out out.docx --src-lang en --dst-lang en

# Translate and clean Chinese plain text into English
python scripts/pipeline.py --input in.txt --out out.txt --src-lang zh --dst-lang en
```

`pipeline.py` opens `--input` read-only and refuses runs where `--out` resolves to the input file.

To use `de-ai` as an explicit-only agent Skill ([SKILL.md](SKILL.md)), install this directory into your host's Skills folder (and deploy `pi/prompts/de-ai.md` on Pi), then invoke `/de-ai <file>` or `/skill:de-ai`.

## How it works

1. **Extract blocks**: Splits `.md`/`.txt` on blank lines and reads `.docx` paragraphs, skipping headings, code blocks, tables, captions, references, and blocks shorter than `--min-words` (default `30`).
2. **Run translation chains**: Sends each block through up to four 3-hop chains across two intermediate languages (such as Japanese, Russian, German, and French) so clause order and modifier placement rearrange before returning to the target language.
3. **Apply regex post-processing**: Fixes punctuation, applies optional term replacements, rotates overused connectives and ordinal series, rewrites `, -ing` riders and modal passives (English) or stock frames and light verbs (Chinese), splits long sentences, varies repeated starters, and restores `[N]` citations.
4. **Validate and rank**: Discards any candidate that drops numbers, citations, uppercase/`ns:Action` identifiers, protected terms, or term counts, introduces `forbidden` words, or falls outside the allowed length ratio (`0.70–1.45` words for English, `0.75–1.40` characters for Chinese, `0.30–1.05` English words per Chinese character for `zh -> en`). Among valid candidates, the script first prefers those that meet the similarity threshold. In same-language runs, it then prefers candidates with at least `0.10` 3-gram Jaccard overlap (`selection.min_divergence`). It ranks candidates within each group by the lowest `score` (`base + penalty`). Overlap above `0.22` adds a penalty.

See [references/chains.md](references/chains.md) for the scoring formulas and rule thresholds.

## Translation chains

Default chains probe a `tier1` engine list first and fall back to `tier2` per hop when an endpoint is unreachable:

```text
source --[iciba]-->   de --[qqTranSmart]--> fr     --[youdao]--> target language
source --[qqTranSmart]--> ja --[iciba]-->   de     --[youdao]--> target language
source --[iciba]-->   ru --[qqTranSmart]--> de     --[iciba]-->  target language
source --[reverso]--> de --[qqTranSmart]--> BRIDGE --[iciba]-->  target language
```

`BRIDGE` resolves to the first language in `zh, en, ja, fr, de, ru` that matches neither source nor target. Reachable endpoints depend on network region (`iciba`, `qqTranSmart`, `youdao`, `baidu` in mainland China; `reverso`, `bing`, `google`, `yandex` elsewhere).

```text
chain2 zh->ja      uses qqTranSmart  [tier1]
chain3 de->en      uses baidu        [tier2]  <- downgraded
```

> [!NOTE]
> `tier1` restricts final hops to `youdao` and `iciba` because `reverso` on the final hop leaves stiff academic phrasing; `reverso` is used only as a mid hop or `tier2` fallback.

Override `chain_templates` in your config JSON (`[language, [tier1...], [tier2...]]`, where `null` means the document target language):

```json
{
  "chain_templates": [
    [["de", ["reverso"], ["bing", "google"]],
     ["fr", ["qqTranSmart"], ["bing"]],
     [null, ["iciba"], ["youdao", "reverso"]]]
  ]
}
```

## Configuration

### Rewrite rules

Copy [projects/rewrite.example.json](projects/rewrite.example.json) and pass it via `--config`:

```json
{
  "seed": 42,
  "ordinal_series": "auto",
  "max_per_word": 2,
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
  "selection": {
    "min_sim": { "en": 0.99, "zh": 0.75 },
    "require_validation": true,
    "keep_all_candidates": true,
    "min_divergence": 0.1
  }
}
```

- Rule values (`0.0` to `1.0`) set per-match trigger probabilities (`0` disables a rule); `seed` fixes the random choices made by the cleanup rules.
- `max_per_word` caps connective replacements (and preserves up to `max_per_word` occurrences of `zh_highfreq_words` before trimming); `ordinal_series` keeps numbering consistent (`First / Second / Last` rather than mixed series).
- `forbidden` rejects any candidate introducing listed words. Term replacements and citation restoration run unconditionally.

### Terminology tables

Same-language runs automatically protect camelCase identifiers, uppercase acronyms, `ns:Action` strings, subscript keys (`K_c,tgs`), version numbers, and repeated capitalized names.

Regex term normalization is opt-in via `--terms` so unrelated prose is never altered by default:

```json
[
  ["\\bkms:\\s*Decrypt\\b", "kms:Decrypt"],
  ["\\breplay memory\\b", "replay cache"]
]
```

```bash
python scripts/pipeline.py --input in.docx --out out.docx --terms projects/terms.example.json
```

Start from [projects/terms.example.json](projects/terms.example.json) or inspect [projects/terms.kerberos-aws.json](projects/terms.kerberos-aws.json) for a full technical domain table.

## CLI reference

| Flag | Description |
| --- | --- |
| `--input`, `--docx` | Input path (`.docx`, `.md`, `.markdown`, `.mdown`, `.txt`) |
| `--out`, `--out-docx` | Output path (must differ from `--input`; extension sets output format) |
| `--src-lang auto\|en\|zh` | Source language; `auto` (default) uses `zh` when all target blocks have CJK/Latin ratio `> 0.3`, else `en` |
| `--dst-lang same\|en\|zh` | Target language; `same` (default) matches the resolved source language |
| `--level light\|standard\|deep` | Number of chains to run: `1`, `3` (default), or `4` |
| `--min-words <int>` | Minimum CJK characters + English words per rewritable block (default `30`) |
| `--config <json>` | Rule probabilities, selection thresholds, seed, and `chain_templates` |
| `--terms <json>` | Optional `[[regex, replacement], ...]` table |
| `--work <dir>` | Working and cache directory (default `<out>.work`) |
| `--seed <int>` | Override config `seed` |
| `--dry-run` | Probe chains and write `<work>/plan.json` without translating blocks |
| `--skip-preflight` | Skip initial hop probing |
| `--out-pdf <pdf>` | Export `.docx` output to metadata-scrubbed PDF via LibreOffice (600s timeout) or Windows Word COM (300s timeout) |

**Exit codes**: `0` all target blocks replaced; `1` invalid arguments or no rewritable blocks; `2` one or more blocks kept original text or PDF export failed; `3` no usable translation chain.

## Output

```text
out.docx                    Rewritten document (.docx core metadata scrubbed)
out.docx.work/report.md     Per-block summary table, unreplaced blocks, and skip reasons
out.docx.work/result.json   Full candidate outputs, feature breakdowns, and validation logs
out.docx.work/units/        Cached raw chain translations reused on identical reruns
```

Each target block finishes in one of six statuses: `replaced`, `replaced-low-sim(<min_sim)`, `replaced-min-change(<min_div)`, `replaced-worse(+Δ)` (written back), or `all-candidates-failed-validation`, `all-chains-failed` (original text kept). `Before` and `After` scores in `report.md` rank candidates within a block and are not detector probabilities.

### Format handling and limits

| Format | Read / write behavior | Skipped blocks |
| --- | --- | --- |
| `.docx` | Read/written via `python-docx`; keeps paragraph styles, merges runs inside replaced paragraphs, scrubs `docProps/core.xml` | Heading/Title/TOC/Caption/Bibliography styles, figure/table/reference/abstract lines, monospace paragraphs, blocks `< min-words` |
| `.md`, `.markdown`, `.mdown` | Split on blank lines; written UTF-8 (`\n`) | Headings, fenced/indented code (including tables inside fences), tables, blockquotes, horizontal rules, images, HTML, link definitions, blocks `< min-words` |
| `.txt` | Split on blank lines; written UTF-8 (`\n`) | Blocks `< min-words` |

> [!CAUTION]
> Replacing a `.docx` paragraph merges its runs, removing inline bold, italics, and superscript formatting inside that paragraph. Review `.docx` formatting and any blocks flagged `replaced-min-change` or `replaced-worse` before finalizing. Legacy `.doc` files must be saved as `.docx` first.

### Directory layout

```text
scripts/
  pipeline.py         CLI entry point, caching, candidate selection, and report generation
  docio.py            .docx / Markdown / plain-text block I/O and PDF export
  chains.py           Chain templates, preflight hop probing, and retries
  rules.py            Seeded English and Chinese regex post-processing rules
  score.py            GPT-2 / statistical scoring, term extraction, and fidelity checks
  config_default.json Default rule probabilities and selection thresholds
  requirements.txt    Python package dependencies
references/chains.md  Empirical feature comparisons, scoring formulas, and chain design
projects/             Example rewrite config and terminology tables
```
