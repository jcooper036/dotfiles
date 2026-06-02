# Cursor configuration

Mirrors the Claude Code setup in `~/dotfiles/claude/`. Edit files here, then run `./setup.sh` to refresh symlinks under `~/.cursor/`.

## Layout

| Cursor path | Source | Claude equivalent |
|-------------|--------|-------------------|
| `~/.cursor/rules/jacob-core.mdc` | `rules/jacob-core.mdc` | `~/dotfiles/claude/CLAUDE_root.md` |
| `~/.cursor/skills/*` | `~/dotfiles/claude/skills/*` + `skills/*` | `~/.claude/skills` |
| `~/.cursor/agents/*.md` | `agents/*.md` | `~/.claude/agents` + `dotfiles/claude/agents` |
| `~/.cursor/hooks.json` | `hooks/hooks.json` | `~/.claude/settings.json` hooks |
| `~/.cursor/hooks/set-path.sh` | `hooks/set-path.sh` | `~/.claude/set-path.sh` |
| `~/.cursor/statusline.sh` | `statusline.sh` | `~/.claude/statusline.sh` |
| `~/.cursor/cli-config.json` | merged via `setup.sh` | `~/.claude/settings.json` |

## Setup

```bash
cd ~/dotfiles/cursor
./setup.sh
```

Restart the Cursor CLI after setup so `cli-config.json`, hooks, and status line changes load.

## Shared skills

Personal skills live in `~/dotfiles/claude/skills/` and are symlinked into both:

- `~/.claude/skills` (Claude Code)
- `~/.cursor/skills` (Cursor)

Cursor-only skills (e.g. migrated slash commands) go in `~/dotfiles/cursor/skills/`.

## Agents

Subagents in `agents/` are adapted from Claude Code subagents. Cursor uses a simpler frontmatter (`name`, `description` only); extra Claude fields are ignored.

- `gh-bot-debug` — GitHub App bot auth diagnostics
- `issue-solver` — monitor and fix autonomous GitHub issues
- `library-pr-reviewer` — review autonomous PRs on library repos

## Permissions

`cli-config.merge.json` is generated from `~/.claude/settings.json` + `settings.local.json` (Bash → Shell, WebFetch → domain allowlist). `setup.sh` merges it into `~/.cursor/cli-config.json` without touching model/auth caches.

## Project-level configs

Per-repo Claude files still apply in Claude Code:

- `CLAUDE.md` / `CLAUDE.local.md`
- `.claude/settings.local.json`

For Cursor projects, use:

- `.cursor/rules/` for file-scoped rules
- `.cursor/agents/` for repo-specific subagents
- `AGENTS.md` at repo root (Cursor also reads `CLAUDE.md` in many setups)

## Docs

- Cursor: https://cursor.com/docs
- Claude Code (shared concepts): https://code.claude.com/docs/en/settings
