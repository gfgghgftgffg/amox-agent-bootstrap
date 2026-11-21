# Chains, features and scoring

Background for the rules. The direction of each finding is trustworthy; the absolute numbers come from a single pair of documents and should not be extrapolated.

## Chains

The final hop is restricted to `youdao` / `iciba`. Reverso as an English terminal keeps European academic phrasing and still gets flagged on a second pass, so it appears only as a mid hop or in the tier2 final-hop pool. modernMt needs an API key and is not used.

| # | English source (EN→EN) | Chinese source (ZH→ZH) | Hops |
|---|---|---|---|
| A | `EN-iciba-DE → FR-qq → EN-youdao` | `ZH-iciba-DE → FR-qq → ZH-youdao` | 3 |
| B | `EN-qq-JA → DE-iciba → EN-youdao` | `ZH-qq-JA → DE-iciba → ZH-youdao` | 3 |
| C | `EN-iciba-RU → DE-qq → EN-iciba` | `ZH-iciba-RU → DE-qq → ZH-iciba` | 3 |
| D | `EN-reverso-DE → ZH-qq → EN-iciba` | `ZH-reverso-DE → EN-qq → ZH-iciba` | 3 |

For a Chinese source with English output the last hop lands on EN; the bridge language is the first language that is neither source nor target (usually Japanese).

The chains run in parallel on the same block and the best candidate wins. There is no second round.

## Per-paragraph feature comparison

One historical comparison between paragraphs a detector highlighted and paragraphs it passed. This is where the English rule thresholds come from.

| Feature | Highlighted | Passed | Rule target |
|---|---|---|---|
| Sentences ≤11 words | 7.7% | 15.7% | ≥16% |
| Modal passive / sentence | +51.3% | baseline | ≤0.08 |
| Trailing participial rider / sentence | 0.173 | <0.05 | 0 |
| Comma density / sentence | 1.55 | 1.11 | ≤1.15 |
| Stock connectives | +30.4% | baseline | swap, not delete |
| Sentence-level NLL std | 0.476 | 0.580 | ≥0.55 |
| 3-gram overlap with source | 0.361 (untreated) | 0.110 (cleared) | <0.22 |

There is no equivalent measurement for Chinese. The Chinese rules come from countable features: concentrated sentence length, low punctuation variety, connective density, `的` stacking, light verbs (进行/实现/具有/起到), passives (被…所/得到了/受到了), parallelism density, and stock frames (随着…的发展, 在…的背景下, 综上所述).

## Scoring

**English** (`EnglishScorer`, GPT-2 plus sentence statistics)

```
raw    = 0.45
         - 0.60 × short-sentence fraction
         - 0.25 × (sentence NLL std − 0.50)
         + 0.40 × uniform-length fraction
         + 0.35 × modal-passive rate
         + 0.25 × filler-connective rate
base   = clip(raw / 1.575, 0, 1)          # normalised by the formula's maximum
score  = base
         + 0.80 × gerund-rider rate
         + 0.35 × max(0, The/This opener fraction − 0.30)
         + 0.50 × max(0, 3-gram overlap − 0.22)
         + 0.20 × modal-passive rate
fidelity = cosine of GPT-2 last hidden state, threshold 0.99
```

**Chinese** (`ChineseScorer`, statistics only, no model)

```
raw  = 0.40
       - 0.50 × short-sentence fraction
       + 0.30 × sentence-length overshoot
       + 0.15 × comma density
       + 0.20 × 的 density overshoot
       + 0.25 × connective density
       + 0.15 × light-verb rate
       + 0.10 × passive rate
       - 0.10 × punctuation variety
base = max(0, raw / 1.55)
score = base + 0.50 × max(0, 3-gram overlap − 0.22)
fidelity = length ratio, threshold 0.75
```

Normalisation by the theoretical maximum exists because short blocks otherwise saturate at 1.0 and candidates stop being distinguishable.

The score is used only to rank candidates and to compare a block before and after. It is not any detector's output.

## Validation

A candidate is discarded if any check fails:

1. Number set containment
2. Citation-number set containment
3. Uppercase identifiers and `ns:Action` names preserved
4. Term-table replacement counts unchanged (English target only)
5. Length ratio: 0.70–1.45 words for English, 0.75–1.40 characters for Chinese; across languages, 0.30–1.05 English words per Chinese character

Check 5 is the only one that catches a translation endpoint silently truncating a long paragraph.
