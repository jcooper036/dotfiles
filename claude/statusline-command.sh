#!/usr/bin/env bash
input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // "Claude"')
cwd=$(echo "$input" | jq -r '.cwd // .workspace.current_dir // "~"')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

build_bar() {
  local pct="${1:-0}"
  local filled=$(( pct * 10 / 100 ))
  local bar=""
  for i in $(seq 1 10); do
    if [ "$i" -le "$filled" ]; then
      bar="${bar}█"
    else
      bar="${bar}░"
    fi
  done
  echo "$bar"
}

format_reset() {
  local resets_at="$1"
  local now
  now=$(date +%s)
  local diff=$(( resets_at - now ))
  if [ "$diff" -le 0 ]; then
    echo "now"
  else
    local hours=$(( diff / 3600 ))
    local mins=$(( (diff % 3600) / 60 ))
    if [ "$hours" -gt 0 ]; then
      echo "${hours}h${mins}m"
    else
      echo "${mins}m"
    fi
  fi
}

wt_session_name=$(echo "$input" | jq -r '.worktree.name // empty')
wt_session_path=$(echo "$input" | jq -r '.worktree.path // empty')
wt_linked_name=$(echo "$input" | jq -r '.workspace.git_worktree // empty')

if [ -n "$wt_session_name" ]; then
  if [ -n "$wt_session_path" ]; then
    dir_display=$(echo "$wt_session_path" | sed "s|$HOME|~|")
  else
    dir_display=$(echo "$cwd" | sed "s|$HOME|~|")
  fi
  git_part="(wt) $wt_session_name"
elif [ -n "$wt_linked_name" ]; then
  dir_display=$(echo "$cwd" | sed "s|$HOME|~|")
  git_part="(wt) $wt_linked_name"
else
  dir_display=$(echo "$cwd" | sed "s|$HOME|~|")
  branch=$(git -C "$cwd" branch --show-current 2>/dev/null)
  if [ -n "$branch" ]; then
    git_part="(br) $branch"
  else
    git_part=""
  fi
fi

if [ -n "$used_pct" ]; then
  used_int=$(printf "%.0f" "$used_pct")
  remaining_int=$(( 100 - used_int ))
  bar=$(build_bar "$used_int")
  ctx_part="ctx [${bar}] ${remaining_int}% left"
else
  ctx_part="ctx [----------] --% left"
fi

five_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
five_resets=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
week_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
week_resets=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

limits_part=""
if [ -n "$five_pct" ] && [ -n "$five_resets" ]; then
  five_int=$(printf "%.0f" "$five_pct")
  five_reset_str=$(format_reset "$five_resets")
  limits_part="5h: ${five_int}% (resets ${five_reset_str})"
fi
if [ -n "$week_pct" ] && [ -n "$week_resets" ]; then
  week_int=$(printf "%.0f" "$week_pct")
  week_reset_str=$(format_reset "$week_resets")
  week_str="7d: ${week_int}% (resets ${week_reset_str})"
  if [ -n "$limits_part" ]; then
    limits_part="${limits_part}  |  ${week_str}"
  else
    limits_part="$week_str"
  fi
fi

if [ -n "$git_part" ]; then
  dir_and_git="${dir_display}  ${git_part}"
else
  dir_and_git="$dir_display"
fi

if [ -n "$limits_part" ]; then
  printf "%s  |  %s  |  %s  |  %s" "$model" "$dir_and_git" "$ctx_part" "$limits_part"
else
  printf "%s  |  %s  |  %s" "$model" "$dir_and_git" "$ctx_part"
fi
