---
name: gh-create-issues-with-dependency
description: Use this whenever you are creating a Github issue that has a dependency on another Github issue or trying to determine if issues have dependencies.
---

# use the gh cli to set dependencies
The `gh issue` interface has a native way to handle dependencies - this is a new feature.

## add a dependendent issue on creation
Create issues in the dependcy chain order. Create non-blocked issues first. For creating blocked issues:
```bash
gh issue create <rest of arguments> --blocked-by <blocking issue number>
```

## checking if an issue has blockers
```bash
gh issue list <other args> --json blockedBy
```

## injecting an issue as a blocker of another issue
This should only be used if the issue chain is being resolved later, and a NEW dependency of a current issue is discovered. For example
- original creation: 10 -| 11 -| 12
- discovery: We need 13 to happen before 12, so 13 -| 12 as well

When creating D
```bash
gh issue create <rest of args for 13> --blocking 12
```

## use help when you don't know
The gh tool is evolving, so check how it works rather than assuming.

```bash
gh issue --help
gh issue create --help
gh issue list --help
```

