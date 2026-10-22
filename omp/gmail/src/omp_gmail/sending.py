"""Sending a draft under a send grant: mechanical checks, independent review, send, label, log."""

from email.utils import getaddresses
from typing import Any

from . import config, grants, mail, reviewer

SENT_LABEL = "agent-sent"


class SendHeld(RuntimeError):
    """The draft was not sent; it stays in Drafts. The message says why and how to escalate."""


def _addresses(*header_values: str) -> list[str]:
    return [addr.lower() for _, addr in getaddresses([v for v in header_values if v]) if addr]


def _hold(grant: grants.Grant, draft_id: str, reasons: list[str], verdict: dict | None = None) -> SendHeld:
    grants.log_send({"grant_id": grant.id, "draft_id": draft_id, "result": "held", "reasons": reasons} | ({"review": verdict} if verdict else {}))
    bullet = "\n".join(f"- {r}" for r in reasons)
    return SendHeld(
        f"Not sent; draft {draft_id} is still in Drafts.\n{bullet}\n"
        f"Do not retry by rewording around these reasons. Escalate to the user via: {grant.escalation}"
    )


def _own_addresses(service, account: str) -> set[str]:
    """The account address plus its Gmail send-as aliases."""
    aliases = service.users().settings().sendAs().list(userId="me").execute().get("sendAs", [])
    return {account.lower()} | {a["sendAsEmail"].lower() for a in aliases}


def mechanical_problems(grant: grants.Grant, me: set[str], draft: dict[str, Any], thread: list[dict[str, Any]]) -> list[str]:
    """Checks that need no judgment. Empty list = OK. `me` is the user's own addresses."""
    problems = []
    recipients = _addresses(draft.get("to", ""), draft.get("cc", ""), draft.get("bcc", ""))
    if not recipients:
        problems.append("draft has no recipients")
    if outside := sorted({a for a in recipients if not grant.covers(a)}):
        problems.append(f"recipients not covered by grant {grant.id}: {', '.join(outside)}")
    # Someone on the other side may have pulled new people into the conversation.
    participants = {a for m in thread for a in _addresses(m.get("from", ""), m.get("to", ""), m.get("cc", ""))}
    if newcomers := sorted(a for a in participants if a not in me and not grant.covers(a)):
        problems.append(f"thread includes participants the grant does not cover: {', '.join(newcomers)}")
    if draft.get("attachments") and not grant.allow_attachments:
        problems.append("draft has attachments and the grant does not allow sending attachments")
    if (sent := grants.sends_in_last_day(grant.id)) >= grant.max_sends_per_day:
        problems.append(f"grant {grant.id} already sent {sent} messages in the last 24h (limit {grant.max_sends_per_day})")
    return problems


def send_draft(service, labels: mail.Labels, cfg: config.Config, grant_id: str, draft_id: str) -> dict[str, Any]:
    grant = grants.get_active(grant_id)
    draft = mail.get_draft(service, labels, draft_id, max_body_chars=200_000)
    thread = []
    if draft["thread_id"]:
        full = mail.get_thread(service, labels, draft["thread_id"], max_body_chars=reviewer.MAX_BODY_CHARS)
        thread = [m for m in full["messages"] if m["message_id"] != draft["message_id"] and "DRAFT" not in m["labels"]]

    if problems := mechanical_problems(grant, _own_addresses(service, cfg.account), draft, thread):
        raise _hold(grant, draft_id, problems)
    verdict = reviewer.review(cfg.reviewer_model, grant, cfg.account, thread, draft)
    if verdict["decision"] != "send":
        raise _hold(grant, draft_id, [f"reviewer: {r}" for r in verdict["reasons"]] or ["reviewer held the message"], verdict)

    sent = service.users().drafts().send(userId="me", body={"id": draft_id}).execute()
    label_id = next((i for i, label in labels.by_id.items() if label["name"] == SENT_LABEL), None)
    if label_id is None:
        label_id = mail.create_label(service, labels, SENT_LABEL)["id"]
    service.users().messages().modify(userId="me", id=sent["id"], body={"addLabelIds": [label_id]}).execute()
    grants.log_send(
        {"grant_id": grant.id, "draft_id": draft_id, "result": "sent", "message_id": sent["id"], "thread_id": sent["threadId"],
         "to": draft["to"], "cc": draft["cc"], "bcc": draft.get("bcc", ""), "subject": draft["subject"], "review": verdict}
    )
    return {"sent": True, "message_id": sent["id"], "thread_id": sent["threadId"], "grant_id": grant.id, "reviewer": verdict["reasons"]}
