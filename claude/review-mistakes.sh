#!/bin/bash

# Comes from https://www.xda-developers.com/added-one-hook-claude-code-stopped-same-mistake-twice/
# Hook for Claude code to review common mistakes
# requires jq


INPUT=$(cat)
STOP_HOOK_ACTIVE=$(printf '%s' "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
  exit 0
fi

MISTAKES_FILE="${CLAUDE_PROJECT_DIR}/.claude/rules/mistakes.md"
if [ ! -f "$MISTAKES_FILE" ]; then
  exit 0
fi


MISTAKES=$(<"$MISTAKES_FILE")
jq -n --arg mistakes "$MISTAKES" '{
  decision: "block",
  reason: (
    "Before finishing, review your work against these known mistakes:\n"
    + $mistakes
    + "\nInspect the changes made during this turn and fix any repeated mistake before responding again."
  )
}'

