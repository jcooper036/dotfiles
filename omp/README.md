# OhMyPi config
Contains configuration, personal tools, skills, etc. for `omp` [https://omp.sh/docs](https://omp.sh/docs)

## MCP servers
`mcp.json` is omp's user-level MCP config. Symlink it once per machine:
```bash
mkdir -p ~/.omp/agent
ln -s ~/dotfiles/omp/mcp.json ~/.omp/agent/mcp.json
```
In a running omp session, `/mcp reload` picks up changes.

## gmail
`gmail/` is a local MCP server (Python, run through `uv`) that gives agents one Gmail account per machine (work account at work, personal account at home):

| Tool | What it does |
|---|---|
| `search_threads`, `get_thread`, `get_message` | Search with Gmail query syntax and read mail as plain text, with each message's attachment list |
| `list_labels`, `create_label`, `modify_labels` | Organize mail. Archive = remove `INBOX`, mark read = remove `UNREAD` |
| `trash`, `untrash` | Move to or from Trash (recoverable for 30 days) |
| `download_attachment` | Checks the file type first, then saves it. Never overwrites an existing file |
| `create_draft`, `update_draft`, `list_drafts`, `get_draft`, `delete_draft` | Drafts with local file attachments. Threaded replies and reply-all |

**There is no send tool.** Agents write drafts and you press send in Gmail. The OAuth scope (`gmail.modify`) technically allows sending, but the server never calls a send endpoint.

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
