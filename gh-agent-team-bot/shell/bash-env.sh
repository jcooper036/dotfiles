if [ -n "${AGENT_TEAM_BOT_ORIGINAL_BASH_ENV:-}" ] && [ -r "$AGENT_TEAM_BOT_ORIGINAL_BASH_ENV" ]; then
  . "$AGENT_TEAM_BOT_ORIGINAL_BASH_ENV"
fi
. "${AGENT_TEAM_BOT_ROOT:-$HOME/dotfiles/gh-agent-team-bot}/shell/activate.sh"
