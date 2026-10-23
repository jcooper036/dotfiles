# Git and github
- ALWAYS use the `gh` tool to interact with github

## git hygene
- ALWAYS work in worktrees
- ALL worktrees should be kept in .worktrees/ (in the project, not in the users folder)
- .worktrees should always be git ignored
- before doing any git operations, check what branch you are on
- never git add or git commit or git push to the "trunk" or "main" branch unless explicity approved to do so
- instead, if you find yourself on one of those branches, make a new worktree for the current changes first
- once PRs are merged, remove old worktrees

