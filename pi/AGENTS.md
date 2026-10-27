- Prioritize final result quality over speed.

- Python execution and dependency installation utilize the Conda `codex` environment; Conda path: `{{CONDA_PATH}}`, interpreter path: `{{PYTHON_PATH}}`. `pypdf` is installed for PDF processing.
- Proxy at 127.0.0.1:7897. Using it if encounter network issues or slow speed.

# Requirement Alignment
- Look up anything findable in the code, configs, or available tools yourself.
- Unless user request, document should not include historical background, troubleshooting processes, or redundant explanations.

# Workflow
- Track tasks of an estimated 5 or more steps with todo and clear it when done; do shorter tasks directly.
- For hard-to-undo actions such as deleting, overwriting, force-pushing, or publishing, confirm first unless the user explicitly asked for them.
- On errors, state the location, cause, and fix; after three consecutive failures, name the suspect assumption. Fix then continue.

<!-- pi-task-router:start -->
Task Router for Pi is opt-in. When the user invokes /skill:task-routing or applicable instructions explicitly enable it, the coordinating parent follows that skill and its generated tr_* role map. Otherwise keep the existing workflow.
Installation alone does not authorize delegation. An assigned child follows its role contract and does not activate parent routing or launch further agents.
Use @gfgghgftgffg/pi-subagents-lean from amox_pi_extensions_lean for execution, not builtin role substitutions or a separate runner. Supply exact model and thinking from the role map on every fresh launch; explicit task-scoped choices take precedence. Preserve host permissions and report unsupported routes.
Choose among available direct-subagent and workflow operations by decision structure and useful batching, not agent count or number of steps. If only one is available, use it for bounded phases; do not invent the other. Reassess at safe phase boundaries; independent coding acceptance remains required.
<!-- pi-task-router:end -->