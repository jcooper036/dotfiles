"""Machine-local configuration: which account this machine uses and where its OAuth client lives.

Nothing here is checked into git. The refresh token itself lives in the macOS Keychain (see auth.py).
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("OMP_GMAIL_HOME") or Path.home() / ".config" / "omp-gmail")
CONFIG_FILE = CONFIG_DIR / "config.json"
CLIENT_SECRETS_FILE = CONFIG_DIR / "client_secret.json"
GRANTS_FILE = CONFIG_DIR / "send_grants.json"
SEND_LOG_FILE = CONFIG_DIR / "send_log.jsonl"


class NotConfigured(RuntimeError):
    pass


@dataclass
class Config:
    account: str
    project: str
    download_dir: str
    logged_in_at: str | None = None
    # Set when Google issued a time-limited refresh token (e.g. an External app still in "Testing").
    refresh_expires_at: str | None = None
    # Model (omp fuzzy name) that independently reviews every agent send before it goes out.
    reviewer_model: str = "sonnet"


def load() -> Config:
    if not CONFIG_FILE.exists():
        raise NotConfigured("Gmail tools are not set up on this machine. Run `omp-gmail setup` in a terminal.")
    return Config(**json.loads(CONFIG_FILE.read_text()))


def load_optional() -> Config | None:
    try:
        return load()
    except NotConfigured:
        return None


def save(cfg: Config) -> None:
    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(asdict(cfg), indent=2) + "\n")
    CONFIG_FILE.chmod(0o600)
