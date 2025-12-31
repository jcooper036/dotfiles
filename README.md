# dotfiles
Config files for syncing across machines

# setup
## STEP 0 - Get brew and some dependencies set up
Install Homebrew using their directions: https://brew.sh/

There are two things to install to make sure brew is up and running.  
- `uv` is the python manager from astral (https://docs.astral.sh/uv/) and 
- `eza` is a long term project extension of exa, which is an ls augment (https://github.com/z-shell/zsh-eza). 
- `starship` is the terminal customization tool (replacement for powerlevel10K which is not being developed anymore). 
- `zoxide` is a navigation tool with memory, far supperior to cd (https://github.com/ajeetdsouza/zoxide). 
```zsh
brew install uv
brew install eza
brew install starship
brew install zoxide
brew install nvim
```

## Bring in this repo 
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

# nvim
Custom nvim configuration built on NvChad starter. Install NvChad from scratch, then symlink in the custom configs from this repo.

## Setup
### 1. Install NvChad starter
```bash
git clone https://github.com/NvChad/starter ~/.config/nvim && nvim
```
Run `:MasonInstallAll` and `:Lazy sync`, then close nvim.

### 2. Replace starter files with dotfiles symlinks
NvChad's starter includes `init.lua` and `lua/plugins/init.lua`. We make minimal modifications to these files to point at our `custom/` directory, which keeps the majority of customization in one place without disrupting the starter base. Replace the starter files with symlinks to our modified versions:

```bash
rm -rf ~/.config/nvim/.git
rm ~/.config/nvim/init.lua
rm ~/.config/nvim/lua/plugins/init.lua
ln -s ~/dotfiles/nvim/custom ~/.config/nvim/lua/custom
ln -s ~/dotfiles/nvim/init.lua ~/.config/nvim/init.lua
ln -s ~/dotfiles/nvim/plugins-init.lua ~/.config/nvim/lua/plugins/init.lua
```

### 3. Install plugins
```bash
nvim
# Then run :Lazy sync and :MasonInstallAll
```

