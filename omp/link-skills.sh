#!/usr/bin/env bash
# Links skills into omp's skills dir (the hub), then exposes the hub to other agents:
# ~/.agents/skills links to the hub, and ~/.claude/skills gets one link per hub skill.
# Usage: link-skills.sh [<skill-dir>...]
set -euo pipefail

hub="$(omp config path)/skills"
claude_dir="$HOME/.claude/skills"
agents_link="$HOME/.agents/skills"
status=0

mkdir -p "$hub" "$claude_dir" "$(dirname "$agents_link")"

# Agent Skills wants the frontmatter `name:` to match the directory name.
skill_name() {
  local name
  name="$(awk '/^---[[:space:]]*$/ { n++; next } n == 1 && /^name:/ { sub(/^name:[[:space:]]*/, ""); gsub(/["\047[:space:]]/, ""); print; exit }' "$1/SKILL.md")"
  echo "${name:-$(basename "$1")}"
}

for arg in "$@"; do
  if [ ! -f "$arg/SKILL.md" ]; then
    echo "error    $arg has no SKILL.md" >&2
    status=1
    continue
  fi
  src="$(cd "$arg" && pwd -P)"
  case "$src" in
    */.worktrees/*)
      echo "error    $src is inside a worktree; link from the main checkout" >&2
      status=1
      continue
      ;;
  esac
  name="$(skill_name "$src")"
  dest="$hub/$name"
  if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then
    echo "ok       $name"
    continue
  fi
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    echo "error    $dest already exists; remove it to relink" >&2
    status=1
    continue
  fi
  ln -s "$src" "$dest"
  echo "linked   $name -> $src"
done

if [ "$(readlink "$agents_link" 2>/dev/null)" != "$hub" ]; then
  if [ -e "$agents_link" ] && [ ! -L "$agents_link" ]; then
    echo "error    $agents_link is a real directory; move its skills into $hub, then delete it" >&2
    exit 1
  fi
  rm -f "$agents_link"
  ln -s "$hub" "$agents_link"
  echo "linked   $agents_link -> $hub"
fi

# ~/.claude/skills stays a real directory: Claude Code keeps its own state there (synced/, .trash/).
for skill in "$hub"/*/; do
  name="$(basename "$skill")"
  dest="$claude_dir/$name"
  [ "$(readlink "$dest" 2>/dev/null)" = "$hub/$name" ] && continue
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    echo "error    $dest exists and is not a hub link; move it into $hub" >&2
    status=1
    continue
  fi
  ln -s "$hub/$name" "$dest"
  echo "mirrored $name"
done

for dest in "$claude_dir"/*; do
  [ -L "$dest" ] && [ ! -e "$dest" ] || continue
  case "$(readlink "$dest")" in
    "$hub"/*) rm "$dest" && echo "pruned   $(basename "$dest")" ;;
  esac
done

exit "$status"
