# Optional GitHub bot identity

This is an opt-in integration for the Leash-Labs `jacob-agent-team` GitHub App. Cloning or setting up dotfiles does not enable it. Choose which agents use it on each machine. The app's installation determines repository access; this setup does not grant permissions or change branch protection.

## Prepare this machine

Requires macOS, Bun at `~/.bun/bin/bun`, and GitHub CLI at `/opt/homebrew/bin/gh`.

Keep the private key outside the repository, for example `~/.secrets/gh-agent-team-bot/private-key.pem`. Put the following in `~/.secrets/github_team_bot.env`, using the values from the GitHub App settings:

```sh
AGENT_TEAM_BOT_APP_ID=5110740
AGENT_TEAM_BOT_CLIENT_ID=YOUR_CLIENT_ID
AGENT_TEAM_BOT_PRIVATE_KEY_PATH=~/.secrets/gh-agent-team-bot/private-key.pem
```

The secrets directory must be mode `700`; the environment file and PEM must be mode `600`. The installer discovers the installation ID through GitHub and adds `AGENT_TEAM_BOT_INSTALLATION_ID` to the environment file. The ID is also the number at the end of the installation's Configure URL under the organization's installed GitHub Apps.

```sh
cd ~/dotfiles/gh-agent-team-bot
bun install
```

## Enable Claude Code on this machine

```sh
bun run install:claude
```

This patches only the environment in `~/.claude/settings.json`. Restart Claude Code. Every local Claude Code session using that user configuration will then use the bot for GitHub operations and Git authorship.

## Enable Codex on this machine

```sh
bun run install:codex
```

This patches only `shell_environment_policy.set` in `~/.codex/config.toml`. Restart Codex. Local Codex sessions using that user configuration will then use the bot. Use `bun run install:both` to opt in both tools.

## Choose individual sessions instead

Leave the persistent integration uninstalled for that tool, then launch a session explicitly:

```sh
bun ~/dotfiles/gh-agent-team-bot/src/cli.ts run claude
bun ~/dotfiles/gh-agent-team-bot/src/cli.ts run codex
```

Run the launcher from the project where you want to work. It sets the bot environment for the launched process and its children. Ordinary launches keep their existing identity. Hosted agents and MCP connections require separate authentication setup.

## Disable either integration

```sh
bun run uninstall:claude
bun run uninstall:codex
```

Use `bun run uninstall:both` for both. Restart the affected tools. Uninstall restores the settings this installer replaced and preserves unrelated settings and subsequent user edits. It leaves the private key and token cache in place. Configuration backups and installation state live under `~/.cache/gh-agent-team-bot`.

## Authentication stays inside opted-in processes

The helper signs an app JWT with the PEM, discovers the Leash-Labs installation, and obtains an installation token through `gh api`. Tokens stay in an owner-only cache and renew five minutes before expiry. Authentication errors stop the command. Agent `gh` uses a separate configuration directory without Jacob's saved login.

Agent sessions set bot author and committer metadata. Git rewrites standard GitHub SSH URLs to HTTPS in the process environment and uses the credential helper only for `github.com/Leash-Labs`. Repository remotes, global Git configuration, and shared shell configuration stay unchanged. Existing commits, explicit author overrides, and coauthor trailers retain their own attribution.

Agent-specific shell startup files preserve wrapper precedence when macOS login shells rebuild `PATH`. They load the user's existing startup files; they do not replace or edit them. These wrappers separate normal identities, not processes deliberately accessing credentials under Jacob's OS account.

## Verify from the agent's shell

`gh auth status` reports the bot identity, installation ID, repository access and expiry without printing credentials. `gh pr list -R Leash-Labs/leash` checks GraphQL access; `git ls-remote git@github.com:Leash-Labs/leash.git HEAD` checks HTTPS credential routing. Run `bun run doctor --refresh` here to exercise renewal.

Run `bun test` and `bun run check` before changing the helper. When installing from a worktree, the installer links this checkout at `~/dotfiles/gh-agent-team-bot`. Keep the worktree until the code is merged and the installation points at the merged checkout.
