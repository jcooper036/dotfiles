local plugins = {
	{
		"williamboman/mason.nvim",
		opts = require("custom.configs.overrides").mason,
	},

	{
		"nvim-treesitter/nvim-treesitter",
		opts = require("custom.configs.overrides").treesitter,
	},

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
					-- Add dadbod next to the default sources; replacing them would drop LSP completion.
					local cmp = require("cmp")
					local sources = vim.deepcopy(cmp.get_config().sources)
					table.insert(sources, 1, { name = "vim-dadbod-completion" })
					cmp.setup.buffer({ sources = sources })
				end,
			})
		end,
	},

	-- BigQuery language server client. Installed everywhere but inert until
	-- `vim.lsp.enable("bqls")` runs in the machine-local lua/local.lua (see README).
	{
		"kitagry/bqls.nvim",
		commit = "082e6c0ead00a28df51115577b1367309c519c56",
		ft = "sql",
		dependencies = { "neovim/nvim-lspconfig" },
		init = function()
			vim.api.nvim_create_autocmd("LspAttach", {
				callback = function(args)
					local client = vim.lsp.get_client_by_id(args.data.client_id)
					if not client or client.name ~= "bqls" then
						return
					end
					vim.keymap.set("n", "<leader>qr", function()
						vim.lsp.buf.code_action({
							apply = true,
							filter = function(action)
								return action.title == "Execute Query"
							end,
						})
					end, { buffer = args.buf, desc = "BigQuery run query" })
					-- bqls dry-runs on didSave, using its in-memory copy of the buffer, so nothing is written.
					vim.keymap.set("n", "<leader>qd", function()
						client:notify("textDocument/didSave", { textDocument = { uri = vim.uri_from_bufnr(args.buf) } })
					end, { buffer = args.buf, desc = "BigQuery dry run" })
				end,
			})
		end,
		-- The server version is pinned in the script, not by this plugin's own install.sh.
		build = function(plugin)
			local script = vim.fn.stdpath("config") .. "/lua/custom/bin/install-bqls.sh"
			local out = vim.system({ script, plugin.dir .. "/bin" }, { text = true }):wait()
			if out.code ~= 0 then
				error(out.stderr)
			end
		end,
	},

	{
		"kylechui/nvim-surround",
		version = "*",
		event = "VeryLazy",
		config = function()
			require("nvim-surround").setup({})
		end,
	},
	{
		"iamcco/markdown-preview.nvim",
		cmd = { "MarkdownPreviewToggle", "MarkdownPreview", "MarkdownPreviewStop" },
		ft = { "markdown" },
		build = "cd app && ./install.sh",
	},
	-- Core Dap
	{
		"mfussenegger/nvim-dap",
		dependencies = {
			"rcarriga/nvim-dap-ui",
			"nvim-neotest/nvim-nio",
		},
		config = function()
			local dap, dapui = require("dap"), require("dapui")
			dapui.setup()
			-- Auto open/close UI
			dap.listeners.after.event_initialized["dapui_config"] = function()
				dapui.open()
			end
			dap.listeners.after.event_terminated["dapui_config"] = function()
				dapui.close()
			end
			dap.listeners.before.event_exited["dapui_config"] = function()
				dapui.close()
			end
		end,
	},
	-- Python adaptor
	{
		"mfussenegger/nvim-dap-python",
		ft = "python",
		dependencies = { "mfussenegger/nvim-dap" },
		config = function()
			local dap = require("dap")
			local dappython = require("dap-python")
			dappython.setup("python")

			table.insert(dap.configurations.python, {
				type = "python",
				request = "launch",
				name = "Python: Launch with Root",
				program = "${file}",
				cwd = vim.fn.getcwd(),
				env = {
					PYTHONPATH = vim.fn.getcwd(),
				},
				console = "integratedTerminal",
			})
		end,
	},
	-- Inline variable values with debugger
	{
		"theHamsta/nvim-dap-virtual-text",
		dependencies = { "mfussenegger/nvim-dap" },
		config = function()
			require("nvim-dap-virtual-text").setup()
		end,
	},
}

return plugins
