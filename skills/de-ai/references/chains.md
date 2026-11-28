# Translation Chains, Feature Thresholds, and Scoring

Reference notes for `scripts/chains.py`, `scripts/rules.py`, and `scripts/score.py`. Directional patterns below guided rule design; the exact English numbers come from a single paired-document comparison and are used only for internal candidate ranking.

## Chain design

The pipeline tries up to four 3-hop paths per block in sequence. It filters candidates by validation and prioritizes similarity and overlap before using the score to rank candidates in the same group.

| Chain | `EN -> EN` hops | `ZH -> ZH` hops | Hop count |
| --- | --- | --- | --- |
| 1 | `EN -[iciba]-> DE -[qq]-> FR -[youdao]-> EN` | `ZH -[iciba]-> DE -[qq]-> FR -[youdao]-> ZH` | 3 |
| 2 | `EN -[qq]-> JA -[iciba]-> DE -[youdao]-> EN` | `ZH -[qq]-> JA -[iciba]-> DE -[youdao]-> ZH` | 3 |
| 3 | `EN -[iciba]-> RU -[qq]-> DE -[iciba]-> EN` | `ZH -[iciba]-> RU -[qq]-> DE -[iciba]-> ZH` | 3 |
| 4 | `EN -[reverso]-> DE -[qq]-> ZH -[iciba]-> EN` | `ZH -[reverso]-> DE -[qq]-> EN -[iciba]-> ZH` | 3 |

- For cross-language runs (such as `ZH -> EN`), the final hop (`None` in `DEFAULT_CHAINS`) resolves to the target language (`EN`), and `BRIDGE` in Chain 4 picks the first code in `zh, en, ja, fr, de, ru` that is neither source nor target (`ja` for `ZH <-> EN`).
- `tier1` restricts final hops to `youdao` and `iciba`. Using `reverso` on the final English hop retains European academic phrasing that still triggers detector highlights, so `reverso` is used only on Hop 1 or in the `tier2` fallback pool.
- `modernMt` requires an API key and is omitted from default chains.

## English paragraph feature comparison

English rule targets in `rules.py` and weights in `EnglishScorer` derive from comparing detector-highlighted paragraphs against unhighlighted paragraphs in a benchmark pair:

| Feature | Highlighted | Passed | Rule target |
| --- | --- | --- | --- |
| Sentences `<= 11` words | `7.7%` | `15.7%` | `>= 16%` |
| Modal passive per sentence | `+51.3%` | baseline | `<= 0.08` |
| Trailing `, -ing` rider per sentence | `0.173` | `< 0.05` | `0` |
| Comma count per sentence | `1.55` | `1.11` | `<= 1.15` |
| Stock NMT connectives | `+30.4%` | baseline | rotate within class, do not delete |
| Sentence-level GPT-2 NLL std | `0.476` | `0.580` | `>= 0.55` |
| 3-gram Jaccard overlap with source | `0.361` (untreated) | `0.110` (cleared) | `< 0.22` |

No paired detector sample exists for Chinese, so `ChineseScorer` and the `zh_*` rules track countable surface features directly: uniform long sentences, low punctuation variety, stock connectives (`首先`, `此外`, `因此`, `综上所述`), `的` stacking, light verbs (`进行`, `实现`, `具有`, `起到`, `加以`, `予以`), passives (`被…所`, `得到了`, `受到了`), `、` parallel runs, and opening frames (`随着…的发展`, `在…的背景下`).

## Candidate scoring formulas

Lower `score` ranks higher. Both scorers divide `raw` by its theoretical maximum (`1.575` for English, `1.55` for Chinese) so short paragraphs do not saturate at `1.0`. Scores rank candidates within the same block and are not detector probabilities.

### English (`EnglishScorer`: local `gpt2` + surface statistics)

```text
raw      = 0.45
           - 0.60 * short_sent_frac
           - 0.25 * (sent_nll_std - 0.50)
           + 0.40 * uniform_sent_frac
           + 0.35 * modal_passive_rate
           + 0.25 * nmt_conn_rate
base     = clip(raw / 1.575, 0.0, 1.0)
penalty  = 0.80 * gerund_comma_rate
           + 0.35 * max(0.0, the_this_starter_frac - 0.30)
           + 0.50 * max(0.0, trigram_jaccard - 0.22)
           + 0.20 * modal_passive_rate
score    = base + penalty
fidelity = cosine(cand_gpt2_hidden_mean, orig_gpt2_hidden_mean)   # default min_sim: 0.99
```

### Chinese (`ChineseScorer`: surface statistics only)

```text
raw      = 0.40
           - 0.50 * short_frac
           + 0.30 * min(1.0, max(0.0, (avg_len - 30) / 25))
           + 0.15 * min(1.0, comma_rate / 2.5)
           + 0.20 * min(1.0, max(0.0, (de_rate - 2) / 4))
           + 0.25 * min(1.0, connector_rate / 1.0)
           + 0.15 * min(1.0, vague_verb_rate / 1.0)
           + 0.10 * min(1.0, passive_rate / 1.5)
           - 0.10 * min(1.0, punct_variety / 8)
base     = max(0.0, raw / 1.55)
penalty  = 0.50 * max(0.0, trigram_jaccard - 0.22)
score    = base + penalty
fidelity = min(len(orig), len(cand)) / max(len(orig), len(cand)) # default min_sim: 0.75
```

## Fidelity validation (`score.validate`)

When `selection.require_validation` is `true` (default), a candidate is rejected before ranking if any check fails:

1. **Numbers**: every numeric literal (`\d+(?:\.\d+)?`) in the source appears in the candidate.
2. **Citations**: every `[N]` reference number in the source appears in the candidate.
3. **Code/policy identifiers**: uppercase constants (`[A-Z][A-Z0-9_]{1,}`), `ns:Action` tokens, and underscore identifiers (`[A-Za-z]+_[A-Za-z0-9_]+`) in the source survive in the candidate.
4. **Auto-extracted protected terms** (same-language runs): camelCase names, acronyms, subscript keys (`K_c,tgs`), version numbers, and repeated capitalized multi-word names keep at least their original occurrence count.
5. **Term-table counts** (`dst_lang == "en"` only): each replacement string in `--terms` appears the exact same number of times in source and candidate.
6. **Forbidden words and placeholders**: no newly introduced string from `forbidden`, and no leftover `QZ\d{3}ZQ` placeholder token.
7. **Length ratio**: `0.70–1.45` English words or `0.75–1.40` Chinese characters for same-language blocks (`>= 10` units), or `0.30–1.05` English words per Chinese character on cross-language runs (`>= 20` CJK characters). This catches silent tail truncation by free translation endpoints even when numbers and citations sit near the top of the paragraph.
