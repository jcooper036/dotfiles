# Vim Learning Log

Reference for concepts learned. Use vim's native tools to look up specifics.

## Discovery Tools
- `<leader>kk` - Telescope keymaps (search for any command)
- `:help {topic}` - Built-in docs (the source of truth)
- `:map {key}` - See what a key does
- `:verbose map {key}` - See where a mapping was defined

---

## Concepts Covered

### Linewise vs Characterwise Yanking
How you select determines how `p` pastes.
- `V` = linewise → `p` pastes on new line
- `v` = characterwise → `p` pastes inline
- `:put` always pastes on a new line regardless
- **Search terms:** `:help linewise`, `:help characterwise`

### word vs WORD Motions
- `w`/`b`/`e` stop at punctuation/underscores
- `W`/`B`/`E` stop at whitespace only (treats `MONDAY_API_KEY` as one unit)
- **Search terms:** `:help word`, `:help WORD`

### f/t Motions (Find and Till)
For precise same-line jumps to known characters.
- `f{char}` - jump to character (inclusive)
- `t{char}` - jump till character (exclusive, stops before it)
- Combine with operators: `dt=`, `cf"`, `yt,`
- **Search terms:** `:help f`, `:help t`

### Shift + hjkl Commands
Not all are navigation:
- `H`/`M`/`L` - viewport Top/Middle/Bottom (navigation)
- `J` - Join lines (editing)
- `K` - Keyword lookup (documentation)
- **Search terms:** `:help H`, `:help J`, `:help K`

### Viewport Positioning (z commands)
Scroll window to reposition current line without moving cursor in file.
- `zt` / `zz` / `zb` - Top/Center/Bottom
- **Search terms:** `:help scroll-cursor`, `:help zt`

### Surround Plugin (nvim-surround)
Add, delete, change surrounding characters.
- `<leader>kk` → search "surround"
- **Search terms:** `:help nvim-surround`

### Find and Replace
- `:%s/old/new/g` - whole file
- `:%s/old/new/gc` - with confirmation
- Scopes: `%` = file, `'<,'>` = visual selection, `10,20` = line range
- **Search terms:** `:help :substitute`, `:help :s_flags`

### Macros
Recording keystrokes to replay.
- `q{register}` - start recording (e.g., `qd`)
- `q` - stop recording
- `@{register}` - replay (e.g., `@d`)
- **Search terms:** `:help recording`, `:help @`

### Insert Mode Escape Hatch
- `Ctrl-o` - execute ONE normal mode command, then return to insert
- Example: `Ctrl-o A"` appends quote at end of line without leaving insert
- **Search terms:** `:help i_CTRL-O`

### Ex Commands for Line Operations
- `:34put` - paste below line 34 (without moving cursor)
- `:34` - jump to line 34
- **Search terms:** `:help :put`, `:help :range`

### Buffer Management
- `:ls` - list buffers
- `:%bd` - close all buffers
- `:bd pattern*` - close buffers matching pattern
- **Search terms:** `:help :bdelete`, `:help :buffers`

### Terminal Management
- `<leader>v` / `<leader>h` / `<leader>i` - Toggle Vertical/Horizontal/Floating terminal
- `<C-x>` - Escape terminal mode to normal mode (NvChad default)
- `<C-\><C-n>` - Native Neovim escape terminal mode
- **Search terms:** `:help terminal`, `:help CTRL-\_CTRL-N`

### File Management (Creation)
- `:e filename` - Edit a new file (created on `:w`)
- `a` (inside NvimTree) - Create new file or directory (end with `/`)
- **Search terms:** `:help :edit`, `:help nvim-tree-mappings-default`

### Ranges and Whole File Operations
- `%` - Shortcut for "the whole file"
- `:%y` - Yank entire file without moving cursor
- `:%d` - Delete entire file
- `ggVG` - Select whole file in visual mode (useful if you *must* see it)
- **Search terms:** `:help :range`, `:help %`

### Marks and Jumps
- `mm` - Set mark 'm' at current cursor position
- `'m` - Jump back to line of mark 'm'
- `` `m `` - Jump back to exact position of mark 'm'
- `Ctrl-o` - Jump back in jump list (previous location)
- `Ctrl-i` - Jump forward in jump list
- **Search terms:** `:help marks`, `:help jumplist`

---

## Vim Thinking Patterns

1. **"Change what you want to replace"**
   Use `c` instead of delete + navigate + insert. `ct=` beats `dt=i`.

2. **Know your landmarks**
   `f` and `t` are surgical when you know the character you're targeting.

3. **Operators + Motions = Power**
   Any operator (`d`, `c`, `y`, `v`) combines with any motion (`w`, `W`, `f"`, `t=`, `i"`, `a{`).

4. **`:help` is your first lookup, not Google**
   Vim's docs are comprehensive. Learn the search terms.

5. **Linewise operations for lines, characterwise for text**
   Choose `V` vs `v` intentionally based on what you want to happen on paste.
