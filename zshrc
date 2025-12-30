# path
export PATH="/opt/homebrew/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH=".:$PYTHONPATH/Users/$USER"

# logging config
export LOG_LEVEL='INFO'

# load compinit
autoload -Uz compinit && compinit

# zoxide https://github.com/ajeetdsouza/zoxide
eval "$(zoxide init zsh)"

# fuzzyfinder https://github.com/junegunn/fzf#installation
source <(fzf --zsh)

# starship https://starship.rs/guide/
export STARSHIP_CONFIG="$HOME/dotfiles/starship.toml"
eval "$(starship init zsh)"

# uv
eval "$(uv generate-shell-completion zsh)"

# aliases
alias python='uv run python'
alias vim='nvim'
alias zrc='nvim ~/.zshrc'
alias commit='git commit'
alias push='git push'
alias pull='git pull'
alias checkout='git checkout'
alias cug="git checkout trunk;git pull"
alias pyt='if command -v uv >/dev/null; then uv run pytest; else pytest; fi'
function py() {
    uv run $1
}

# secrets
alias secret_load='load_secrets'
alias secret_add='vim $HOME/.secrets/misc.sh'
# load secrets if the file exists
function load_secrets() {
  if [[ -d "$HOME/.secrets" ]]; then
    for file in "$HOME/.secrets"/*(N.); do
      source "$file"
    done
  fi
}
# call the loader
load_secrets

# activate venv autmomatically on switching directories
function auto_venv_switch() {
    # 1. Check if .venv directory exists in the current folder
    if [[ -d ".venv" ]]; then
        # Only activate if it isn't already active (prevents redundant sourcing)
        if [[ "$VIRTUAL_ENV" != "$PWD/.venv" ]]; then
            # If a different venv is active, deactivate it first quietly
            if [[ -n "$VIRTUAL_ENV" ]]; then
                deactivate
            fi
            source .venv/bin/activate
        fi
    
    # 2. If no .venv exists here, but we are currently in one, deactivate it
    elif [[ -n "$VIRTUAL_ENV" ]]; then
        deactivate
    fi
}

# Load the add-zsh-hook utility
autoload -U add-zsh-hook

# Register the function to run on directory changes
add-zsh-hook chpwd auto_venv_switch

# Run it once immediately (so it works when you first open the terminal)
auto_venv_switch

# The next line updates PATH for the Google Cloud SDK.
if [ -f '/Users/jacobcooper/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/jacobcooper/google-cloud-sdk/path.zsh.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/Users/jacobcooper/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/jacobcooper/google-cloud-sdk/completion.zsh.inc'; fi

# NVM config
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Machine-specific config (not in git)
[ -f ~/.zshrc.local ] && source ~/.zshrc.local

# added since last time
