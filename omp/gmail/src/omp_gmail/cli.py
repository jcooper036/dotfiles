"""`omp-gmail` command: setup | login | status | serve."""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from . import auth, config

CONSOLE = "https://console.cloud.google.com"
CONSUMER_DOMAINS = ("@gmail.com", "@googlemail.com")


def _ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        answer = input(f"{prompt}{suffix}: ").strip()
        if answer or default:
            return answer or default  # type: ignore[return-value]


def _pause(message: str) -> None:
    input(f"{message}\nPress Enter when done... ")


def _gcloud(*args: str) -> subprocess.CompletedProcess | None:
    if not shutil.which("gcloud"):
        return None
    return subprocess.run(["gcloud", *args], capture_output=True, text=True)


def _choose_project(default: str | None) -> str:
    current = _gcloud("config", "get-value", "project")
    current_project = current.stdout.strip() if current and current.returncode == 0 else ""
    listing = _gcloud("projects", "list", "--format=json(projectId,name)", "--sort-by=projectId")
    projects = json.loads(listing.stdout) if listing and listing.returncode == 0 and listing.stdout.strip() else []

    print("\nThe OAuth client lives in a Google Cloud project. A Workspace account needs a project in its own")
    print("organization; a personal @gmail.com account can use any project you own.")
    if projects:
        print("Projects visible to gcloud on this machine:")
        for i, p in enumerate(projects, 1):
            marks = [m for m, on in (("current gcloud project", p["projectId"] == current_project), ("previously used", p["projectId"] == default)) if on]
            print(f"  {i:>2}. {p['projectId']:<32} {p.get('name', '')}" + (f"  <- {', '.join(marks)}" if marks else ""))
    else:
        print("(gcloud is missing or not signed in, so no projects can be suggested.)")
    choice = _ask("Pick a number or type a project id", default or current_project or None)
    if choice.isdigit() and 1 <= int(choice) <= len(projects):
        return projects[int(choice) - 1]["projectId"]
    return choice


def _enable_gmail_api(project: str) -> None:
    print(f"\nEnabling the Gmail API in {project}...")
    result = _gcloud("services", "enable", "gmail.googleapis.com", f"--project={project}")
    if result and result.returncode == 0:
        print("Gmail API enabled.")
        return
    if result:
        print(result.stderr.strip())
    _pause(f"Enable it in the browser instead: {CONSOLE}/apis/library/gmail.googleapis.com?project={project}")


def _configure_consent_screen(project: str, account: str) -> None:
    print(f"\nConfigure the OAuth consent screen: {CONSOLE}/auth/overview?project={project}")
    print("  If it says 'Get started': app name 'omp-gmail', support email = your address, then continue.")
    if account.lower().endswith(CONSUMER_DOMAINS):
        print("  Audience: External. Add yourself as a test user, then click 'Publish app' so it is 'In production'.")
        print("  (While the app is in Testing, Google expires sign-ins after 7 days. As an unverified production app")
        print("  you'll click through a 'Google hasn't verified this app' warning once per sign-in; that's expected.)")
    else:
        print("  Audience: Internal. Sign-ins then last until revoked, with no verification warning.")
    _pause("")


def _obtain_client_secrets(project: str) -> None:
    target = config.CLIENT_SECRETS_FILE
    if target.exists():
        existing = json.loads(target.read_text()).get("installed", {})
        if existing.get("project_id") == project and _ask("Reuse the existing OAuth client for this project? (y/n)", "y").lower().startswith("y"):
            return

    print(f"\nCreate a Desktop OAuth client: {CONSOLE}/auth/clients/create?project={project}")
    print("  Application type: Desktop app. Name: omp-gmail. Create, then 'Download JSON'.")
    _pause("")
    downloads = sorted((Path.home() / "Downloads").glob("client_secret_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    while True:
        path = Path(_ask("Path to the downloaded client JSON", str(downloads[0]) if downloads else None)).expanduser()
        try:
            installed = json.loads(path.read_text()).get("installed")
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Can't read {path}: {exc}")
            continue
        if not installed:
            print("That isn't a Desktop app client (no 'installed' section). Create the client with type 'Desktop app'.")
            continue
        if installed.get("project_id") != project:
            print(f"Warning: that client belongs to project {installed.get('project_id')!r}, not {project!r}.")
        break
    config.CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    shutil.copyfile(path, target)
    target.chmod(0o600)
    print(f"Saved the client to {target}. You can delete {path}.")


def setup() -> None:
    existing = config.load_optional()
    print("omp-gmail setup: configures which Gmail account the agent tools use on this machine.")
    account = _ask("Gmail address", existing.account if existing else None)
    while "@" not in account:
        account = _ask("That doesn't look like an email address. Gmail address")
    project = _choose_project(existing.project if existing else None)
    _enable_gmail_api(project)
    _configure_consent_screen(project, account)
    _obtain_client_secrets(project)
    download_dir = _ask("Where should downloaded attachments go", existing.download_dir if existing else "~/Downloads/gmail-agent")

    switching = existing is not None and existing.account.lower() != account.lower()
    cfg = config.Config(account=account, project=project, download_dir=download_dir)
    config.save(cfg)
    if switching:
        auth.forget(existing.account)  # type: ignore[union-attr]
    print("\nOpening the browser to sign in...")
    login(cfg)


def login(cfg: config.Config | None = None) -> None:
    cfg = auth.login(cfg or config.load())
    print(f"Signed in as {cfg.account}.")
    if cfg.refresh_expires_at:
        print(f"Warning: Google limited this sign-in until {cfg.refresh_expires_at}. If that's under a month away, the")
        print(f"OAuth app is probably still in Testing; publish it at {CONSOLE}/auth/audience?project={cfg.project}.")
    print("In omp, run `/mcp reconnect gmail` (or start a new session) to pick it up.")


def status() -> int:
    cfg = config.load_optional()
    if cfg is None:
        print("Not set up. Run `omp-gmail setup`.")
        return 1
    print(f"account:      {cfg.account}")
    print(f"project:      {cfg.project}")
    print(f"downloads:    {cfg.download_dir}")
    print(f"signed in:    {cfg.logged_in_at or 'never'}")
    if cfg.refresh_expires_at:
        days = (datetime.fromisoformat(cfg.refresh_expires_at) - datetime.now(UTC)).days
        print(f"sign-in ends: {cfg.refresh_expires_at} ({days} days)")
    try:
        creds = auth.load_credentials(cfg)
        profile = auth.gmail_service(creds).users().getProfile(userId="me").execute()
    except auth.NotSignedIn as exc:
        print(f"token:        {exc}")
        return 1
    print(f"token:        ok ({profile['messagesTotal']} messages in mailbox)")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="omp-gmail", description="Gmail tools for omp agents (no sending).")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("setup", help="choose account + GCP project, create the OAuth client, sign in")
    sub.add_parser("login", help="sign in again with the configured account")
    sub.add_parser("status", help="show configuration and check the stored sign-in")
    sub.add_parser("serve", help="run the MCP server on stdio (used by omp)")
    command = parser.parse_args().command
    try:
        if command == "serve":
            from .server import serve

            serve()
        elif command == "setup":
            setup()
        elif command == "login":
            login()
        else:
            sys.exit(status())
    except (config.NotConfigured, auth.NotSignedIn) as exc:
        sys.exit(str(exc))
    except KeyboardInterrupt:
        sys.exit(130)
