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

# dotfiles
The user uses ~/dotfiles to store configs for different tools
- vim
- ghostty
- omp
- zsh

Through a pattern of symlinking, they pass configs from here to other places

Dotfiles is a personal repo, and it services different machines with different purposes. Do not commit work content here, no link work content there.

