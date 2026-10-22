"""OAuth sign-in and the authorized Gmail client.

The refresh token is stored in the macOS Keychain (service `omp-gmail`, account = email address),
so one browser sign-in lasts until Google revokes it.
"""

import json
from datetime import UTC, datetime, timedelta

import keyring
from google.auth.credentials import Credentials as AnyCredentials
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from keyring.errors import PasswordDeleteError

from . import config

# gmail.modify is the narrowest scope that covers reading, labels, trash, and drafts.
# It also permits sending; the server sends only through send_draft, under a user-approved send grant.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
KEYRING_SERVICE = "omp-gmail"


class NotSignedIn(RuntimeError):
    pass


def _relogin_hint(account: str) -> str:
    return f"Gmail sign-in for {account} is missing or expired. Run `omp-gmail login` in a terminal."


def load_credentials(cfg: config.Config) -> Credentials:
    raw = keyring.get_password(KEYRING_SERVICE, cfg.account)
    if raw is None:
        raise NotSignedIn(_relogin_hint(cfg.account))
    creds = Credentials.from_authorized_user_info(json.loads(raw), SCOPES)
    if not creds.valid:
        try:
            creds.refresh(Request())
        except RefreshError as exc:
            raise NotSignedIn(f"{_relogin_hint(cfg.account)} ({exc})") from exc
    return creds


def forget(account: str) -> None:
    try:
        keyring.delete_password(KEYRING_SERVICE, account)
    except PasswordDeleteError:
        pass


def gmail_service(creds: AnyCredentials):
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def login(cfg: config.Config) -> config.Config:
    """Run the browser OAuth flow, verify the mailbox, and store the refresh token in the Keychain."""
    flow = InstalledAppFlow.from_client_secrets_file(str(config.CLIENT_SECRETS_FILE), SCOPES)
    creds = flow.run_local_server(
        port=0,
        login_hint=cfg.account,
        access_type="offline",
        prompt="consent",  # guarantees a refresh token even if this client was authorized before
        authorization_prompt_message=f"Sign in as {cfg.account} in the browser window. If none opened:\n{{url}}",
        success_message="omp-gmail is signed in. You can close this tab.",
    )
    if not creds.refresh_token:
        raise NotSignedIn("Google returned no refresh token; revoke the app at https://myaccount.google.com/permissions and retry.")

    actual = gmail_service(creds).users().getProfile(userId="me").execute()["emailAddress"]
    if actual.lower() != cfg.account.lower():
        raise NotSignedIn(f"Signed in as {actual}, but this machine is configured for {cfg.account}. Nothing was saved.")

    keyring.set_password(KEYRING_SERVICE, cfg.account, creds.to_json())
    now = datetime.now(UTC)
    cfg.logged_in_at = now.isoformat(timespec="seconds")
    expires_in = flow.oauth2session.token.get("refresh_token_expires_in")
    cfg.refresh_expires_at = (now + timedelta(seconds=int(expires_in))).isoformat(timespec="seconds") if expires_in else None
    config.save(cfg)
    return cfg
