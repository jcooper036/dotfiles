"""Send grants: user-approved, bounded permission for an agent to send email.

Without an active grant nothing can be sent. A grant names who may be emailed, until when, what the
agent may say, and how it escalates to the user. Creating a grant or widening its recipients goes
through tools that omp must be configured to confirm with the user every time (see require_user_prompt).
"""

import json
import os
import secrets
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from email.utils import getaddresses
from pathlib import Path

import yaml

from . import config

MAX_DAYS = 30
CONSUMER_DOMAINS = frozenset(
    {
        "gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com", "msn.com", "yahoo.com",
        "icloud.com", "me.com", "mac.com", "aol.com", "proton.me", "protonmail.com", "gmx.com", "hey.com",
    }
)
# omp tool names of the grant-widening tools; omp must prompt the user for each call.
PROMPTED_TOOLS = ("mcp__gmail_request_send_grant", "mcp__gmail_add_grant_recipients")


class GrantError(ValueError):
    pass


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass
class Grant:
    id: str
    user_instruction: str
    recipients: list[str]
    scope: str
    escalation: str
    created_at: str
    expires_at: str
    max_sends_per_day: int = 10
    allow_attachments: bool = False
    revoked_at: str | None = None
    recipient_history: list[dict] = field(default_factory=list)

    def status(self) -> str:
        if self.revoked_at:
            return "revoked"
        return "expired" if datetime.fromisoformat(self.expires_at) <= _now() else "active"

    def covers(self, address: str) -> bool:
        address = address.lower()
        domain = address.rpartition("@")[2]
        return any(p == address or (p.startswith("*@") and p[2:] == domain) for p in self.recipients)


def normalize_recipient(pattern: str) -> str:
    """Validate one recipient pattern: an exact address or `*@domain` (not a consumer mail domain)."""
    pattern = pattern.strip().lower()
    if pattern.startswith("*@"):
        domain = pattern[2:]
        if "." not in domain or "*" in domain or "@" in domain:
            raise GrantError(f"Invalid domain pattern: {pattern!r}")
        if domain in CONSUMER_DOMAINS:
            raise GrantError(f"{pattern!r} would allow anyone with a {domain} address; list exact addresses instead.")
        return pattern
    addresses = getaddresses([pattern])
    address = addresses[0][1] if len(addresses) == 1 else ""
    if "," in pattern or not address or "@" not in address or "*" in address:
        raise GrantError(f"Invalid recipient: {pattern!r}. Use one exact address or '*@company.com'.")
    return address


def _load() -> dict[str, Grant]:
    if not config.GRANTS_FILE.exists():
        return {}
    return {g["id"]: Grant(**g) for g in json.loads(config.GRANTS_FILE.read_text())}


def _save(grants: dict[str, Grant]) -> None:
    config.CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    tmp = config.GRANTS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps([asdict(g) for g in grants.values()], indent=2) + "\n")
    tmp.chmod(0o600)
    tmp.replace(config.GRANTS_FILE)


def list_grants(include_inactive: bool = False) -> list[Grant]:
    grants = sorted(_load().values(), key=lambda g: g.created_at, reverse=True)
    return [g for g in grants if include_inactive or g.status() == "active"]


def get_active(grant_id: str) -> Grant:
    grant = _load().get(grant_id)
    if grant is None:
        raise GrantError(f"No send grant {grant_id!r}.")
    if (status := grant.status()) != "active":
        raise GrantError(f"Send grant {grant_id} is {status}.")
    return grant


def create(
    user_instruction: str, recipients: list[str], scope: str, escalation: str,
    expires_in_days: int, max_sends_per_day: int, allow_attachments: bool,
) -> Grant:
    missing = [name for name, value in (("user_instruction", user_instruction), ("scope", scope), ("escalation", escalation)) if not value.strip()]
    if missing or not recipients:
        raise GrantError(f"A send grant needs explicit bounds; missing: {', '.join(missing + ([] if recipients else ['recipients']))}.")
    if not 1 <= expires_in_days <= MAX_DAYS:
        raise GrantError(f"expires_in_days must be between 1 and {MAX_DAYS}.")
    now = _now()
    grant = Grant(
        id="g-" + secrets.token_hex(4),
        user_instruction=user_instruction.strip(),
        recipients=sorted({normalize_recipient(r) for r in recipients}),
        scope=scope.strip(),
        escalation=escalation.strip(),
        created_at=now.isoformat(timespec="seconds"),
        expires_at=(now + timedelta(days=expires_in_days)).isoformat(timespec="seconds"),
        max_sends_per_day=max_sends_per_day,
        allow_attachments=allow_attachments,
    )
    grants = _load()
    grants[grant.id] = grant
    _save(grants)
    return grant


def add_recipients(grant_id: str, recipients: list[str], reason: str) -> Grant:
    if not reason.strip():
        raise GrantError("Say why these recipients are being added.")
    grant = get_active(grant_id)
    added = sorted({normalize_recipient(r) for r in recipients} - set(grant.recipients))
    grant.recipients = sorted(set(grant.recipients) | set(added))
    grant.recipient_history.append({"at": _now().isoformat(timespec="seconds"), "added": added, "reason": reason.strip()})
    grants = _load()
    grants[grant.id] = grant
    _save(grants)
    return grant


def revoke(grant_id: str) -> Grant:
    grants = _load()
    grant = grants.get(grant_id)
    if grant is None:
        raise GrantError(f"No send grant {grant_id!r}.")
    grant.revoked_at = grant.revoked_at or _now().isoformat(timespec="seconds")
    _save(grants)
    return grant


# ---------------------------------------------------------------- send log


def log_send(entry: dict) -> None:
    config.CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    with config.SEND_LOG_FILE.open("a") as fh:
        fh.write(json.dumps({"at": _now().isoformat(timespec="seconds")} | entry) + "\n")
    config.SEND_LOG_FILE.chmod(0o600)


def read_log() -> list[dict]:
    if not config.SEND_LOG_FILE.exists():
        return []
    return [json.loads(line) for line in config.SEND_LOG_FILE.read_text().splitlines() if line.strip()]


def sends_in_last_day(grant_id: str) -> int:
    cutoff = _now() - timedelta(days=1)
    return sum(
        1 for e in read_log()
        if e.get("grant_id") == grant_id and e.get("result") == "sent" and datetime.fromisoformat(e["at"]) > cutoff
    )


# ---------------------------------------------------------------- user-approval guard


def _omp_config_file() -> Path:
    if override := os.environ.get("PI_CODING_AGENT_DIR"):
        return Path(override) / "config.yml"
    profile = os.environ.get("OMP_PROFILE") or os.environ.get("PI_PROFILE")
    base = Path(os.environ.get("PI_CONFIG_DIR") or Path.home() / ".omp")
    return (base / "profiles" / profile / "agent" if profile else base / "agent") / "config.yml"


def require_user_prompt() -> None:
    """Fail closed unless omp is configured to ask the user before every grant-widening call.

    The approval itself happens in omp, outside this server; this check makes sure it can't be silently off.
    """
    path = _omp_config_file()
    try:
        settings = yaml.safe_load(path.read_text()) or {}
    except (OSError, yaml.YAMLError):
        settings = {}
    approval = ((settings.get("tools") or {}).get("approval") or {}) if isinstance(settings, dict) else {}
    unprompted = [t for t in PROMPTED_TOOLS if str(approval.get(t, "")).strip().lower() != "prompt"]
    if unprompted:
        lines = "\n".join(f"      {t}: prompt" for t in PROMPTED_TOOLS)
        raise GrantError(
            f"Send grants are disabled: omp is not set to ask the user before {', '.join(unprompted)}. "
            f"The user must add this to {path}:\n  tools:\n    approval:\n{lines}"
        )
