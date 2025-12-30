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
