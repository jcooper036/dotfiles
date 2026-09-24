---
name: cleanup
description: Audit and clean the machine of leftover branch work — git branches and worktrees in every repo under ~, docker containers / networks / images built from branches, and listening processes started from branches. Only trunk and main survive. Use when asked to clean up the system, prune branches or worktrees, clear out branch containers, free ports held by branch services, or run cleanup-git / cleanup-docker / cleanup-processes.
---

# cleanup

Three scripts in `scripts/` (next to this file), aliased in zsh as `cleanup-git`, `cleanup-docker`, `cleanup-processes`. Each prints a classification table and changes nothing unless passed `-e` / `--execute`. With `-e` it acts on the same classification and prints the table with the outcome in `ACTION`.

## Run order: processes, docker, git

Services are stopped before the worktrees they run from are removed. Docker and process classification also resolve `.worktrees/<name>` paths, which reads best while those worktrees still exist.

## Procedure

For each script, in order:

1. Run it without `-e`.
2. Read every row that will act (`ACTION` is `delete`, `remove` or `stop`) and check it against the category definitions below. A row whose `REASON` does not justify its category is a leak: do not run `-e`; report the row to the user instead.
3. If nothing leaked, run it with `-e`.
4. Collect `unclassified` rows, `FAILED` actions, and `still running after SIGTERM` lines for the report.

Never act on an `unclassified` row yourself. Those are the user's decision.

## Categories

### cleanup-git

Scans every git repo under `$HOME` (depth 6, skipping dot-dirs, `Library`, `node_modules`). `trunk`, `main`, `master`, and the repo's `origin/HEAD` branch are never listed. Deletion is local only: `git worktree remove` then `git branch -D`. Remote branches are never touched.

| category | meaning | action |
|---|---|---|
| completed | PR merged or closed, no local work beyond it | delete |
| stale | no PR and last commit over 14 days old, or no commits beyond trunk and untouched for a day | delete |
| abandoned | unpushed commits or uncommitted changes, last edited over 3 days ago | delete (`--force`) |
| in_progress | open PR, or recent activity | none |
| unclassified | open PR idle over 14 days; recent local work after the PR resolved; unmerged work in a repo with no remote; checked out in the primary worktree; PR lookup failed; stray or detached worktree | none |

Repos with no remote cannot be checked for PRs or unpushed work, so unmerged branches there go to `unclassified` rather than `abandoned` or `stale`.

### cleanup-docker

Traces containers, compose networks and compose-built images to a branch through the compose labels `working_dir` (preferred) or project name matched against worktree folder names. Pulled images (postgres, prefect, ...) have no compose label and are never listed or removed. Volumes are not touched.

| category | meaning | action |
|---|---|---|
| branch | traced to a non-trunk branch, or to a `.worktrees/` path that no longer exists | stop, rm / network rm / rmi |
| keep | traced to trunk / main, or image tagged `trunk` | none |
| unclassified | no compose labels, or project matches no repo or worktree | none |

### cleanup-processes

Every TCP listener owned by the user, traced to a branch through a `.worktrees/` path in its command line, else its cwd. Stopping is SIGTERM only; survivors are listed after a 3s grace period, never SIGKILLed. The script's own ancestors (the agent's shell, the agent) are always kept.

| category | meaning | action |
|---|---|---|
| branch | running from a non-trunk checkout | SIGTERM |
| keep | running from trunk / main | none |
| other | not running from a git checkout | none |
| unclassified | running from a detached HEAD | none |

## Report to the user

- Counts per script of what was deleted / removed / stopped.
- Every `unclassified` row, grouped by reason, with the path or name the user needs to act on.
- Every `FAILED` action and SIGTERM survivor, verbatim.
- Any row you held back as a leak, and why.
