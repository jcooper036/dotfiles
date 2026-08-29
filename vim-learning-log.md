# Vim Learning Log

Reference for concepts learned. Use vim's native tools to look up specifics.

## Discovery Tools
- `<leader>kk` - Telescope keymaps (search for any command)
- `:help {topic}` - Built-in docs (the source of truth)
- `:map {key}` - See what a key does
- `:verbose map {key}` - See where a mapping was defined
- `:checkhealth lsp` - Diagnose why an LSP server isn't attached/running
- `:LspInfo` - Clients attached to current buffer (root dir, filetype match)
- `:lua vim.print(vim.lsp.get_clients())` - Raw list of all active LSP clients

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

### Search and Find
- `*` / `#` - Search forward/backward for word under cursor (whole word)
- `g*` / `g#` - Search forward/backward for word under cursor (partial match)
- `n` / `N` - Next/previous match
- `/pattern` - Search forward for pattern
- `?pattern` - Search backward for pattern
- **Search terms:** `:help *`, `:help g*`, `:help search-commands`

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

### Window Management
**Core concept:** Buffers are files in memory. Windows are viewports that display buffers.

**Navigation:**
- `<C-w>h/j/k/l` - Move between windows (vim directions)
- `<C-w>w` - Cycle through windows

**Closing:**
- `<C-w>c` or `:close` - Close window (keeps buffer alive)
- `<C-w>o` - Close all OTHER windows (only-one)
- `:bd` - Close buffer (closes all windows showing it)

**Splitting:**
- `<C-w>s` - Split horizontally
- `<C-w>v` - Split vertically

**Search terms:** `:help windows`, `:help CTRL-W`, `:help window-resize`

### Terminal Management
**Key concept:** A terminal is just a buffer in a window. All window/buffer commands (`<C-w>hjkl`, `<C-w>c`, `:bd`, `/`, `y`) work on it. The only new thing is terminal-mode, which swallows keystrokes.

**NvChad — new terms (spawn a fresh one each time):**
- `<leader>h` / `<leader>v` - new horizontal / vertical split terminal
- `<leader>pt` - Telescope pick a hidden term

**NvChad — toggleable terms (one persistent instance per id, keeps shell state):**
- `<A-h>` / `<A-v>` / `<A-i>` - toggle horizontal / vertical / floating terminal

**Escaping terminal mode:**
- `<C-x>` - NvChad default
- `<C-\><C-n>` - native Neovim

**Often you don't need a terminal at all:**
- `:!cmd` - run a command, no buffer
- `:r !cmd` - read command output into the buffer
- `:'<,'>!cmd` - filter a selection through a command
- **Search terms:** `:help terminal`, `:help terminal-input`, `:help CTRL-\_CTRL-N`, `:help :read!`

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
- `:jumps` - View jump list history
- **Key concept:** Jumps (like `gd`, `/`, `G`, `%`) add to jump list. Motions (like `j`, `w`, `{`) don't.
- **Search terms:** `:help marks`, `:help jumplist`, `:help jump-motions`

### Scrolling and Big Movements
- `Ctrl-d` / `Ctrl-u` - Down/Up half a page (most common)
- `Ctrl-f` / `Ctrl-b` - Forward/Back a full page
- `{number}j` / `{number}k` - Move exact line count (e.g., `10j`)
- `}` / `{` - Jump by paragraph (blank line separated)
- **Search terms:** `:help CTRL-D`, `:help scroll-cursor`, `:help {`

### Delete and Put Commands
- `x` - delete character under cursor (like Del)
- `X` - delete character before cursor (like Backspace)
- `s` - substitute character (delete + insert mode)
- `r{char}` - replace character with {char}
- `p` - put (paste) AFTER cursor / BELOW line
- `P` - put (paste) BEFORE cursor / ABOVE line
- **Key concept:** Linewise yanks (`dd`, `yy`) paste on new lines. Characterwise yanks (`yw`, `diw`) paste inline.
- **Search terms:** `:help x`, `:help p`, `:help P`

### Text Objects (Inner vs Around)
Operate on "the thing you're in" from anywhere in it. Pattern: `{operator}{i/a}{text-object}`
- `i` (inner) - the thing WITHOUT surrounding delimiters/whitespace
- `a` (around) - the thing WITH its delimiters/whitespace

**Common text objects:**
- `iw` / `aw` - inner/around word
- `i"` / `a"` - inside/around quotes (also works with `'` and `` ` ``)
- `i(` / `a(` - inside/around parens (also `i)` / `a)`)
- `i{` / `a{` - inside/around braces (also `i}` / `a}`)
- `i[` / `a[` - inside/around brackets (also `i]` / `a]`)
- `it` / `at` - inside/around HTML/XML tag
- `ip` / `ap` - inner/around paragraph

**Examples:**
- `ciw` - change whole word from anywhere in the word
- `di"` - delete text inside quotes (keep quotes)
- `da"` - delete text and the quotes
- `yip` - yank paragraph
- `vi{` - visually select inside braces

**Search terms:** `:help text-objects`, `:help iw`, `:help aw`

### Git Conflict Resolution in Vim
**Built-in navigation (no plugins):**
- `]c` / `[c` - Jump to next/previous diff hunk (in diffmode)
- `/<<<<<<` then `n`/`N` - Navigate between conflict markers

**Diffmode commands (`nvim -d file1 file2`):**
- `do` - Diff obtain (pull from other window)
- `dp` - Diff put (push to other window)
- `:diffupdate` - Refresh diff after manual edits

**Git mergetool workflow:**
- Configure: `git config --global merge.tool nvimdiff`
- Configure layout: `git config --global mergetool.nvimdiff.layout "LOCAL,MERGED,REMOTE"`
- After `git merge` with conflicts: run `git mergetool`
- Opens 3-pane view (LOCAL, MERGED, REMOTE) — edit MERGED pane
- Uses `]c`/`[c` + `do`/`dp` to resolve, `:wqa` to save and advance

**Search terms:** `:help diff-mode`, `:help do`, `:help dp`, `:help mergetool`

### Shell Filtering (`!`)
Pipe a range or visual selection through any shell command.
- `:'<,'>!sort` - sort selected lines
- `:'<,'>!sort -r` / `-u` / `-n` - reverse / unique / numeric sort
- `:'<,'>!uniq` - remove consecutive duplicates
- `:'<,'>!column -t` - align into columns
- **Key concept:** `!` turns vim into a pipeline — any Unix tool becomes a text transformation
- **Search terms:** `:help :!`, `:help filter`

### LSP References vs Project Text Search
Two different tools for "where else does this appear":
- `grr` - LSP references (Neovim 0.11+ built-in default, not an NvChad remap). Uses the language server, so it's accurate for renamed/reimported symbols.
- `gri` - LSP go to implementation
- `:Telescope grep_string` - ripgrep search defaulting to word under cursor (or visual selection if one is active). Plain text, not LSP-aware, but works across any file type.
- **Key concept:** No need to yank/select first for a single word — both tools read the word under the cursor directly, same as `*`.
- **Note:** `<leader>fw` in this config is `Telescope live_grep`, which opens an empty prompt (you type the pattern) — different from `grep_string`, which is not currently bound to a key.
- **Search terms:** `:help lsp-defaults`, `:help gO`, `telescope.builtin` docs for `grep_string`

### Mode-Scoped Keymaps (why `grr` broke in visual mode)
Keymaps are bound to specific modes. `grr` (LSP references) is normal-mode only.
- In visual mode, `r` is a different command entirely: "replace every selected char with the next key pressed."
- So `v w g r r` = enter visual → select word+ → `g` dead-ends (no visual `gr` command) → `r` starts visual-replace → final `r` is consumed as the replacement char → selection becomes all `r`s.
- **Key concept:** Lookup commands (`*`, `grr`, `gri`, `K`) are normal-mode and read the word under the cursor — no selection needed. Visual mode is for operating on (deleting/yanking/changing) a span, not for triggering lookups.
- **Search terms:** `:help v_r`, `:help map-modes`

### `vw` vs `viw`
- `vw` from word start selects through to the start of the NEXT word — drags trailing whitespace/punctuation along.
- `dw`/`cw` have a special-cased exception for this quirk; plain visual `v` + `w` does not.
- `viw` (inner word text object) selects exactly the word, nothing more — use this instead of `vw` when you want just the word.
- **Search terms:** `:help word-motions`, `:help iw`

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
