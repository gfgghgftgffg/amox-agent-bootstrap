# de-ai

Rewrite a document so it reads less like machine translation or generated text. Works on `.docx`, `.md` and `.txt`; Chinese or English sources, English or Chinese output.

The rewrite is **cross-family machine translation to break the word order, then deterministic regex to shave sentence tails and length**. No LLM writes the prose.

## How it works

```
source --[iciba]-->   German  --[qq]--> French  --[youdao]--> source language
source --[qq]-->      Japanese --[iciba]--> German --[youdao]--> source language
source --[iciba]-->   Russian --[qq]--> German  --[iciba]-->  source language
source --[reverso]--> German  --[qq]--> bridge  --[iciba]-->  source language
```

Each block runs every chain, producing one candidate per chain. Candidates are cleaned, validated, then ranked. Cleaning is pure regex:

- English: drop `, -ing` riders, reduce modal passives, swap filler connectives within a class, split long sentences at a real subject, break runs of identical sentence openings
- Chinese: delete stock frames (`随着…的发展`, `综上所述`), turn light verbs into real ones (`进行了分析` → `分析了`), rewrite passives, thin high-frequency modifiers, swap trailing connectives (`，从而`, `，使得`), split long sentences

Every rule has a probability you can tune; the seed makes runs reproducible.

## Install

```bash
pip install -r scripts/requirements.txt
```

English documents additionally need `torch` and `transformers` plus a cached GPT-2 (about 3GB). Where the Hugging Face Hub is unreachable, pre-fetch once:

```bash
HF_ENDPOINT=https://hf-mirror.com python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('gpt2')"
```

After that the model loads offline.

## Usage

As an agent skill: drop this directory into `~/.pi/agent/skills/` (or a compatible skills directory) together with the prompt template, then invoke it explicitly — it is excluded from automatic model selection on purpose.

Or run it directly:

```bash
# Chinese in, Chinese out
python scripts/pipeline.py --input in.md --out out.md --src-lang zh --dst-lang zh

# English in, English out (Word)
python scripts/pipeline.py --input in.docx --out out.docx --src-lang en --dst-lang en

# Chinese in, English out
python scripts/pipeline.py --input in.txt --out out.txt --src-lang zh --dst-lang en
```

Dry run first to see the plan:

```bash
python scripts/pipeline.py --input in.docx --out out.docx --src-lang auto --dst-lang same --dry-run
```

Supported extensions: `.docx`, `.md`, `.markdown`, `.txt`. Legacy `.doc` must be re-saved as `.docx`.

## Engine availability

Translation goes through the free endpoints wrapped by [`translators`](https://github.com/UlionTse/translators). **Each hop tries tier1 first — the set validated by the original experiment — and falls back to a general pool only when tier1 is unreachable.**

| Network | Usually reachable |
|---|---|
| Mainland China | `iciba`, `qqTranSmart`, `youdao`, `baidu` |
| Elsewhere | `reverso`, `bing`, `google`, `yandex` |

Every hop prints the engine and tier it landed on; `[tier2]` means the validated engine was unreachable:

```
chain2 zh->ja      uses qqTranSmart  [tier1]
chain3 de->en      uses baidu        [tier2]  <- downgraded
```

To change the order, override `chain_templates` — each hop is `[lang, [tier1...], [tier2...]]`:

```json
{
  "chain_templates": [
    [["de", ["reverso"], ["bing", "google"]],
     ["fr", ["qqTranSmart"], ["bing"]],
     [null, ["iciba"], ["youdao", "reverso"]]]
  ]
}
```

## Terminology

Protection needs no configuration: camel-case names, all-caps acronyms, `ns:Action` identifiers, subscript keys, version numbers and repeated product names are extracted from the document, and any candidate that loses one is discarded.

Replacement needs an explicit table, because it is a global regex and a wrong table damages the document:

```bash
python scripts/pipeline.py --input in.docx --out out.docx --terms projects/terms.example.json
```

## Artifacts

```
out.docx                     rewritten document, metadata scrubbed
out.docx.work/report.md      per-block table, unrewritten reasons, skip list
out.docx.work/result.json    every candidate, scores, validation problems, final text
out.docx.work/units/         raw translation per block per chain, reused on rerun
```

## Validation

A candidate is discarded if any check fails: number set, citation set, uppercase identifiers, term counts, forbidden words, length ratio.

The length ratio (0.70–1.45 words for English, 0.75–1.40 characters for Chinese) guards against silent truncation — free endpoints drop the tail of long paragraphs while numbers and citations survive, so length is the only signal left.

## Caveats

- The ranking score is not a detector probability. It is comparable only between candidates of the same block and between a block's before and after. This tool promises no detection score.
- A `.docx` write merges runs inside a paragraph: mid-paragraph bold, italics and superscript citation numbers are lost. Check formatting after export.
- A full-document rewrite also touches blocks that were fine, and can make them worse. Read the output.
- Document text is sent to the third-party translation endpoints above. Do not use it on confidential material.
- PDF export needs LibreOffice (cross-platform) or Microsoft Word on Windows. Everything else needs no external program.

## License

MIT
