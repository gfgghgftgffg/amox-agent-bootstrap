---
name: de-ai
description: "Rewrite .docx, .md, or .txt documents in Chinese or English through cross-family translation chains and deterministic regex cleanup. Invoke explicitly when asked to remove machine-translation phrasing or generated-text patterns without letting a language model write the prose."
disable-model-invocation: true
license: MIT
metadata:
  version: "1.0"
---

# De-AI Pipeline

Run `scripts/pipeline.py` to rewrite document blocks through 3-hop cross-family translation chains and seeded regex rules. Never author, polish, or patch document prose yourself: your job is to run the script, inspect its artifacts, perform at most one targeted rerun if needed, and report the outcome.

> [!WARNING]
> `pipeline.py` sends target paragraphs to third-party translation endpoints via `translators`. Do not run it on confidential or restricted files.

## Environment

Use the active environment's Python interpreter (`codex` Conda environment on bootstrapped hosts) and install missing packages from `scripts/requirements.txt` rather than reimplementing steps:

```bash
PY=python
S="<skill-dir>/scripts/pipeline.py"
```

English targets also require `torch`, `transformers`, and cached `gpt2` weights (~3 GB; prefetch once with `HF_ENDPOINT=https://hf-mirror.com` when Hugging Face Hub is blocked). `--out-pdf` requires `.docx` input plus LibreOffice (or Microsoft Word on Windows).

## Steps

### 1. Confirm input, output path, and target language

- Supported inputs: `.docx`, `.md`, `.markdown`, `.mdown`, `.txt`. Save pasted chat text to a `.md` or `.txt` file first; ask the user to re-save legacy `.doc` files as `.docx`.
- Confirm target output language (`zh` or `en`; defaults to matching the source language via `--dst-lang same`).
- Choose an `--out` path distinct from `--input`. `pipeline.py` opens `--input` read-only and exits with an error if `--out` resolves to the same file.

Use `--dst-lang same` to keep the source language. If the user requests a different language, set `--dst-lang zh` or `--dst-lang en` explicitly in both commands below.

### 2. Run a dry-run check

```bash
"$PY" "$S" --input "<input>" --out "<output>" --src-lang auto --dst-lang same --dry-run
```

Inspect console output and `<output>.work/plan.json`:

- Confirm target block count and check `skipped` so body paragraphs were not accidentally excluded.
- Verify detected source language: `auto` picks `zh` only when every target block has a CJK/Latin ratio `> 0.3`, otherwise `en`. Pass `--src-lang zh` or `--src-lang en` explicitly on mixed-language documents.
- Confirm at least two translation chains passed probing; if fewer than two are reachable, customize `chain_templates` via `--config` before proceeding.

### 3. Run the rewrite

```bash
"$PY" "$S" --input "<input>" --out "<output>" --src-lang auto --dst-lang same --level standard
```

`--level` controls chain count (`light`: 1, `standard`: 3, `deep`: 4). Start with `standard`.

### 4. Inspect `<output>.work/report.md` and `result.json`

| Block status | Meaning | Required action |
| --- | --- | --- |
| `replaced` | Passed validation, similarity, divergence, and score checks | None |
| `replaced-low-sim(<min_sim)` | Written back below similarity threshold (`0.99` EN / `0.75` ZH); possible meaning drift | Present `orig` and `final` side by side for user review |
| `replaced-min-change(<min_div)` | Written back with `3-gram` Jaccard overlap `< 0.10` (`chosen_divergence` in `result.json`) | Rerun once with `--level deep`; if unchanged, report that mechanical rewriting could not improve the block |
| `replaced-worse(+Δ)` | Written back, though every valid candidate scored higher (worse) than `orig_score` | Show `orig` and `final` so the user can choose |
| `all-candidates-failed-validation` | Original kept because every chain failed fidelity checks | Inspect `candidates[].validation` (`length anomaly` = truncation, `term drift` = changed term count, `numbers missing` / `citations missing` / `identifiers missing` / `protected term lost`) |
| `all-chains-failed` | Original kept because every chain errored | Inspect `failed[].detail` (typically endpoint rate limits or network failures) |

### 5. Rerun at most once

If blocks ended in `replaced-min-change`, `replaced-worse`, `all-candidates-failed-validation`, or `all-chains-failed`, run at most one second pass using `--level deep` or a different `--seed`. Stop after round two regardless of remaining statuses. The script caches both translations and errors under `<output>.work/units/` by text, chain, languages, configuration and seed. A new seed creates new cache keys.

### 6. Report results

Include four items in your reply:

1. Counts of targeted, replaced, skipped, and failed (kept-original) blocks, plus any `[tier2]` hop downgrades logged during probing.
2. Per-block summary (`unit`, `status`, `chosen_chain`, `Before` and `After` scores, and `3-gram overlap`).
3. Specific blocks requiring human review (`replaced-low-sim`, `replaced-worse`, `replaced-min-change`, `all-candidates-failed-validation`, `all-chains-failed`, and Chinese `features` metrics in `result.json` when `dst == "zh"`).
4. One plain note that `chosen_score` (`After` in `report.md`) only ranks candidates within a block and is not a detector probability. State this once without repeating disclaimers.

## CLI flags and exit codes

| Flag | Purpose |
| --- | --- |
| `--input`, `--docx` | Input path (`.docx`, `.md`, `.markdown`, `.mdown`, `.txt`) |
| `--out`, `--out-docx` | Output path (extension selects output format) |
| `--src-lang auto\|en\|zh` | Source language (`auto` default) |
| `--dst-lang same\|en\|zh` | Target language (`same` default) |
| `--level light\|standard\|deep` | Run `1`, `3` (default), or `4` chains |
| `--min-words <int>` | Minimum CJK chars + English words per target block (`30` default) |
| `--config <json>` | Probabilities, thresholds, seed, and `chain_templates` (copy from [projects/rewrite.example.json](projects/rewrite.example.json)) |
| `--terms <json>` | Optional `[[regex, replacement], ...]` table ([projects/terms.example.json](projects/terms.example.json), [projects/terms.kerberos-aws.json](projects/terms.kerberos-aws.json)) |
| `--work <dir>` | Artifact/cache directory (`<out>.work` default) |
| `--seed <int>` | Override random seed |
| `--dry-run` | Write a block and chain plan without rewriting |
| `--skip-preflight` | Skip initial hop probing |
| `--out-pdf <pdf>` | Convert `.docx` output to metadata-scrubbed PDF (LibreOffice 600s timeout, Windows Word 300s timeout) |

Exit codes: `0` all target blocks replaced; `1` invalid arguments or zero target blocks; `2` one or more blocks kept original text or PDF export failed; `3` zero usable chains.

## Chains, rules, and known limits

See [references/chains.md](references/chains.md) for chain designs, scoring weights, and validation thresholds:

- **Default chains**: Four 3-hop templates (`de -> fr -> target`, `ja -> de -> target`, `ru -> de -> target`, `de -> BRIDGE -> target`). Mid hops prefer `iciba`, `qqTranSmart`, and `reverso`; `tier1` final hops use only `youdao` or `iciba` (`reverso` sits in `tier2` because it leaves stiff European academic phrasing on final hops).
- **Rule order**:
  - English: punctuation -> `--terms` -> ordinals & connectives -> `is/are responsible for` -> `, -ing` / `and -ing` -> modal passives -> long-sentence split -> repeated starters -> `[N]` citation restore.
  - Chinese: punctuation -> `--terms` -> stock-frame deletion -> ordinals -> connectives -> trailing `，从而`/`，使得`/`，并且` swaps -> light-verb compaction -> passives -> high-frequency modifier trim -> long-sentence split -> period-connector fragment fix -> repeated starters -> redundant words -> `[N]` citation restore.
- **Terminology**: Same-language runs auto-protect camelCase, uppercase acronyms, `ns:Action`, `K_c,x`, version numbers, and repeated capitalized names. `--terms` defaults to empty so global regexes never alter unrelated prose unprompted.
Review the full output before sign-off, including flagged replacements and `.docx` formatting.

- **Format and linguistic limits**:
  - `.docx` writes preserve paragraph styles and scrub `docProps/core.xml`, while merging runs inside modified paragraphs (dropping inline bold, italics, and superscripts). Markdown fences (including tables inside fences) stay untouched.
  - Chinese `的` density, max `的` per sentence, and `、` parallelism runs are recorded in `result.json` (`features`) for human editing rather than rewritten by regex.
  - Free translation endpoints rate-limit long runs; rerun with identical flags to resume from `<output>.work/units/`.
