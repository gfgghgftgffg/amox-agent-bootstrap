- Prioritize final result quality over speed.

- Python 执行与依赖安装统一使用 Conda 的 `codex` 环境；Conda：`{{CONDA_PATH}}`，解释器：`{{PYTHON_PATH}}`。已安装 `pypdf`，可处理 PDF。
- Proxy at 127.0.0.1:7897. Using it if encounter network issues or slow speed.

# Requirement Alignment
- Look up anything findable in the code, configs, or available tools yourself.
- Unless user request, document should not include historical background, troubleshooting processes, or redundant explanations.

# Workflow
- Track tasks of an estimated 5 or more steps with todo and clear it when done; do shorter tasks directly.
- For hard-to-undo actions such as deleting, overwriting, force-pushing, or publishing, confirm first unless the user explicitly asked for them.
- On errors, state the location, cause, and fix; after three consecutive failures, name the suspect assumption. Fix then continue.


Task Router 配置：`{{TASK_ROUTER_CONFIG_PATH}}`；用 `codex -p task-routing` 启动新会话激活。源码：`{{TASK_ROUTER_SOURCE_PATH}}`。
<!-- task-router:start -->
When the task-routing profile is active or the user invokes $task-routing, use that skill for delegation. Otherwise keep the existing workflow.
Its role map defines defaults. Explicit user model/effort instructions take precedence for their stated task or role scope without changing persistent settings. Preserve host permissions and project constraints; report unsupported choices instead of silently substituting models.
Choose among the role map candidates by task complexity, risk, context volume, and economy; do not use the strongest candidate for every task by default.
The parent owns direction and decisions; assigned children follow their role without recursively orchestrating. Load only the role and workflow guidance needed for this task.
Research summaries are navigation aids. Before important evidence-based decisions, the main agent reads the relevant originals and checks coverage; another child does not replace this judgment.
Within the authorized task, continue through the requested deliverable and relevant acceptance checks, fixing failures caused by the change. Do not stop at a first draft or add routine approval checkpoints. Report concrete blockers and unverified requirements.
Match reading and verification to the task. Do not force every role, a full-repository survey, repeated successful checks, or unrelated improvements. Completion does not expand scope or external-action permissions.
<!-- task-router:end -->