local C = {
	{
		modes = { "n" },
		lhs = "<leader>kk",
		rhs = "<cmd> Telescope keymaps <CR>",
		-- this is telling it to go in the Telescope category under Keymaps
		opts = { desc = "Telescope keymaps" },
  },
	{
		modes = { "n" },
		lhs = ";",
		rhs = ":",
		opts = { desc = "enter command mode", nowait = true },
	},
	{
		modes = { "v" },
		lhs = ">",
		rhs = ">gv",
		opts = { desc = "indent" },
	},
	{
		modes = { "n" },
		lhs = "<leader>db",
		rhs = function()
			require("dap").toggle_breakpoint()
		end,
		opts = { desc = "DAP Toggle breakpoint" },
	},
	{
		modes = { "n" },
		lhs = "<leader>dc",
		rhs = function()
			require("dap").continue()
		end,
		opts = { desc = "DAP Start/contine debugging" },
	},
	{
		modes = { "n" },
		lhs = "<leader>dr",
		rhs = function()
			require("dap").run({
				type = "python",
				request = "launch",
				name = "Launch file",
				program = "${file}",
			})
		end,
		opts = { desc = "DAP Debug run current file" },
	},
	{
		modes = { "n" },
		lhs = "<leader>do",
		rhs = function()
			require("dap").step_over()
		end,
		opts = { desc = "DAP Step over" },
	},
	{
		modes = { "n" },
		lhs = "<leader>di",
		rhs = function()
			require("dap").step_into()
		end,
		opts = { desc = "DAP Step into" },
	},
	{
		modes = { "n" },
		lhs = "<leader>dO",
		rhs = function()
			require("dap").step_out()
		end,
		opts = { desc = "DAP Step out" },
	},
	{
		modes = { "n" },
		lhs = "<leader>dt",
		rhs = function()
			require("dap-python").test_method()
		end,
		opts = { desc = "DAP Debug run test method" },
	},
	{
		modes = { "n" },
		lhs = "<leader>dq",
		rhs = function()
			require("dap").terminate()
		end,
		opts = { desc = "DAP Terminate" },
	},
	{
		modes = { "n" },
		lhs = "<leader>du",
		rhs = function()
			require("dapui").toggle()
		end,
		opts = { desc = "DAP Toggle UI" },
	},
}

local map = vim.keymap.set

for _, mp in ipairs(C) do
	local opts = mp.opts or {}
	local ok, error = xpcall(function()
		map(mp.modes, mp.lhs, mp.rhs, opts)
	end, debug.traceback)
	if not ok then
		vim.notify(
			string.format("ERROR: Custom mapping failed for '%s': %s", vim.inspect(mp) or "unknwon", error),
			vim.log.levels.ERROR
		)
	end
end

return C
