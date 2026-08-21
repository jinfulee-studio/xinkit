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

**Working discipline**
- `code-minimalism` — same functionality, fewest elements: single responsibility, deep-not-shallow
  modules, YAGNI, and the anti-patterns that look like good design
- `incident-retro` — classify → 5-Why root cause → extract the pattern → four artifacts → verify
- `defense-audit` — defenses across Detection → Prevention → Recovery → Learning
- `conventional-commit` — commit message discipline and the workflow around it

**Design**
- `uiux-laws` — accessibility, feedback, layout, forms, typography, and the AI-era additions
- `awwwards-design` — original award-grade design systems, motion language, page specs
- `awwwards-audit` — evidence-based UI/UX audit scored on design, usability, creativity, content

**Research**
- `synthetic-panel` — simulate N customer interviews with LLM personas, map qualitative responses
  to purchase intent via semantic anchors (method from arXiv 2510.08338)

**claude.ai Artifacts**
- `artifact-scaffold` / `artifact-mocks` / `artifact-ship` — scaffold a single-file artifact project,
  manage mock fixtures for `window.claude.complete`, validate the hard constraints, then ship it

**Agents** (16, invoked when relevant)
Architecture and implementation — `code-architect` `impl-agent` `bugfixer` `test-specialist` `test-runner`
Review — `code-reviewer` `reviewer` `silent-failure-hunter` `type-design-analyzer` `project-health-auditor` `qa-tester`
Analysis and writing — `spec-analyst` `research-agent` `doc-writer`
Artifacts — `artifact-prompt-engineer` `artifact-validator`


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

