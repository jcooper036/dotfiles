# path
export PATH="/opt/homebrew/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH=".:$PYTHONPATH/Users/$USER"
export LOG_LEVEL='INFO'

# load compinit
autoload -Uz compinit && compinit

# zoxide
eval "$(zoxide init zsh)"

# uv
eval "$(uv generate-shell-completion zsh)"

# aliases
alias python='python3'
alias pip='pip3'
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

# shell integration
source ~/.iterm2_shell_integration.zsh

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
