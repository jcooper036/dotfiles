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
					require("cmp").setup.buffer({ sources = { { name = "vim-dadbod-completion" } } })
				end,
			})
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
		-- TODO lazy load via keys or commands
	},
	-- Python adaptor
	{
		"mfussenegger/nvim-dap-python",
		ft = "python",
		dependencies = { "mfussenegger/nvim-dap" },
		config = function()
			require("dap-python").setup("python") -- uses project's venv
		end,
	},
	-- debugger UI
	{
		"rcarriga/nvim-dap-ui",
		dependencies = { "mfussenegger/nvim-dap", "nvim-neotest/nvim-nio" },
		config = function()
			local dap, dapui = require("dap"), require("dapui")
			dapui.setup()
			-- Auto-open UI when debugging starts
			dap.listeners.after.event_initialized["dapui_config"] = function()
				dapui.open()
			end
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
