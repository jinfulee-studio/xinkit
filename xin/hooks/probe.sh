#!/usr/bin/env bash
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"XIN_PUBLIC_REACHED_P3W6 host=%s"}}\n' "$(hostname 2>/dev/null || echo unknown)"
