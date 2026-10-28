---
name: {{SKILL_NAME}}
description: Manually invoke the installed {{SKILL_NAME}} workflow.
disable-model-invocation: true
---

Read `{{UPSTREAM_SKILL_PATH}}` in full, then follow its instructions for the user's request. Resolve all relative file references against that original SKILL.md directory, not this wrapper directory.
