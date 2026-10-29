---
name: amox-grill-me
description: Interview the user about a plan or design until reaching shared understanding, resolving decision dependencies and recommending answers. Invoke explicitly to stress-test a plan.
disable-model-invocation: true
license: MIT
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Finding facts is your job. When a question needs a fact from the environment (filesystem, tools, etc.), look it up yourself; delegate to a sub-agent when the investigation warrants it.

The decisions are mine: put each to me and wait for my answer. Do not act on the plan until I confirm we have reached a shared understanding.
