-- Custom options for neovim
local opt = vim.opt

-- Line wrapping
opt.wrap = true -- Enable line wrapping
opt.linebreak = true -- Break lines at word boundaries
opt.breakindent = true -- Preserve indentation in wrapped lines
opt.showbreak = "↪ " -- Show symbol at start of wrapped lines

-- Configure LSP diagnostics to handle long messages better
-- Virtual text doesn't support wrapping, so we show just severity icon inline
vim.diagnostic.config({
  virtual_text = {
    prefix = "■", -- Just show an icon, not the full message
    format = function(diagnostic)
      return "" -- Empty string = just show the icon prefix
    end,
  },
  float = {
    source = "always", -- Show source in floating window
    border = "rounded",
    wrap = true, -- Enable wrapping in float window
    max_width = 100,
  },
  signs = true, -- Show signs in gutter
  underline = true,
  update_in_insert = false,
  severity_sort = true,
})

-- Auto-show diagnostic float on cursor hold (after 500ms by default)
vim.api.nvim_create_autocmd("CursorHold", {
  callback = function()
    vim.diagnostic.open_float(nil, { focusable = false })
  end,
})
