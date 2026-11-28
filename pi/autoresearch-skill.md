---
name: {{SKILL_NAME}}
description: Run the installed {{SKILL_NAME}} workflow on explicit user request.
disable-model-invocation: true
---

Read `{{UPSTREAM_SKILL_PATH}}` in full and execute its workflow for the current request. Resolve every relative path in those instructions against that original SKILL.md directory, not this wrapper directory.
