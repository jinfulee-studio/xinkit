# xinkit

The public methodology layer of **Xin** (心) — a working system for AI coding agents.

Xin is Chinese for *heart*, but the sense intended here is **用心** — attentiveness:
doing the work properly rather than producing something that merely looks done.

## What this is

A Claude Code plugin carrying verification discipline, structured debugging, and
completion gates. Install it and your sessions inherit those rules.

```
claude plugin marketplace add jinfulee-studio/xinkit
claude plugin install xin@xinkit
```

## What's inside

**Session axioms** (injected at every session start, ~500 tokens)
Verification tiers L1/L2/L3 · no claim without evidence · structured debugging with a
one-failure stop rule · change channel after two same-shaped failures · less is more ·
read before write.

**Review and build agents** (invoked when relevant)
- `silent-failure-hunter` — finds error handling that swallows failures without surfacing them
- `type-design-analyzer` — scores encapsulation, invariant expression, and enforcement
- `spec-analyst` — extracts requirements and specifications from code or prose
- `project-health-auditor` — technical debt, hotspots, speculative abstraction, dead code
- `bugfixer` — root-cause-first bug fixing with a stop rule on repeated failure
- `qa-tester` — end-to-end verification against real output, not reported success
- `test-runner` — runs the suite, reads failures, proposes fixes
- `research-agent` — structured external research with sourced findings
- `doc-writer` — technical documentation, API docs, changelogs

**Skills**
- `defense-audit` — evaluates defenses across Detection → Prevention → Recovery → Learning
- `awwwards-design` — original award-grade web design systems, motion language, page specs
- `awwwards-audit` — evidence-based UI/UX audit scored on design, usability, creativity, content


## What this is not

**This repository is an automatically generated build target. It is read-only.**

The source lives in a separate private repository and is published here by a one-way
script. Pull requests cannot be merged — they would be overwritten on the next publish.
Open an issue instead if something looks wrong.

## Honest scope

The execution layer this relies on — hook events, `settings.json` schema, plugin
marketplaces, subagent orchestration — is **Claude Code machinery**. Other agents
(OpenAI Codex, and others) can consume the same plugin format and the plain-text rules,
but they are bridged consumers, not native peers. The name is vendor-neutral; the
runtime underneath currently is not. Stated plainly so the name isn't read as a
capability claim it can't back.

## License

MIT. See LICENSE.
