local plugins = {
  {
    "hrsh7th/nvim-cmp",
    opts = function()
      local cmp = require("cmp")

      -- Get NvChad's default config
      local default_opts = require("nvchad.configs.cmp")

      -- Override just the mappings
      default_opts.mapping["<Tab>"] = cmp.mapping.confirm({ select = true })
      default_opts.mapping["<C-n>"] = cmp.mapping.select_next_item()
      default_opts.mapping["<C-p>"] = cmp.mapping.select_prev_item()
      default_opts.mapping["<CR>"] = cmp.mapping({
        i = function(fallback)
          fallback()
        end,
      })

      return default_opts
    end,
  },

  {
    "tpope/vim-dadbod",
    lazy = false,
  },

  {
    "kristijanhusak/vim-dadbod-ui",
    dependencies = {
      { "tpope/vim-dadbod", lazy = true },
      { "kristijanhusak/vim-dadbod-completion", ft = { "sql", "mysql", "plsql" }, lazy = true },
    },
    cmd = {
      "DBUI",
      "DBUIToggle",
      "DBUIAddConnection",
      "DBUIFindBuffer",
    },
    init = function()
      vim.g.db_ui_use_nerd_fonts = 1

      vim.api.nvim_create_autocmd("FileType", {
        pattern = { "sql", "mysql", "plsql" },
        callback = function()
          require("cmp").setup.buffer { sources = { { name = "vim-dadbod-completion" } } }
        end,
      })
    end,
  },

  -- To make a plugin not be loaded
  -- {
  --   "NvChad/nvim-colorizer.lua",
  --   enabled = false
  -- },

  -- All NvChad plugins are lazy-loaded by default
  -- For a plugin to be loaded, you will need to set either `ft`, `cmd`, `keys`, `event`, or set `lazy = false`
  -- If you want a plugin to load on startup, add `lazy = false` to a plugin spec, for example
  -- {
  --   "mg979/vim-visual-multi",
  --   lazy = false,
  -- }
}

return plugins
