---
name: codex-collaborator
description: Collaborate with Codex (OpenAI's codex CLI, default model gpt-6-astra) on a task over a multi-turn conversation held in one persistent Codex session. Use whenever the user asks to work with, pair with, consult, brainstorm with, or hand part of a task to Codex.
when_to_use: The user says "work with codex", "ask codex", "collaborate with codex", "get codex's take", "have codex do X", "pair with codex", or names codex / astra as a partner. For a one-shot adversarial review with structured findings, use outside-reviewer instead.
---

# Codex collaborator

Codex is a peer, not an oracle. Claude keeps the task, decides what to send, verifies what comes back, and reports to the user. One Codex session (thread) per collaboration, continued turn after turn so Codex keeps its own context.

## Talk through `scripts/codex-turn`
The script wraps `codex exec` (new thread) and `codex exec resume <thread_id>` (same thread), probes the binary and login, and keeps a transcript of every turn in the out dir.

```bash
SKILL=/Users/jacob/.claude/skills/codex-collaborator
OUT=<scratchpad>/codex/<topic>
$SKILL/scripts/codex-turn -o $OUT -C <repo-or-worktree> $OUT/msg.md
$SKILL/scripts/codex-turn -o $OUT -C <repo-or-worktree> -t "$(cat $OUT/thread_id)" $OUT/msg.md
```

- First line of output is `thread=<id> exit=<n> turn=<ts> out=<dir>`; Codex's reply follows. Trust the reply only on `exit=0`.
- Omit `-t` exactly once per collaboration. Every later turn passes `-t`, or Codex starts with no memory.
- Write each message to a file and pass the path. Do not inline prompts in the shell.
- Run with the Bash tool `timeout` at 600000. Long turns: `run_in_background` and wait for the notification. Never wrap in `timeout` (not installed).
- Never run two turns on one thread at once. Parallel work needs separate threads, each with its own out dir.
- Flags: `-m` model (default `gpt-6-astra`), `-e` reasoning effort (`low`|`medium`|`high`, default `medium`; `minimal` returns HTTP 400), `-s` sandbox for a new thread (default `read-only`).

## Sandbox is fixed at thread creation
Resume keeps the sandbox the thread started with. Decide before the first turn.
- `read-only`: discussion, design, review, investigation. The default.
- `workspace-write`: Codex edits files. Give it its own worktree under `<repo>/.worktrees/`, branched from Claude's branch, and pass that as `-C`. Claude merges the result after reviewing the diff.

## The first message carries the whole brief
Codex sees nothing of Claude's conversation. The opening turn states:
- the goal and the user's constraints
- Codex's role in this collaboration (critic, co-designer, implementer of a named piece)
- relevant paths, and what Claude has already done or ruled out
- the expected reply shape (short, plain prose, or a specific list)

Codex loads `~/.codex/AGENTS.md`, which links to the same global rules Claude follows. Do not restate them.

Later turns are short and refer back: "you proposed X; I tested it, it failed with <output>; what next".

## Verify, then relay
- Check Codex's factual claims about the code against the code before acting on them.
- Tell the user where Claude and Codex agree, disagree, and what Claude will do. Do not paste Codex replies as the answer.
- Give the user the thread id. They can open the same session with `codex resume <thread_id>` to read or join it.

## Transcript
Each turn writes `prompt-<ts>.md`, `reply-<ts>.md`, `events-<ts>.jsonl`, `stderr-<ts>.log` to the out dir, and `thread_id`. Point the user at these files rather than summarizing a failure. Codex's own rollout lives under `~/.codex/sessions/`, findable by `grep -rl <thread_id> ~/.codex/sessions`.
