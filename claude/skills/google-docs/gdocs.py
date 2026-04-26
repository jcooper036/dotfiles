# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-auth>=2.0",
#     "google-api-python-client>=2.0",
# ]
# ///
"""Google Docs skill runner — authenticates and executes a user script with
pre-built API services injected as globals.

Injected globals available to the executed script:
    credentials  — google.auth.credentials.Credentials (refreshed)
    docs_service — googleapiclient.discovery.Resource (Docs API v1)
    drive_service — googleapiclient.discovery.Resource (Drive API v3)
"""

import sys
from pathlib import Path

import google.auth
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES: list[str] = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/documents.readonly",
]


def get_credentials() -> google.auth.credentials.Credentials:
    """Load ADC credentials, refresh them, and probe Drive to validate."""
    credentials, _ = google.auth.default(scopes=SCOPES)
    credentials.refresh(Request())

    drive = build("drive", "v3", credentials=credentials)
    drive.files().list(pageSize=1, fields="files(id)").execute()

    return credentials


def main() -> None:
    assert len(sys.argv) == 2, f"Usage: gdocs.py <script_path>, got {sys.argv}"

    script_path = Path(sys.argv[1])
    assert script_path.exists(), f"Script not found: {script_path}"

    credentials = get_credentials()
    docs_service = build("docs", "v1", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)

    exec(
        compile(script_path.read_text(), str(script_path), "exec"),
        {
            "__name__": "__main__",
            "__file__": str(script_path),
            "credentials": credentials,
            "docs_service": docs_service,
            "drive_service": drive_service,
        },
    )


if __name__ == "__main__":
    main()
