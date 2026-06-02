---
name: setup-ruff-autosave
description: Configure VS Code to use Ruff for Python formatting on autosave. Use when setting up Ruff format-on-save in a project.
disable-model-invocation: true
---

Edit the .vscode/settings.json file in the current project to configure Ruff as the Python formatter with format-on-save enabled. Add or update these settings:

```json
"[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
},
"ruff.format.args": [],
"ruff.lint.args": []
```

If the settings file doesn't exist, create it. If it exists but doesn't have these Ruff settings configured, add them. If they're already set up correctly, report that to the user.
