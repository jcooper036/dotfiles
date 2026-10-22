"""Gmail API operations used by the MCP tools. Every function takes an authorized `service`."""

import base64
import hashlib
import mimetypes
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import getaddresses
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from googleapiclient.http import MediaInMemoryUpload

from . import safety

# Gmail refuses to send messages whose attachments total more than 25 MB, so a bigger draft is useless.
MAX_ATTACHMENT_BYTES = 25 * 1024 * 1024
SUMMARY_HEADERS = ["From", "To", "Subject", "Date"]
SYSTEM_LABELS_HIDDEN_FROM_SUMMARY = {"CATEGORY_PERSONAL", "CATEGORY_UPDATES", "CATEGORY_PROMOTIONS", "CATEGORY_SOCIAL", "CATEGORY_FORUMS"}


# ---------------------------------------------------------------- decoding


def _b64decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def _headers(payload: dict) -> dict[str, str]:
    return {h["name"].lower(): h["value"] for h in payload.get("headers", [])}


def _charset(part: dict) -> str:
    content_type = _headers(part).get("content-type", "")
    for param in content_type.split(";")[1:]:
        key, _, value = param.strip().partition("=")
        if key.lower() == "charset" and value:
            return value.strip('"')
    return "utf-8"


def _decode_text(part: dict) -> str:
    raw = _b64decode(part["body"].get("data", ""))
    try:
        text = raw.decode(_charset(part), errors="replace")
    except LookupError:
        text = raw.decode("utf-8", errors="replace")
    return text.replace("\r\n", "\n")


def _snippet(msg: dict) -> str:
    return unescape(msg.get("snippet", ""))  # Gmail returns snippets HTML-escaped


class _HTMLToText(HTMLParser):
    BLOCK_TAGS = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "table"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in ("script", "style", "head"):
            self._skip_depth += 1
        elif tag in self.BLOCK_TAGS:
            self.chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "head") and self._skip_depth:
            self._skip_depth -= 1
        elif tag in self.BLOCK_TAGS:
            self.chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self.chunks.append(data)

    def text(self) -> str:
        lines = (" ".join(line.split()) for line in "".join(self.chunks).splitlines())
        out: list[str] = []
        for line in lines:
            if line or (out and out[-1]):
                out.append(line)
        return "\n".join(out).strip()


def html_to_text(html: str) -> str:
    parser = _HTMLToText()
    parser.feed(html)
    parser.close()
    return parser.text()


def _walk(part: dict):
    yield part
    for child in part.get("parts", []):
        yield from _walk(child)


def _is_attachment(part: dict) -> bool:
    return bool(part.get("filename")) or bool(part["body"].get("attachmentId"))


def _body_text(payload: dict) -> str:
    parts = [p for p in _walk(payload) if not _is_attachment(p)]
    for mime, convert in (("text/plain", None), ("text/html", html_to_text)):
        for part in parts:
            if part.get("mimeType") == mime and part["body"].get("data"):
                text = _decode_text(part)
                return convert(text) if convert else text
    return ""


def _attachments(payload: dict) -> list[dict[str, Any]]:
    return [
        {
            "part_id": part["partId"],
            "filename": part.get("filename") or "",
            "mime_type": part.get("mimeType", ""),
            "size": part["body"].get("size", 0),
        }
        for part in _walk(payload)
        if part.get("partId") and _is_attachment(part)
    ]


# ---------------------------------------------------------------- labels


class Labels:
    """Name <-> id lookup for the mailbox's labels. System label ids equal their names (INBOX, UNREAD, ...)."""

    def __init__(self, service) -> None:
        self.service = service
        self.refresh()

    def refresh(self) -> None:
        labels = self.service.users().labels().list(userId="me").execute().get("labels", [])
        self.by_id = {label["id"]: label for label in labels}

    def name(self, label_id: str) -> str:
        label = self.by_id.get(label_id)
        return label["name"] if label else label_id

    def names(self, label_ids: list[str]) -> list[str]:
        return sorted(self.name(i) for i in label_ids if i not in SYSTEM_LABELS_HIDDEN_FROM_SUMMARY)

    def resolve(self, names_or_ids: list[str]) -> list[str]:
        lookup = {}
        for label in self.by_id.values():
            lookup[label["id"].lower()] = label["id"]
            lookup[label["name"].lower()] = label["id"]
        resolved, unknown = [], []
        for item in names_or_ids:
            (resolved if item.lower() in lookup else unknown).append(lookup.get(item.lower(), item))
        if unknown:
            raise ValueError(f"Unknown label(s): {', '.join(unknown)}. Use list_labels, or create_label first.")
        return resolved


# ---------------------------------------------------------------- reading


def message_view(msg: dict, labels: Labels, max_body_chars: int) -> dict[str, Any]:
    payload = msg["payload"]
    headers = _headers(payload)
    body = _body_text(payload)
    return {
        "message_id": msg["id"],
        "thread_id": msg["threadId"],
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        "cc": headers.get("cc", ""),
        "date": headers.get("date", ""),
        "subject": headers.get("subject", ""),
        "labels": labels.names(msg.get("labelIds", [])),
        "body": body[:max_body_chars],
        "body_truncated": len(body) > max_body_chars,
        "attachments": _attachments(payload),
    }


def _batch_get(service, requests: list) -> list[dict]:
    """Execute up to 50 GET requests in one HTTP round trip, preserving order."""
    results: list[dict | None] = [None] * len(requests)
    errors: list[Exception] = []

    def callback(request_id: str, response: dict, exception: Exception | None) -> None:
        if exception:
            errors.append(exception)
        else:
            results[int(request_id)] = response

    for start in range(0, len(requests), 50):
        batch = service.new_batch_http_request(callback=callback)
        for i, request in enumerate(requests[start : start + 50], start):
            batch.add(request, request_id=str(i))
        batch.execute()
    if errors:
        raise errors[0]
    return results  # type: ignore[return-value]


def search_threads(service, labels: Labels, query: str, max_results: int, page_token: str | None) -> dict[str, Any]:
    listing = service.users().threads().list(userId="me", q=query, maxResults=max_results, pageToken=page_token).execute()
    threads = listing.get("threads", [])
    detail = _batch_get(
        service,
        [
            service.users().threads().get(userId="me", id=t["id"], format="metadata", metadataHeaders=SUMMARY_HEADERS)
            for t in threads
        ],
    )
    out = []
    for thread in detail:
        messages = thread["messages"]
        first, last = _headers(messages[0]["payload"]), _headers(messages[-1]["payload"])
        out.append(
            {
                "thread_id": thread["id"],
                "subject": first.get("subject", ""),
                "from": first.get("from", ""),
                "last_from": last.get("from", ""),
                "last_date": last.get("date", ""),
                "message_count": len(messages),
                "labels": labels.names(sorted({i for m in messages for i in m.get("labelIds", [])})),
                "snippet": _snippet(messages[-1]),
            }
        )
    return {"threads": out, "next_page_token": listing.get("nextPageToken")}


def get_thread(service, labels: Labels, thread_id: str, max_body_chars: int) -> dict[str, Any]:
    thread = service.users().threads().get(userId="me", id=thread_id, format="full").execute()
    return {"thread_id": thread["id"], "messages": [message_view(m, labels, max_body_chars) for m in thread["messages"]]}


def get_message(service, labels: Labels, message_id: str, max_body_chars: int) -> dict[str, Any]:
    return message_view(service.users().messages().get(userId="me", id=message_id, format="full").execute(), labels, max_body_chars)


# ---------------------------------------------------------------- organizing


def list_labels(labels: Labels) -> list[dict[str, str]]:
    return sorted(
        ({"name": label["name"], "id": label["id"], "type": label["type"]} for label in labels.by_id.values()),
        key=lambda label: (label["type"] != "user", label["name"].lower()),
    )


def create_label(service, labels: Labels, name: str) -> dict[str, str]:
    label = service.users().labels().create(
        userId="me", body={"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
    ).execute()
    labels.refresh()
    return {"name": label["name"], "id": label["id"]}


def modify_labels(service, labels: Labels, kind: str, ids: list[str], add: list[str], remove: list[str]) -> dict[str, Any]:
    add_ids, remove_ids = labels.resolve(add), labels.resolve(remove)
    if not add_ids and not remove_ids:
        raise ValueError("Nothing to change: pass add and/or remove.")
    body = {"addLabelIds": add_ids, "removeLabelIds": remove_ids}
    if kind == "message":
        service.users().messages().batchModify(userId="me", body={"ids": ids} | body).execute()
    else:
        for thread_id in ids:
            service.users().threads().modify(userId="me", id=thread_id, body=body).execute()
    return {"modified": len(ids), "kind": kind, "added": [labels.name(i) for i in add_ids], "removed": [labels.name(i) for i in remove_ids]}


def set_trashed(service, kind: str, ids: list[str], trashed: bool) -> dict[str, Any]:
    resource = service.users().messages() if kind == "message" else service.users().threads()
    for item_id in ids:
        (resource.trash if trashed else resource.untrash)(userId="me", id=item_id).execute()
    return {"kind": kind, "count": len(ids), "trashed": trashed}


# ---------------------------------------------------------------- attachments


def download_attachment(service, message_id: str, part_id: str, dest_dir: Path) -> dict[str, Any]:
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    part = next((p for p in _walk(msg["payload"]) if p.get("partId") == part_id), None)
    if part is None or not _is_attachment(part):
        raise ValueError(f"Message {message_id} has no attachment with part_id {part_id!r}.")
    body = part["body"]
    if body.get("attachmentId"):
        body = service.users().messages().attachments().get(userId="me", messageId=message_id, id=body["attachmentId"]).execute()
    data = _b64decode(body.get("data", ""))

    filename = safety.safe_filename(part.get("filename") or f"attachment-{part_id}")
    safety.check(filename, part.get("mimeType", ""), data)  # raises before anything is written

    dest_dir.mkdir(parents=True, exist_ok=True)
    stem, suffix = Path(filename).stem, Path(filename).suffix
    target = dest_dir / filename
    n = 1
    while True:
        try:
            with target.open("xb") as fh:  # never overwrite an existing file
                fh.write(data)
            break
        except FileExistsError:
            n += 1
            target = dest_dir / f"{stem} ({n}){suffix}"
    return {"path": str(target), "size": len(data), "mime_type": part.get("mimeType", ""), "sha256": hashlib.sha256(data).hexdigest()}


# ---------------------------------------------------------------- drafts


def _clean_header(value: str) -> str:
    if "\r" in value or "\n" in value:
        raise ValueError("Header values cannot contain line breaks.")
    return value


def _addresses(values: list[str]) -> str:
    return ", ".join(_clean_header(v.strip()) for v in values if v.strip())


def _read_attachments(paths: list[str]) -> list[tuple[str, str, bytes]]:
    files = []
    for raw in paths:
        path = Path(raw).expanduser()
        if not path.is_file():
            raise ValueError(f"Attachment not found: {path}")
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        files.append((path.name, mime, path.read_bytes()))
    return files


def _compose(
    headers: dict[str, str], body: str, attachments: list[tuple[str, str, bytes]]
) -> EmailMessage:
    total = sum(len(data) for _, _, data in attachments)
    if total > MAX_ATTACHMENT_BYTES:
        raise ValueError(f"Attachments total {total / 1e6:.1f} MB; Gmail's limit is 25 MB.")
    msg = EmailMessage()
    for name, value in headers.items():
        if value:
            msg[name] = _clean_header(value)
    msg.set_content(body)
    for filename, mime, data in attachments:
        maintype, _, subtype = mime.partition("/")
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)
    return msg


def _upload(msg: EmailMessage) -> MediaInMemoryUpload:
    return MediaInMemoryUpload(msg.as_bytes(policy=policy.SMTP), mimetype="message/rfc822", resumable=True)


def _draft_summary(draft: dict) -> dict[str, Any]:
    return {"draft_id": draft["id"], "message_id": draft["message"]["id"], "thread_id": draft["message"]["threadId"]}


def _reply_headers(service, message_id: str, reply_all: bool, account: str) -> tuple[str, dict[str, str], list[str], list[str]]:
    """Thread id, threading headers, default To and Cc for a reply to `message_id`."""
    original = service.users().messages().get(
        userId="me", id=message_id, format="metadata",
        metadataHeaders=["Message-ID", "References", "Subject", "From", "Reply-To", "To", "Cc"],
    ).execute()
    h = _headers(original["payload"])
    subject = h.get("subject", "")
    rfc_id = h.get("message-id", "")
    threading = {
        "Subject": subject if subject.lower().startswith("re:") else f"Re: {subject}",
        "In-Reply-To": rfc_id,
        "References": f"{h.get('references', '')} {rfc_id}".strip(),
    }
    me = account.lower()
    to = [addr for _, addr in getaddresses([h.get("reply-to") or h.get("from", "")]) if addr]
    if to and to[0].lower() == me:  # replying to our own message: keep the original recipients
        to = [addr for _, addr in getaddresses([h.get("to", "")]) if addr]
    cc: list[str] = []
    if reply_all:
        seen = {a.lower() for a in to} | {me}
        for _, addr in getaddresses([h.get("to", ""), h.get("cc", "")]):
            if addr and addr.lower() not in seen:
                seen.add(addr.lower())
                cc.append(addr)
    return original["threadId"], threading, to, cc


def create_draft(
    service,
    account: str,
    to: list[str],
    cc: list[str],
    bcc: list[str],
    subject: str | None,
    body: str,
    attachment_paths: list[str],
    reply_to_message_id: str | None,
    reply_all: bool,
) -> dict[str, Any]:
    thread_id = None
    headers: dict[str, str] = {"Subject": subject or ""}
    if reply_to_message_id:
        thread_id, threading, default_to, default_cc = _reply_headers(service, reply_to_message_id, reply_all, account)
        headers = threading | ({"Subject": subject} if subject else {})
        to = to or default_to
        cc = cc or default_cc
    if not to:
        raise ValueError("A draft needs at least one recipient in `to`.")
    headers |= {"To": _addresses(to), "Cc": _addresses(cc), "Bcc": _addresses(bcc)}
    msg = _compose(headers, body, _read_attachments(attachment_paths))
    meta = {"message": {"threadId": thread_id}} if thread_id else {}
    draft = service.users().drafts().create(userId="me", body=meta, media_body=_upload(msg)).execute()
    return _draft_summary(draft) | {"to": headers["To"], "cc": headers["Cc"], "subject": headers["Subject"]}


def update_draft(
    service,
    draft_id: str,
    to: list[str] | None,
    cc: list[str] | None,
    bcc: list[str] | None,
    subject: str | None,
    body: str | None,
    add_attachment_paths: list[str],
    remove_attachment_names: list[str],
) -> dict[str, Any]:
    current = service.users().drafts().get(userId="me", id=draft_id, format="raw").execute()
    old = BytesParser(policy=policy.default).parsebytes(_b64decode(current["message"]["raw"]))

    headers = {name: old.get(name, "") for name in ("Subject", "In-Reply-To", "References", "To", "Cc", "Bcc")}
    if to is not None:
        headers["To"] = _addresses(to)
    if cc is not None:
        headers["Cc"] = _addresses(cc)
    if bcc is not None:
        headers["Bcc"] = _addresses(bcc)
    if subject is not None:
        headers["Subject"] = subject

    if body is None:
        old_body = old.get_body(preferencelist=("plain", "html"))
        old_text: str = "" if old_body is None else old_body.get_content()
        if old_body is not None and old_body.get_content_type() == "text/html":
            old_text = html_to_text(old_text)
        body = old_text

    remove = set(remove_attachment_names)
    kept = []
    for part in old.iter_attachments():
        name = part.get_filename() or ""
        if name in remove:
            remove.discard(name)
            continue
        kept.append((name, part.get_content_type(), part.get_payload(decode=True) or b""))
    if remove:
        raise ValueError(f"Draft has no attachment named: {', '.join(sorted(remove))}")

    msg = _compose(headers, body, kept + _read_attachments(add_attachment_paths))
    meta = {"message": {"threadId": current["message"]["threadId"]}}
    draft = service.users().drafts().update(userId="me", id=draft_id, body=meta, media_body=_upload(msg)).execute()
    return _draft_summary(draft) | {
        "to": headers["To"], "cc": headers["Cc"], "subject": headers["Subject"],
        "attachments": [name for name, _, _ in kept] + [Path(p).name for p in add_attachment_paths],
    }


def list_drafts(service, query: str | None, max_results: int, page_token: str | None) -> dict[str, Any]:
    listing = service.users().drafts().list(userId="me", q=query, maxResults=max_results, pageToken=page_token).execute()
    drafts = listing.get("drafts", [])
    detail = _batch_get(
        service,
        [service.users().drafts().get(userId="me", id=d["id"], format="metadata") for d in drafts],
    )
    out = []
    for draft in detail:
        h = _headers(draft["message"]["payload"])
        out.append(
            _draft_summary(draft)
            | {"to": h.get("to", ""), "subject": h.get("subject", ""), "snippet": _snippet(draft["message"])}
        )
    return {"drafts": out, "next_page_token": listing.get("nextPageToken")}


def get_draft(service, labels: Labels, draft_id: str, max_body_chars: int) -> dict[str, Any]:
    draft = service.users().drafts().get(userId="me", id=draft_id, format="full").execute()
    view = message_view(draft["message"], labels, max_body_chars)
    view["bcc"] = _headers(draft["message"]["payload"]).get("bcc", "")
    return {"draft_id": draft["id"]} | view
