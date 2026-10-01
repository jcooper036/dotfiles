_wt_paths() {
  git worktree list --porcelain | sed -n 's/^worktree //p'
}

_wt_main_root() {
  _wt_paths | head -n 1
}

_wt_branch_path() {
  git worktree list --porcelain |
    awk -v ref="branch refs/heads/$1" '/^worktree /{p = substr($0, 10)} $0 == ref {print p; exit}'
}

_wt_branch_known() {
  git show-ref --verify --quiet "refs/heads/$1" ||
    [[ -n $(git for-each-ref --count=1 --format=x "refs/remotes/*/$1") ]]
}

_wt_create() {
  local branch=$1 main dest
  main=$(_wt_main_root)
  dest=$main/.worktrees/$branch
  if _wt_branch_known "$branch"; then
    git worktree add "$dest" "$branch" >&2 || return
  else
    git worktree add -b "$branch" "$dest" >&2 || return
  fi
  git -C "$main" check-ignore -q .worktrees || print -u2 "gws: .worktrees is not git ignored in $main"
  print -r -- "$dest"
}

_wt_ensure() {
  local existing
  existing=$(_wt_branch_path "$1")
  [[ -n $existing ]] || existing=$(_wt_create "$1") || return
  print -r -- "$existing"
}

_wt_pick() {
  git worktree list --porcelain |
    awk '/^worktree /{p = substr($0, 10); b = "(detached)"} /^branch /{b = substr($0, 19)} /^$/{printf "%-40s\t%s\n", b, p}' |
    fzf --delimiter='\t' --preview='git -C {2} status -sb; echo; git -C {2} log --oneline --color=always -15' |
    cut -f2
}

_wt_dest() {
  local sub=$1/${2%/}
  [[ -n $2 && -d $sub ]] && print -r -- "$sub" || print -r -- "$1"
}

_wt_track_new() {
  local -a before after
  before=(${(f)"$(_wt_paths)"})
  "$@" || return
  after=(${(f)"$(_wt_paths)"})
  zoxide add ${after:|before}
}

gws() {
  local -a split
  zparseopts -D -E -F -- -split=split || return 1
  if (( $#split )) && [[ -z $1 || -z $TMUX ]]; then
    print -u2 "gws: --split needs a branch name and a tmux session"
    return 1
  fi
  local prefix root
  prefix=$(git rev-parse --show-prefix) || return 1
  if [[ -n $1 ]]; then
    root=$(_wt_ensure "$1") || return 1
  else
    root=$(_wt_pick)
  fi
  [[ -n $root ]] || return 1
  zoxide add "$root"
  local -a go=(cd)
  (( $#split )) && go=(tmux split-window -h -c)
  $go "$(_wt_dest "$root" "$prefix")"
}

gwr() {
  local prefix
  prefix=$(git rev-parse --show-prefix) || return 1
  cd "$(_wt_dest "$(_wt_main_root)" "$prefix")"
}

_gws_branches() {
  local -a branches
  branches=(${(f)"$(git for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null)"})
  compadd -a branches
}

_gws() {
  _arguments '--split[open the worktree in a new tmux pane]' '1:branch:_gws_branches'
}

compdef _gws gws
compdef _precommand _wt_track_new
