if [[ -r "${AGENT_TEAM_BOT_ORIGINAL_ZDOTDIR:-$HOME}/.zshenv" ]]; then
  source "${AGENT_TEAM_BOT_ORIGINAL_ZDOTDIR:-$HOME}/.zshenv"
fi
export ZDOTDIR="${AGENT_TEAM_BOT_ROOT:-$HOME/dotfiles/gh-agent-team-bot}/shell/zsh"
source "${AGENT_TEAM_BOT_ROOT:-$HOME/dotfiles/gh-agent-team-bot}/shell/activate.sh"
