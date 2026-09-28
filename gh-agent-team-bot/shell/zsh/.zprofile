if [[ -r "${AGENT_TEAM_BOT_ORIGINAL_ZDOTDIR:-$HOME}/.zprofile" ]]; then
  source "${AGENT_TEAM_BOT_ORIGINAL_ZDOTDIR:-$HOME}/.zprofile"
fi
source "${AGENT_TEAM_BOT_ROOT:-$HOME/dotfiles/gh-agent-team-bot}/shell/activate.sh"
