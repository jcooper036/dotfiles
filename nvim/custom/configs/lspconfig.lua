local on_attach = require("nvchad.configs.lspconfig").on_attach
local capabilities = require("nvchad.configs.lspconfig").capabilities

-- 1. Get the list of ALL servers currently installed via Mason
local mason_lspconfig = require("mason-lspconfig")
local installed_servers = mason_lspconfig.get_installed_servers()

-- 2. Loop through the dynamic list instead of a hardcoded one
for _, lsp in ipairs(installed_servers) do
  vim.lsp.config(lsp, {
    on_attach = on_attach,
    capabilities = capabilities,
  })
  vim.lsp.enable(lsp)
end

