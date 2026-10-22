"""`omp-gmail` command: setup | login | status | serve."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from . import auth, config

CONSOLE = "https://console.cloud.google.com"
CONSUMER_DOMAINS = ("@gmail.com", "@googlemail.com")
SETUP_STEPS = 6

_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _style(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def bold(text: str) -> str:
    return _style("1", text)


def link(text: str) -> str:
    return _style("4;34", text)


def dim(text: str) -> str:
    return _style("2", text)


def good(text: str) -> str:
    return _style("32", text)


def warn(text: str) -> str:
    return _style("33", text)


def _step(n: int, title: str) -> None:
    print(f"\n{_style('1;36', f'[{n}/{SETUP_STEPS}] {title}')}")


def _ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        answer = input(f"{prompt}{suffix}: ").strip()
        if answer or default:
            return answer or default  # type: ignore[return-value]


def _continue() -> None:
    input(bold("Press Enter when done... "))


def _gcloud(*args: str) -> subprocess.CompletedProcess | None:
    if not shutil.which("gcloud"):
        return None
    return subprocess.run(["gcloud", *args], capture_output=True, text=True)


def _choose_project(default: str | None) -> str:
    current = _gcloud("config", "get-value", "project")
    current_project = current.stdout.strip() if current and current.returncode == 0 else ""
    listing = _gcloud("projects", "list", "--format=json(projectId,name)", "--sort-by=projectId")
    projects = json.loads(listing.stdout) if listing and listing.returncode == 0 and listing.stdout.strip() else []

    print("The OAuth client that signs you in lives in a Google Cloud project.")
    print(dim("A Workspace account needs a project in its own organization; a personal @gmail.com account can use any project you own."))
    if projects:
        print("Projects visible to gcloud on this machine:")
        for i, p in enumerate(projects, 1):
            marks = [m for m, on in (("current gcloud project", p["projectId"] == current_project), ("previously used", p["projectId"] == default)) if on]
            print(f"  {i:>2}. {p['projectId']:<32} {p.get('name', '')}" + dim(f"  <- {', '.join(marks)}" if marks else ""))
    else:
        print(dim("(gcloud is missing or not signed in, so no projects can be suggested.)"))
    choice = _ask("Pick a number or type a project id", default or current_project or None)
    if choice.isdigit() and 1 <= int(choice) <= len(projects):
        return projects[int(choice) - 1]["projectId"]
    return choice


def _enable_gmail_api(project: str) -> None:
    result = _gcloud("services", "enable", "gmail.googleapis.com", f"--project={project}")
    if result and result.returncode == 0:
        print(good(f"Gmail API is enabled in {project}."))
        return
    if result:
        print(warn(result.stderr.strip()))
    print(f"Enable it in the browser instead: {link(f'{CONSOLE}/apis/library/gmail.googleapis.com?project={project}')}")
    _continue()


def _configure_consent_screen(project: str, account: str) -> None:
    print(f"Open {link(f'{CONSOLE}/auth/overview?project={project}')}")
    print(f"and sign in as {bold(account)} if asked. Then, depending on what the page shows:")
    print(f"  {bold('An overview page')}: the consent screen already exists. Nothing to do here.")
    print("  " + bold('A "Get started" button') + ": click it and fill in:")
    print(f"      App name: omp-gmail    User support email: {account}")
    if account.lower().endswith(CONSUMER_DOMAINS):
        print(f"      Audience: {bold('External')}    Contact email: {account}    then agree and Create.")
        print(f"    Then on the Audience page, add {account} as a test user and click {bold('Publish app')}.")
        print(dim("    Unpublished (Testing) apps lose their sign-in after 7 days. As an unverified published app you'll click"))
        print(dim("    through a 'Google hasn't verified this app' warning when signing in; that's expected."))
    else:
        print(f"      Audience: {bold('Internal')}    Contact email: {account}    then agree and Create.")
        print(dim("    Internal apps keep the sign-in until it's revoked, with no verification warning."))
    _continue()


def _obtain_client_secrets(project: str) -> Path | None:
    """Copy a Desktop OAuth client JSON into the config dir. Returns the source path if one was copied."""
    target = config.CLIENT_SECRETS_FILE
    if target.exists():
        existing = json.loads(target.read_text()).get("installed", {})
        if existing.get("project_id") == project and _ask("An OAuth client for this project is already saved. Reuse it? (y/n)", "y").lower().startswith("y"):
            return None

    downloads = sorted((Path.home() / "Downloads").glob("client_secret_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if downloads:
        print(dim(f"Found a downloaded client in ~/Downloads; if it's from {project}, just press Enter below."))
    print(f"To create one, open {link(f'{CONSOLE}/auth/clients/create?project={project}')}")
    print(f"  Application type: {bold('Desktop app')}    Name: omp-gmail    then Create and {bold('Download JSON')}.")
    while True:
        path = Path(_ask("Path to the client JSON", _home(downloads[0]) if downloads else None)).expanduser()
        try:
            installed = json.loads(path.read_text()).get("installed")
        except (OSError, json.JSONDecodeError) as exc:
            print(warn(f"Can't read {path}: {exc}"))
            continue
        if not installed:
            print(warn("That isn't a Desktop app client (no 'installed' section). Create the client with type 'Desktop app'."))
            continue
        if installed.get("project_id") != project:
            print(warn(f"Note: that client belongs to project {installed.get('project_id')!r}, not {project!r}."))
        break
    config.CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    shutil.copyfile(path, target)
    target.chmod(0o600)
    print(good("OAuth client saved."))
    return path


def _home(path: Path | str) -> str:
    return str(path).replace(str(Path.home()), "~", 1)


def setup() -> None:
    existing = config.load_optional()
    print(bold("omp-gmail setup") + ": connects one Gmail account on this machine to the omp agent tools.")

    _step(1, "Gmail account")
    account = _ask("Gmail address", existing.account if existing else None)
    while "@" not in account:
        account = _ask("That doesn't look like an email address. Gmail address")
    download_dir = _ask("Folder for downloaded attachments", existing.download_dir if existing else "~/Downloads/gmail-agent")

    _step(2, "Google Cloud project")
    project = _choose_project(existing.project if existing else None)

    _step(3, "Enable the Gmail API")
    _enable_gmail_api(project)

    _step(4, "Sign in to the Google Cloud console and check the consent screen")
    _configure_consent_screen(project, account)

    _step(5, "Desktop OAuth client")
    copied_from = _obtain_client_secrets(project)

    switching = existing is not None and existing.account.lower() != account.lower()
    cfg = config.Config(account=account, project=project, download_dir=download_dir)
    config.save(cfg)
    if switching:
        auth.forget(existing.account)  # type: ignore[union-attr]

    _step(6, "Sign in to Gmail")
    print("A browser window opens; pick " + bold(account) + " and allow access.")
    cfg = _login(cfg)

    print(f"\n{good('Setup complete.')} Where everything lives on this machine (none of it is in git):")
    print(f"  Settings        {_home(config.CONFIG_FILE)}")
    print(f"  OAuth client    {_home(config.CLIENT_SECRETS_FILE)}" + (dim(f"  (copied from {_home(copied_from)}; the download can be deleted)") if copied_from else ""))
    print(f"  Sign-in token   macOS Keychain, item '{auth.KEYRING_SERVICE}' for {cfg.account}  " + dim("(view in Keychain Access)"))
    print(f"  Attachments     {cfg.download_dir}")
    print("Next: in omp run " + bold("/mcp reconnect gmail") + " (or start a new session).")
    print("Later: " + bold("omp-gmail status") + " checks the sign-in; " + bold("omp-gmail login") + " signs in again; rerun setup to switch accounts.")


def _login(cfg: config.Config) -> config.Config:
    cfg = auth.login(cfg)
    print(good(f"Signed in as {cfg.account}."))
    if cfg.refresh_expires_at:
        print(warn(f"Google limited this sign-in until {cfg.refresh_expires_at}. If that's under a month away, the OAuth app"))
        print(warn(f"is probably still in Testing; publish it at {CONSOLE}/auth/audience?project={cfg.project}."))
    return cfg


def login() -> None:
    _login(config.load())
    print("In omp, run " + bold("/mcp reconnect gmail") + " (or start a new session) to pick it up.")


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
