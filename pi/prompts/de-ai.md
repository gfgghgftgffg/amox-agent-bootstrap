---
description: "Rewrite a .docx/.md/.txt so it reads less like machine translation or generated text, without letting a model write the prose."
argument-hint: "<file> [Chinese|English output] [--level light|standard|deep]"
---
Read the `de-ai` skill's `SKILL.md` in full first, then follow its "Your steps" section exactly. The entry point is `scripts/pipeline.py` inside that skill directory.

Three hard constraints:

1. Never rewrite, polish or paraphrase the prose yourself. Every change must come from the scripts.
2. Every target block either gets replaced or is reported with a reason. Never patch a failed block with text the script did not produce.
3. Never promise a detection score. `new_score` is a candidate ranking score only.

The user's input:
$ARGUMENTS

If no file path is given, determine the target from the conversation. If it is still unclear, ask which file to process and do not touch unrelated documents.
