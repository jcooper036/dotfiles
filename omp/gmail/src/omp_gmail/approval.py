"""User approval for send grants, shown by this server as a native macOS dialog.

The agent can't see or answer the dialog, so approval doesn't depend on how the MCP client renders
tool calls. No GUI session (SSH, headless, subagent-only machines) or no answer in time means denied.
"""

import subprocess
from datetime import datetime

# Must stay under the MCP call timeout in omp/mcp.json (300 s) so a late click can't approve a call
# the agent already saw time out.
DIALOG_SECONDS = 240

_SCRIPT = [
    "on run argv",
    'display dialog (item 1 of argv) with title (item 2 of argv) buttons {"Deny", "Approve"} '
    f'default button "Deny" cancel button "Deny" with icon caution giving up after {DIALOG_SECONDS}',
    "end run",
]


class NotApproved(RuntimeError):
    pass


def confirm(title: str, text: str) -> None:
    """Show the dialog; return only if the user clicked Approve, else raise NotApproved."""
    args = [part for line in _SCRIPT for part in ("-e", line)]
    try:
        result = subprocess.run(["osascript", *args, text, title], capture_output=True, text=True, timeout=DIALOG_SECONDS + 15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise NotApproved(f"Could not ask the user for approval ({exc}); nothing was granted.") from exc
    out = result.stdout.strip()
    if result.returncode == 0 and "button returned:Approve" in out and "gave up:false" in out:
        return
    if "gave up:true" in out:
        raise NotApproved("The user did not answer the approval dialog in time; nothing was granted.")
    if result.returncode != 0 and "-128" not in result.stderr:  # -128 = user clicked Deny
        raise NotApproved(f"Could not show the approval dialog ({result.stderr.strip()}); nothing was granted.")
    raise NotApproved("The user denied this request; nothing was granted. Do not ask again unless the user tells you to.")


def _clip(text: str, limit: int = 700) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def grant_text(
    account: str, user_instruction: str, recipients: list[str], scope: str, escalation: str,
    expires_at: str, max_sends_per_day: int, allow_attachments: bool,
) -> str:
    return (
        f"An agent asks for permission to SEND email as {account}.\n\n"
        f"Your instruction, as the agent quoted it:\n“{_clip(user_instruction)}”\n\n"
        f"May email: {', '.join(recipients)}\n"
        f"May say: {_clip(scope, 400)}\n"
        f"Escalates via: {_clip(escalation, 200)}\n"
        f"Expires: {datetime.fromisoformat(expires_at).astimezone().strftime('%a %b %-d, %-I:%M %p %Z')}\n"
        f"Limit: {max_sends_per_day} sends per day · attachments {'allowed' if allow_attachments else 'not allowed'}\n\n"
        "Every message is still checked against these terms and by an independent reviewer before it is sent. "
        "Revoke any time with `omp-gmail revoke`."
    )


def recipients_text(account: str, grant_id: str, current: list[str], new: list[str], reason: str, scope: str) -> str:
    return (
        f"An agent asks to email MORE people as {account} under send grant {grant_id}.\n\n"
        f"Add: {', '.join(new)}\n"
        f"Reason given: {_clip(reason, 400)}\n\n"
        f"Already allowed: {', '.join(current)}\n"
        f"Grant scope: {_clip(scope, 400)}"
    )
