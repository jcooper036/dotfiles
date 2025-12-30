local C = {
  {
    modes = { "n" },
    keybind = "<leader>kk",
    mapping_info = "<cmd> Telescope keymaps <CR>",
    -- this is telling it to go in the Telescope category under Keymaps
    desc = "Telescope keymaps",
  },
  {
    modes = { "n" },
    keybind = ";",
    mapping_info = ":",
    desc = "enter command mode",
    opts = { nowait = true },
  },
  {
    modes = { "v" },
    keybind = ">",
    mapping_info = ">gv",
    desc = "indent",
  },
}

local map = vim.keymap.set

for _, mp in ipairs(C) do
  local opts = mp.opts or {}
  opts.desc = mp.desc
  map(mp.modes, mp.keybind, mp.mapping_info, opts)
end

return C
