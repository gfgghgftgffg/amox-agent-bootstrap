---
description: "Rewrite a .docx, .md, or .txt document through cross-family translation chains and regex cleanup without model-written prose."
argument-hint: "<file> [Chinese|English output] [--level light|standard|deep]"
---
Read the `de-ai` skill's `SKILL.md` in full, then run its `Steps` section using `scripts/pipeline.py` inside that skill directory.

Follow these three rules strictly:

1. Do not write, edit, or paraphrase document prose yourself; every text change must come from `scripts/pipeline.py`.
2. Report every target block that was skipped or kept unchanged with its recorded reason; never manually patch a block that failed translation or validation.
3. Do not claim or estimate an AI-detector score; `chosen_score` (`After` in `report.md`) only ranks candidates within a block.

Request arguments:
$ARGUMENTS

If `$ARGUMENTS` omits a file path, identify the target file from the current conversation. If the target file is still ambiguous, ask the user which file to process before touching any document.
