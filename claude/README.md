# Claude configuration

## Files
### CLAUDE_root.md
- is meant to be symlinked to `~/CLAUDE.md`
```bash
ln -s ~/dotfiles/claude/CLAUDE_root.md ~/CLAUDE.md
```
This should contain general practices to emulate across ALL machines and ALL projects.

### CLAUDE_template.md
This is a lightweight template based on the intent layers architecture: https://www.intent-systems.com/learn/intent-layer#turning-on-the-lights .  It follows a concept of progressive disclosure, where each part of a project has a CLAUDE.md file. 
-- WARNING -- I don't know if this behavior is specific to Claude. I know that Claude will read all CLAUDE.md files in a tree when it goes to touch a file - I don't know if other agents do that.

## Other agents
For Gemini, it can be made to rely on CLAUDE.md files with a simple config:
- https://geminicli.com/docs/cli/configuration/#available-settings-in-settingsjson
- usually configured in `~/.gemini/settings.json` if Gemini CLI is installed with `brew install gemini`
```json
{
    "contextFileName" : ["GEMINI.md", "CLAUDE.md", "AGENTS.md"]
}
```
Obviouslly this will mean that configurationsd could get messy (and some agents don't behave well given instructions that work for other agents) but its a good starting position.

