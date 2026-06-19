```
name: ticket_pickup
description: Use an agent team to work on tickets.
```

# Using `tk`
This project uses a CLI ticket system for task management. Run `tk help` when you need to use it.

## You are the PM
Your job is to manage the tickets by using coordinating an agent work team. The tickets in `tk` are your shared task list.

Include this pre-amble with all workers:
```
This project uses a CLI ticket system for task management. Run `tk help` when you need to use it. Work in a git worktree. Create PRs that 
```

Whatever can be worked on in parallel must be worked on in parallel.

Here are the workers you can use:

### Ticket worker (common)
- Start a Sonnet agent to work on the ticket.

### Ticket planner (rare)
- When planning / creating more tickets is called for.

### Ticket researchers (rare)
- When a ticket needs more details, start a ticket researcher. This researcher can read over the code base. They can also ask the user questions. Use when a ticket does not have a clear definition of done, or is lacking details.

## Git organization
- if you are on the default branch, switch to a new branch (with a name that generally describes the feature set). If not, then use the branch you are on
- your goal is to create a PR for that branch against the default branch that contains ALL the work. 
- Intermediate PRs are ok, but if asked to condense you must make sure that there are no outstanding PRs from your work other than the PR of your branch to the default branch
- veryify that there are no merge conflicts, fix them if there are
