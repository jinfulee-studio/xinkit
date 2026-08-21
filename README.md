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
