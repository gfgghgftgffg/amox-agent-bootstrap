---
name: amox-grill-me
description: Question a plan or design across its decision tree, look up codebase facts first, and recommend an answer for every trade-off. Invoke explicitly before implementation.
disable-model-invocation: true
license: MIT
---

Examine every part of this plan and question unresolved assumptions until we reach a shared understanding. Work through the design tree in dependency order so upstream choices settle before downstream ones. For each question, provide your recommended answer.

Look up verifiable facts yourself before asking me: inspect the filesystem, codebase, configs, and available tools, and delegate to a sub-agent when the investigation warrants it.

The decisions are mine: put each to me and wait for my answer. Do not act on the plan until I confirm we have reached a shared understanding.
