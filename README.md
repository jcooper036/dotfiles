# dotfiles
Config files for syncing across machines

# setup
Clone this repo
```bash
git clone git@github.com:jcooper036/dotfiles.git ~/dotfiles
```

# zshrc
Symlink the zshrc file
```bash
ln -s ~/dotfiles/zshrc ~/.zshrc
touch ~/.zshrc.local
```
This config will always load first, and at the end it attempts to load ~/.zshrc.local


# starship_config
The goal is just to have a portable config that I can use for any machine. This is for zsh

## Setup
This assumes that you are using the `zshrc` that is also in this repo, which automatically points the startship config at this location.
### 1. Make sure a Nerd Font is installed and in use
- Nerd Font: https://www.nerdfonts.com/
- In iterm2, that is Settings->Profile->Text->Font
- Use FiraCode Nerd Mono if nothing else
### 2. Install starship
[Install starship rs](https://starship.rs/installing/)
Probably just
```bash
brew install starship
```

