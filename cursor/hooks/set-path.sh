#!/bin/bash
# Prepend ~/.claude/bin so the gh bot wrapper is found before system gh.
# Mirrors ~/.claude/set-path.sh for Cursor sessionStart hooks.
export PATH="/Users/jacob.cooper/.claude/bin:${PATH}"
exit 0
