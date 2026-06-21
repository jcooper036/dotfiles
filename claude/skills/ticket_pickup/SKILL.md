```
name: ticket_pickup
description: Use an agent team to work on tickets.
```

# Using `tk`
This project uses a CLI ticket system for task management. Run `tk help` when you need to use it.
- `tk ls --status=open` tells you all the tickets that need to be completed
- `tk ready` tells you what can be done (based on dependencies)
- there are other useful commmands to examine dependencies

**IMPORTANT** `tk ls` without filters is not good, since it shows all previous tickets it is a distraction.

## Git organization
- after examining the tickets CREATE A WORKTREE BRANCH using the convention <one-or-two-word-summary>-tickets. This is your "integration branch". It should be created from trunk
    - ex for milestone 9 work 
```bash
git worktrees m9-work-tickets .claude/worktrees/m9-work-tickets trunk
```
- All work that your teammates create should be merged to this branch, and you are the sole arbiter of this branch.
- your goal is to create a PR for that branch against the default branch (trunk) that contains ALL the work. 
- verify that there are no merge conflicts, fix them if there are

## You are the PM / Lead Engineer
Your job is to manage the tickets by using coordinating an agent work team. The tickets in `tk` are your shared task list.

As PM you are explicitly authorized to:
- Push the integration branch to origin at any time
- Delete merged sub-branches and their worktree after merging

## Your pattern
- Use `tk ls --status=open` to get the full scope of tickets to be completed
- Use `tk ready` to find that workers can be assigned
- Whatever can be worked on in parallel must be worked on in parallel.
- When they are complete, check that ticket statuses have been handled correctly (the workers actually closed their tickets)

### Ticket worker
- Start a Sonnet agent to work on a specific ticket
- Include this pre-amble with all workers (providing the ticket ID for them):
```
This project uses a CLI ticket system for task management. Run `tk help` when you need to use it. You are being given a specific ticket, claim it with `tk start <id>`. Work in a git worktree. Do not create PRs - instead, 1) close the ticket with `tk close <id>`, 2) report to your parent agent that you are done, and ask them to merge your worktree into their work branch.

IMPORTANT: `tk` modifies ticket files in whatever working directory it runs from. You MUST run all `tk` commands (tk start, tk close, etc.) from inside your worktree — never from the main repo root — so ticket status changes land on your branch, not on trunk.

Ticket ID: <ticket_id>
```

**IMPORTANT (PM):** After merging each worker branch, verify the ticket file status was actually committed inside the merge (check with `git show HEAD --stat | grep tickets`). Workers frequently forget to commit ticket status changes or run `tk` from the wrong directory. If any tickets still show `open` or `in_progress` after their work is merged, update them yourself from inside the integration branch worktree, then commit.

## Completion checklist
- All open tickets have been handled (`tk list --status=open` returns nothing)
- All worker work has been merged back into your integration branch
- All worktrees created by workers have been removed and pruned
- All ticket statuses are up to date.
- Run `cargo test` and verify that all tests pass
- Writen a single PR that details the groups of tickets that were handled. This is the only PR the user reviews

