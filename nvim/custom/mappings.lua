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
		lhs = "<lseader>db",
		rhs = function()
			require("dap").toggle_breakpoint()
		end,
		opts = { desc = "Toggle breakpoint" },
	},
	{
		modes = { "n" },
		lhs = "<leader>dc",
		rhs = function()
			require("dap").continue()
		end,
		opts = { desc = "Start/contine debugging" },
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
