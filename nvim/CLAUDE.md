# nvim configuration

This directory contains custom neovim configuration built on NvChad starter.

## Structure
- `init.lua` - Main entry point, loads base NvChad and custom configs
- `plugins-init.lua` - Plugin initialization
- `custom/` - All custom configurations (plugins, mappings, options, LSP configs)

## Change Log

### 2026-01-07 - LSP Diagnostic Display
**Problem:** LSP diagnostic virtual text extended off-screen and couldn't be read

**Solution:** Virtual text in Neovim doesn't support multi-line wrapping (API limitation). Implemented auto-popup diagnostics instead:
- `custom/options.lua` - Created with diagnostic config showing minimal inline icons and auto-popup full messages on cursor hold
- `custom/mappings.lua` - Added `gl` keybinding to manually trigger diagnostic float
- `init.lua` - Added require for `custom.options`

**Behavior:**
- Inline: Small `■` icon indicates diagnostic presence
- Auto-popup: Full wrapped message appears after 500ms cursor hover
- Manual: `gl` in normal mode shows diagnostic float anytime
