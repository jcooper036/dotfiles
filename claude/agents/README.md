# Vigilant Watch Agent

A Claude Code subagent that monitors GitHub repository issues and automatically creates PRs to fix issues labeled `autonomous` that don't yet have open PRs.

PRs are attributed to **Brother Claudius of the Nominations Chapter**.

## Setup

The agent runs with `permissionMode: dontAsk`, which auto-denies any Bash command not explicitly pre-approved. To grant it the specific `git` and `gh` commands it needs, copy the `settings.local.json` from this directory into the `.claude/` directory of the repository you want the agent to monitor:

```bash
cp ~/dotfiles/claude/agents/settings.local.json <your-repo>/.claude/settings.local.json
```

`settings.local.json` is project-scoped and typically gitignored, so it won't affect other users or other projects.

## Allowed commands

The settings file grants permission for:

| Tool | Commands |
|------|----------|
| `git` | `ls-remote`, `checkout`, `pull`, `push`, `remote`, `branch`, `add`, `commit`, `worktree`, `status`, `diff`, `log`, `rev-parse`, `fetch` |
| `gh` | `auth status`, `issue list`, `issue comment`, `issue close`, `pr list`, `pr create` |
| other | `pwd` |

## Usage

From the target repository (with `settings.local.json` in `.claude/`):

```
@"vigilant-watch (agent)"
```

Or on a recurring schedule:

```
/loop 5m @"vigilant-watch (agent)"
```
