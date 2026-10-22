#!/usr/bin/env bash
# Links omp/config/* into omp's agent dir and seeds config.yml from omp/defaults/.
# Usage: install.sh [--reset-config]
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
agent_dir="$(omp config path)"
stamp="$(date +%Y%m%d-%H%M%S)"

reset_config=false
case "${1:-}" in
  "") ;;
  --reset-config) reset_config=true ;;
  *) echo "usage: $0 [--reset-config]" >&2; exit 2 ;;
esac

mkdir -p "$agent_dir"

for src in "$repo_dir"/config/*; do
  [ -e "$src" ] || continue
  name="$(basename "$src")"
  dest="$agent_dir/$name"
  if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then
    echo "ok       $name"
    continue
  fi
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    mv "$dest" "$dest.bak-$stamp"
    echo "backup   $name -> $name.bak-$stamp"
  fi
  ln -s "$src" "$dest"
  echo "linked   $name"
done

for src in "$repo_dir"/defaults/*; do
  [ -e "$src" ] || continue
  name="$(basename "$src")"
  dest="$agent_dir/$name"
  if [ -e "$dest" ] && [ "$reset_config" = false ]; then
    echo "kept     $name (--reset-config to overwrite)"
    continue
  fi
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    mv "$dest" "$dest.bak-$stamp"
    echo "backup   $name -> $name.bak-$stamp"
  fi
  cp "$src" "$dest"
  echo "copied   $name"
done
