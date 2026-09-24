PROTECTED_BRANCHES="trunk main master"
SCAN_ROOT="${CLEANUP_SCAN_ROOT:-$HOME}"
SCAN_DEPTH="${CLEANUP_SCAN_DEPTH:-6}"
EXECUTE=0
NOW=$(date +%s)
DAY=86400

usage() {
  printf 'usage: %s [-e|--execute] [-h|--help]\n' "$(basename "$0")"
  printf '  default: dry run, print the classification table\n'
  printf '  -e, --execute: act on the classification, then print the table\n'
  printf '  env: CLEANUP_SCAN_ROOT (default $HOME), CLEANUP_SCAN_DEPTH (default 6)\n'
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      -e|--execute) EXECUTE=1 ;;
      -h|--help) usage; exit 0 ;;
      *) usage >&2; exit 2 ;;
    esac
    shift
  done
}

is_protected() {
  case " $PROTECTED_BRANCHES " in
    *" $1 "*) return 0 ;;
  esac
  return 1
}

find_repos() {
  find "$SCAN_ROOT" -maxdepth "$SCAN_DEPTH" \
    \( -name .git -type d -print -prune \) \
    -o \( \( -name '.*' -o -name Library -o -name node_modules \) -prune \) 2>/dev/null |
    sed 's|/\.git$||' | sort
}

list_worktrees() {
  local repo
  find_repos | while read -r repo; do
    git -C "$repo" worktree list --porcelain | awk -v repo="$repo" '
      /^worktree / { path = substr($0, 10); branch = "(detached)" }
      /^branch / { branch = substr($0, 8); sub("^refs/heads/", "", branch) }
      /^$/ { if (path != "") print repo "\t" path "\t" branch; path = "" }
      END { if (path != "") print repo "\t" path "\t" branch }'
  done
}

path_branch() {
  local dir="$1" wt
  case "$dir" in
    */.worktrees/*)
      wt="${dir%%/.worktrees/*}/.worktrees/$(printf '%s' "${dir#*/.worktrees/}" | cut -d/ -f1)"
      if [ -d "$wt" ]; then
        git -C "$wt" symbolic-ref -q --short HEAD || printf '(detached)'
      else
        printf '(missing worktree %s)' "$(basename "$wt")"
      fi
      return 0 ;;
  esac
  [ -d "$dir" ] || return 1
  git -C "$dir" rev-parse --show-toplevel >/dev/null 2>&1 || return 1
  git -C "$dir" symbolic-ref -q --short HEAD || printf '(detached)'
}

branch_verdict() {
  case "$1" in
    "(detached)") printf 'unclassified' ;;
    "(missing worktree"*) printf 'branch' ;;
    *) if is_protected "$1"; then printf 'keep'; else printf 'branch'; fi ;;
  esac
}

age_days() {
  printf '%s' $(( (NOW - $1) / DAY ))
}

print_table() {
  column -t -s "$(printf '\t')" "$1"
}

print_summary() {
  local file="$1" col="$2"
  printf '\n'
  tail -n +2 "$file" | awk -F '\t' -v c="$col" '{ n[$c]++ } END { for (k in n) printf "%s=%d  ", k, n[k]; print "" }'
  if [ "$EXECUTE" -eq 0 ]; then
    printf 'dry run: nothing changed. rerun with -e to act.\n'
  fi
}

tilde() {
  case "$1" in
    "$HOME"/*) printf '~%s' "${1#"$HOME"}" ;;
    *) printf '%s' "$1" ;;
  esac
}
