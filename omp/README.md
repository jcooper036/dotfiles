# OhMyPi config
Contains configuration, personal tools, skills, etc. for `omp` [https://omp.sh/docs](https://omp.sh/docs)

## Setup
```bash
~/dotfiles/omp/install.sh
```
Run it from the main checkout. Links point at the script's own location, so running it from a worktree links omp to files that disappear with the worktree. It is safe to rerun; it targets the agent dir that `omp config path` prints (normally `~/.omp/agent`).

## omp state splits three ways

### `config/` is linked, so changes land in the repo
Every entry in `config/` is symlinked by name into the agent dir. This is for files that change slowly and that we want versioned: `AGENTS.md`, `RULES.md`, `keybindings.yml`, `models.yml`, `mcp.json`, `themes/`, `extensions/`, `hooks/`. If omp writes to one of these, the change shows up as a git diff, which is what we want for config that rarely moves. To add a file, put it in `config/` and rerun `install.sh`. A real file already sitting at a link target is moved aside to `<name>.bak-<timestamp>` before linking.

### `defaults/` is copied, so omp owns the live file
omp rewrites `config.yml` whenever a setting is saved: picking a model, `/settings`, `omp config set`, the setup wizard. Linking it would turn every model switch into a repo diff. The repo holds a starting point instead, and `install.sh` copies it only when the agent dir has no `config.yml`. `install.sh --reset-config` overwrites the live file with the default, backing the old one up first. To keep a setting long term, copy it into `defaults/config.yml` by hand.

### Everything else stays local and is **never** committed
The agent dir also holds logins and API keys (`agent.db`), prompt history, the model catalog, sessions, caches and blobs. These are machine state, and `agent.db` is a credential store. API keys for the shell go in `~/.secrets/*.env`; provider logins go through `/login`. Nothing in `config/` or `defaults/` may contain a secret.

## Skills
omp's skills dir (`~/.omp/agent/skills`) is the hub every agent on this machine reads skills from. It is machine state: each machine picks its own skills, so nothing in it is committed.

### Each machine opts into skills by linking them
```bash
~/dotfiles/omp/link-skills.sh ~/dotfiles/claude/skills/<skill> ~/<repo>/.agents/skills/<skill>
```
The script links each skill folder into the hub under its frontmatter `name`, and refuses paths inside a worktree. Skills that exist only on this machine live in the hub as real folders. Skills inside a repo already load when an agent runs in that repo; link them only to use them everywhere. To drop a skill, delete its hub link and rerun the script.

### Other agents read the hub through links
Every run makes `~/.agents/skills` a link to the hub, which is where Codex and `npx skills` look, so `npx skills add` installs land in the hub as real folders. Every run also gives `~/.claude/skills` one link per hub skill and prunes links whose hub skill is gone. `~/.claude/skills` stays a real directory because Claude Code writes its own state there (`synced/` account skills, `.trash/`), so Claude's synced account skills stay Claude-only. omp reads the hub both directly and through `~/.agents/skills`, and merges the two because they resolve to the same files.

### Link skill folders, never `SKILL.md`
Codex ignores a linked `SKILL.md` file.

## Status line
`defaults/config.yml` sets a custom status line: the default preset's segments, with `status` placed right after `context_pct`. `statusLine.contextLine: annotated` keeps the context percent as its own segment rather than inside the gauge line, so it comes before the weekly quota.

`config/extensions/weekly-quota.ts` fills that `status` slot with the active account's 7-day usage, for example `Weekly 23%`. It reads the same numbers as `omp usage`, refetches every 5 minutes (at most once a minute after a turn), and picks up model switches within 2 seconds. Only Claude (`anthropic`) and Codex (`openai-codex`) are queried. Every other provider shows `Weekly Quota Unknown`. Other extensions' `setStatus` text also lands in the `status` segment, so `showHookStatus: false` keeps it from being shown a second time in the footer.

## Pause and resume
`omp pause [reason]` pauses every omp session on this machine (the reason is optional); `omp reconnect` resumes them. For going offline: agents are told to park their work, then to continue when the connection returns.

- `omp` is a zsh function in `zshrc` that routes those two words to `omp/bin/omp-pause` and `omp/bin/omp-reconnect` (on `PATH` through `zshrc`) and passes everything else to omp, through the GitHub bot launcher where installed. Scripts and cron call the `omp-pause` / `omp-reconnect` scripts directly.
- `omp-pause` writes `~/.omp/agent/pause.json` (`since`, optional `reason`); `omp-reconnect` deletes it. `OMP_PAUSE_FILE` overrides the path.
- `config/extensions/pause.ts` polls that file every 2 seconds in every session, subagents included. On pause it shows `PAUSED` in the status line, steers a busy agent to park its work and end the turn, and blocks every tool call (an in-flight tool finishes). On resume it tells the agent to continue; only sessions that were mid-turn at pause restart on their own, idle ones just get the note.
- A session started while paused is told at startup. Background workers that don't load extensions need their own check of the file.
- Pause is cooperative: an agent mid-request finishes that request first.

## MCP servers
`config/mcp.json` is omp's user-level MCP config, linked like everything else in `config/`. In a running omp session, `/mcp reload` picks up changes.

## GitHub identity
omp has no persistent env setting, so the bot identity comes from the launcher: on machines with `~/.secrets/github_team_bot.env`, `zshrc` aliases `omp` to `gh-agent-team-bot run omp`. Subagents inherit it. Only interactive shells see the alias, so scripts and cron must call the launcher themselves. `command omp` launches without it.

## gmail
`gmail/` is a local MCP server (Python, run through `uv`) that gives agents one Gmail account per machine (work account at work, personal account at home):

| Tool | What it does |
|---|---|
| `search_threads`, `get_thread`, `get_message` | Search with Gmail query syntax and read mail as plain text, with each message's attachment list |
| `list_labels`, `create_label`, `modify_labels` | Organize mail. Archive = remove `INBOX`, mark read = remove `UNREAD` |
| `trash`, `untrash` | Move to or from Trash (recoverable for 30 days) |
| `download_attachment` | Checks the file type first, then saves it. Never overwrites an existing file |
| `create_draft`, `update_draft`, `list_drafts`, `get_draft`, `delete_draft` | Drafts with local file attachments. Threaded replies and reply-all |
| `request_send_grant`, `add_grant_recipients`, `list_send_grants`, `revoke_send_grant` | Manage your permission for agents to send (see below) |
| `send_draft` | Send an existing draft under a send grant |

**Sending is off unless you grant it.** Agents write drafts by default. An agent can send only under a **send grant**, which is permission with explicit bounds:
- **who** it may email: exact addresses, or `*@company.com`. Consumer domains like `*@gmail.com` are refused.
- **until when**: at most 30 days
- **what** it may say
- **how to escalate** to you for anything else

An agent requests a grant with `request_send_grant`, quoting your instruction. The server then opens a macOS dialog on your screen listing the exact terms:
- your instruction, as the agent quoted it
- who it may email
- what it may say
- the escalation path
- the expiry
- the daily limit and whether attachments are allowed

Click **Approve** or **Deny**. Adding recipients later (`add_grant_recipients`) shows a dialog too. The agent can't answer the dialog. Unanswered after 4 minutes counts as Deny, and so does having no GUI session (SSH, headless runs).

Before `send_draft` sends anything:
1. **Mechanical checks.** The grant must be active. Every To, Cc, and Bcc address must be inside it. Nobody in the thread may be outside it besides you and your send-as aliases, so if someone adds a new person to the thread, the send is held. No attachments unless the grant allows them. A daily send cap applies.
2. **Independent review.** A separate model (`reviewer_model` in `~/.config/omp-gmail/config.json`, default `sonnet`) sees only the grant, the thread, and the draft. It runs through `omp -p` with no usable tools: this server refuses to start inside it, `always-ask` approval makes other MCP tools fail headless, and any attempted tool call holds the send. It holds the message if it:
   - commits you to money, time, or an agreement
   - goes beyond the grant's scope
   - discloses information the scope doesn't call for
   - follows instructions that came from an email

   If the reviewer fails or is unsure, the message is held.

A held message stays in Drafts, and the agent is told to escalate. A sent message gets the `agent-sent` label. Every send and every hold is logged to `~/.config/omp-gmail/send_log.jsonl`. Commands:
- `omp-gmail grants` lists grants with their sent and held counts.
- `omp-gmail revoke <id>` stops a grant immediately.

These checks cover agents going through the tools: prompt injection and mistakes. They don't stop an agent that deliberately goes around the server with a shell. The Gmail token can already send, and processes running as you can read it from the Keychain and the grant file.

**Attachment screening** is a type blocklist (`gmail/src/omp_gmail/safety.py`), not antivirus. It runs on the bytes before anything is written, and refuses:
- executables, scripts, and installers, matched by extension, MIME type, or magic bytes, so a renamed `.exe` is still refused
- macro-enabled Office files, including `.docx` or `.xls` files that contain a VBA project
- HTML and SVG
- encrypted zips, and zips containing anything blocked or a nested zip
- archives it can't inspect (rar, 7z, tar, gz, and similar)

Filenames are reduced to a single safe path component. The second layer is Gmail's own server-side malware scanning.

### Setup (once per machine)
Prerequisites: `uv`, plus `gcloud` signed in if you want existing GCP projects suggested.
```bash
source ~/.zshrc        # picks up the omp-gmail alias
omp-gmail setup
```
The wizard runs six numbered steps (`[1/6]` to `[6/6]`):
1. **Gmail account**: the address, and the folder for downloaded attachments.
2. **Google Cloud project**: lists the projects `gcloud` can see; pick one or type a project id. A Workspace account needs a project in its own org. A personal `@gmail.com` account can use any project you own.
3. **Enable the Gmail API** in that project. If `gcloud` can't, it gives you a console link.
4. **Sign in to the Google Cloud console and check the consent screen.** If the page shows an overview, it already exists and there's nothing to do. If it shows "Get started", fill it in:
   - Workspace account: set the audience to **Internal**.
   - `@gmail.com` account: set the audience to **External**, then **Publish app**. Apps left in Testing get sign-ins that expire after 7 days.
5. **Desktop OAuth client**: reuses an already-saved client, or offers the newest `client_secret_*.json` in `~/Downloads`. If neither exists, it links to the page that creates one.
6. **Sign in to Gmail** in the browser. It checks that the mailbox you signed into matches the address you gave.

At the end it prints where everything was saved. All of it stays on this machine; nothing goes in git:
- `~/.config/omp-gmail/config.json`: account, project, download folder
- `~/.config/omp-gmail/client_secret.json`: a copy of the OAuth client (the original in `~/Downloads` can be deleted)
- macOS Keychain, item `omp-gmail`: the refresh token

### Day to day
- `omp-gmail status`: shows the account and checks the stored sign-in.
- `omp-gmail login`: signs in again. You only need this if a tool reports the sign-in expired or was revoked; Internal and published apps keep the sign-in until it's revoked or goes unused for 6 months. Afterwards run `/mcp reconnect gmail` in omp.
- To switch this machine to another account, rerun `omp-gmail setup`.
