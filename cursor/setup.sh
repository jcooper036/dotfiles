#!/usr/bin/env bash
set -euo pipefail

CURSOR="$HOME/.cursor"
DOTFILES_CURSOR="$HOME/dotfiles/cursor"
DOTFILES_CLAUDE="$HOME/dotfiles/claude"

link_file() {
  local src="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  ln -sfn "$src" "$dest"
  echo "linked $dest -> $src"
}

link_dir_entries() {
  local src_glob="$1" dest_dir="$2"
  mkdir -p "$dest_dir"
  for entry in $src_glob; do
    [[ -e "$entry" ]] || continue
    ln -sfn "$entry" "$dest_dir/$(basename "$entry")"
    echo "linked $dest_dir/$(basename "$entry") -> $entry"
  done
}

echo "== Cursor adopt setup =="

mkdir -p "$CURSOR/rules" "$CURSOR/agents" "$CURSOR/hooks" "$CURSOR/skills"

link_file "$DOTFILES_CURSOR/rules/jacob-core.mdc" "$CURSOR/rules/jacob-core.mdc"
link_dir_entries "$DOTFILES_CLAUDE/skills/*" "$CURSOR/skills"
link_dir_entries "$DOTFILES_CURSOR/skills/*" "$CURSOR/skills"
link_dir_entries "$DOTFILES_CURSOR/agents/*.md" "$CURSOR/agents"

link_file "$DOTFILES_CURSOR/hooks/hooks.json" "$CURSOR/hooks.json"
link_file "$DOTFILES_CURSOR/hooks/set-path.sh" "$CURSOR/hooks/set-path.sh"
link_file "$DOTFILES_CURSOR/statusline.sh" "$CURSOR/statusline.sh"

chmod +x "$DOTFILES_CURSOR/hooks/set-path.sh" "$DOTFILES_CURSOR/statusline.sh"

python3 << 'PY'
import json
from pathlib import Path

cursor_config = Path.home() / ".cursor" / "cli-config.json"
merge = Path.home() / "dotfiles" / "cursor" / "cli-config.merge.json"

config = json.loads(cursor_config.read_text())
overlay = json.loads(merge.read_text())

config["permissions"] = overlay["permissions"]
config["approvalMode"] = overlay["approvalMode"]
config["sandbox"] = overlay["sandbox"]
config["webFetchDomainAllowlist"] = overlay["webFetchDomainAllowlist"]
config["statusLine"] = {
    "type": "command",
    "command": "~/.cursor/statusline.sh",
    "padding": 2,
}

cursor_config.write_text(json.dumps(config, indent=2) + "\n")
print(f"merged permissions into {cursor_config}")
PY

echo "Done. Restart Cursor CLI for hooks/statusline/cli-config to take effect."
