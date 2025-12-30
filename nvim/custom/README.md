# Custom config for NvChad
Setting up custom nvim configurations from the NvChad base install. The objective:
- have a repeatable pattern for installing NvChad
- have a mostly seperate `custom` directory so that it is easy to see and take back changes that you have made.
Optimizing for being able to tear down and start from scatch with minimal hastle. It is certainly possible to just modify what NvChad gives you- but I'm not enough of a vim head and don't make modifications all that often, so it's useful to have a record of what I did so that it's easy to come back to in the future.

Neovim version 0.11.5


# Setup From scratch
I recommend deleting everything and starting from scratch

```bash
rm -rf ~/.config/nvim
rm -rf ~/.local/state/nvim
rm -rf ~/.local/share/nvim
brew upgrade nvim
```

Throwing in an `which nvim` and `nvim -v` can't hurt, just to make sure you know where things are coming from.

## 0, Nerd font installation
If you aren't already using one, you'll need a nerd for NvChad as this is where it will get special characters from. I'm using [RobotMono Nerd Font Mono, which you can find here](https://www.nerdfonts.com/font-downloads) along with many other options. After downloading and installing it, set your terminal to use it (for iTerm2 this is under Settings->Profile->Text->Font).

## 1. Install NvChad
Following instructions from https://nvchad.com/docs/quickstart/install

```bash
git clone https://github.com/NvChad/starter ~/.config/nvim && nvim
```
Once nvim opens, you'll get some installs. Then run `:MasonInstallAll` and `:Lazy sync`. Close and re-open vim.

Delete the .git folder
```bash
rm -rf ~/.config/nvim/.git
```

## 2. (Optional) Add the vim alias
Since I never want to use real vim, I set the vim command to alias nvim instead. Plus, `vi` still exists to use pure vim.
```bash
echo "# neovim alias\nalias vim='nvim'" >> .zshrc
```

## 3. Clone this repo
```bash
git clone git@github.com:jcooper036/my_nvim_config.git ~/.config/nvim/lua/custom
```
If all done correctly, you should have a `~/.config/nvim` that you can pull from NvChad, and a `~/.config/nvim/lua/custom` (which NvChad ignores) that you can pull from this repo.

## 4. Modify inits to pick up custom
In `init.lua` add this to the lazy.setup block
```lua
  { import = "custom.plugins"}
```
At then end of the same file, add:
```lua
  require "custom.mappings"
```

Next, head over to lua/plugins/init.lua. Replace it with
```lua
return {
  -- Override plugin definition options. We need to do this for any plugin that nvchad
  -- loads by default, which should just be lspconfig and conform
  {
    "neovim/nvim-lspconfig",
    dependencies = {
      "williamboman/mason.nvim",
      "williamboman/mason-lspconfig.nvim",
    },
    config = function()
      require "configs.lspconfig"
      require "custom.configs.lspconfig"
    end, -- Override to setup mason-lspconfig
  },
  {
    "stevearc/conform.nvim",
    -- event = 'BufWritePre', -- uncomment for format on save
    opts = { require "configs.conform", require "custom.configs.conform" },
  },
}
```
This shouldn't be much different than what is there - it's just adding the custom configs for the two plugins that NvChad requires.
After this point, all custom plugin configs should just be referenced in `lua/custom/plugins.lua`, so there should be no need to modify NvChad setup further. 

### Start nvim 
In the NvChad install you should have already loaded the base plugins there. Now, run `:Lazy sync` and that should install some plugins. You can also use `:MasonInstallAll` to make sure that plugins are installed as well.


## Did it work?
If everything has worked, `<leader> ch` should bring up the cheatsheet, and under General you should see two of the custom commands in there - Markdown Preview (`<leader> + mp`) and  the Telescope keymaps (`<leader> + fk`, this one is a real one in newer versions sometimes, but I found it inconsistent so I just put it there.).

There are some other things you can try, like :DBUI which should start the dadbod database UI utility. 

# Installing plugins
- modify `lua/custom/plugins.lua`

# Installing lsps
Install with Mason. The `lua/custom/configs/lspconfig.lua` module is set up to automatically pick up new lsps
