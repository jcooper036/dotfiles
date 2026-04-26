---
name: google-docs
description: Interact with Google Docs for reading, analyzing, and making changes. Covers document retrieval, content analysis, commenting, and editing with proper permission handling. Always requests explicit approval before modifying documents or adding comments.
allowed-tools: Bash(uv run --script *)
---

# Google Docs Interaction Guidelines

This skill defines how Claude should interact with Google Docs programmatically. Follow these rules strictly.

## Core Principles

1. **Read-only operations** (retrieving document content) can be performed freely
2. **Never modify documents without explicit approval** - default to suggesting edits via comments
3. **Document deletion is forbidden** - never suggest or attempt to delete documents
4. **Always get explicit permission** before commenting on or editing documents
5. **When in doubt, ask the user** - transparency is more important than efficiency
6. **Never claim to be human** - prefix independent Claude comments with "Claude Comment:"

---

## Technical Details

### Authentication & Credentials

Google Docs access uses the Google Docs API v1 (`docs`, not `drive`) and Google Drive API v3 (`drive`) with proper OAuth2 authentication.

#### Setup & Troubleshooting

**Prerequisites:**
- User has authenticated with `gcloud auth application-default login`
- Credentials have appropriate OAuth scopes

**If authentication fails**, help the user run:

```bash
gcloud auth application-default login --scopes=openid,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/accounts.reauth
```

**If quota issues occur**, suggest:

```bash
gcloud auth application-default set-quota-project eng-infrastructure
```

**If auth credentials are stale**, help with:

```bash
gcloud auth application-default login
```

### Running Code

All Google Docs operations use the **runner script** at `~/.claude/skills/google-docs/gdocs.py`. This script handles authentication and dependency management via PEP 723 + `uv run --script`, so it works from any directory without needing a project-level Python environment.

**Workflow:**
1. Write your Google Docs Python code to a temp file (e.g., `tmp/query.py`)
2. Run it through the runner: `uv run --script ~/.claude/skills/google-docs/gdocs.py tmp/query.py`

**Pre-injected globals** available in your script (no imports needed):
- `credentials` — authenticated Google credentials
- `docs_service` — Docs API v1 (`docs_service.documents().get(...)`)
- `drive_service` — Drive API v3 (`drive_service.files().list(...)`)

**Example** — list 5 recently edited docs:
```python
results = drive_service.files().list(
    q="mimeType='application/vnd.google-apps.document'",
    orderBy="modifiedByMeTime desc",
    pageSize=5,
    fields="files(id, name, modifiedTime, webViewLink)",
).execute()

for f in results.get("files", []):
    print(f"{f['name']}  —  {f['modifiedTime']}")
    print(f"  {f['webViewLink']}")
```

### Extracting Document ID

Google Docs URLs have this format:
```
https://docs.google.com/document/d/{DOCUMENT_ID}/edit
```

Extract the `DOCUMENT_ID` from the URL for API calls. Use `re.search(r'/document/d/([a-zA-Z0-9_-]+)', url)`.

### Reading Document Content

Write a script that uses the pre-injected `docs_service`:

```python
document = docs_service.documents().get(documentId=doc_id).execute()
title = document.get("title")

body = document.get("body", {}).get("content", [])
text_parts = []
for element in body:
    if "paragraph" in element:
        for text_run in element["paragraph"].get("elements", []):
            if "textRun" in text_run:
                text_parts.append(text_run["textRun"]["content"])

full_text = ''.join(text_parts)
print(f"# {title}\n\n{full_text}")
```

---

## Operations by Permission Level

### Freely Allowed (No Permission Needed)

These read-only operations can be used without asking:

- Retrieving document content (title, full text, structure)
- Reading document metadata (creation date, last modified, owner)
- Analyzing document content and structure
- Extracting specific sections or data from documents
- Checking document access and permissions

### Requires Explicit Permission

Always ask before running these:

| Operation | Requirements |
|-----------|--------------|
| Add comment to document | Show exact comment text; confirm if "Claude Comment:" prefix is needed |
| Edit document content directly | Confirm user wants direct edits (vs. suggestions) |
| Add document suggestions | Ask if this is preferred edit mode |
| Modify document formatting | Requires explicit approval |
| Share document with others | Requires confirmation of who and what role |
| Change document permissions | Requires explicit approval |
| Copy document | Ask for confirmation |

### Never Do (Forbidden)

**Never attempt these operations. Suggest the user do them manually if needed:**

- Delete documents
- Transfer document ownership
- Remove document permissions (even from self)
- Lock documents
- Archive documents

---

## Detailed Policies

### Adding Comments

**When adding independent comments:**

1. **Always prefix with "Claude Comment:"** so the user knows who wrote it
2. **Show the exact comment text to the user** and get approval before posting
3. **Never add comments without asking** - even if requested to analyze a doc

Example workflow:

```
1. User: "Review this Google Doc and add any comments"
2. Claude: Reads doc, identifies issues, says:
   "I found [issues]. Here's the comment I'd add: [comment text]. Should I post this?"
3. User: "yes" (or suggests edits)
4. Claude: Posts comment with "Claude Comment:" prefix
```

**When posting on behalf of the user:**

- The user may explicitly request you post a specific comment without the "Claude Comment:" prefix
- Only do this if explicitly requested ("post this comment on my behalf")
- Show the comment text for approval regardless

### Editing Documents

**Default behavior: Use suggestions, not direct edits**

1. **Always default to document suggestions mode** (not direct edits)
2. **Show the exact changes** to the user and get approval before applying
3. **Only edit directly** if user explicitly says "make direct edits"

Example workflow:

```
1. User: "Fix the typos in this doc"
2. Claude: Reads doc, identifies typos, shows proposed changes:
   "Found [N] typos. I'll suggest these edits: [list]. OK?"
3. User: "yes" or "make direct edits instead"
4. Claude: Applies changes (as suggestions by default, or direct if approved)
```

### Sharing & Permissions

**Never unilaterally share documents.** Always ask:

- Who should have access?
- What role should they have? (viewer, commenter, editor)
- Should access be removed from anyone?

### Document Access Issues

If you cannot access a document:

1. Check that the document ID is correct
2. Verify the user has access to the document
3. Suggest running the authentication commands above if credentials are stale
4. Ask the user to manually grant access if needed

---

## Quick Reference Card

| Operation | Permission Level | Notes |
|-----------|------------------|-------|
| Read document content | Free | No approval needed |
| Analyze document | Free | No approval needed |
| Add comment | Ask first | Show comment text, use "Claude Comment:" prefix |
| Post comment on user's behalf | Ask first | Only if explicitly requested without prefix |
| Suggest edits | Ask first | Default edit mode |
| Direct edits | Ask first | Only if user explicitly approves |
| Share document | Ask first | Confirm who/what role |
| Change permissions | Ask first | Never unilaterally change |
| Copy document | Ask first | Confirm before copying |
| Delete document | **FORBIDDEN** | Never do, suggest user handle manually |
| Transfer ownership | **FORBIDDEN** | Never do, suggest user handle manually |
| Remove permissions | **FORBIDDEN** | Never do, suggest user handle manually |

---

## Common Issues & Solutions

### "Permission denied" errors

- User may not have access to the document
- Try running: `gcloud auth application-default login`
- Check that credentials have correct scopes (includes `drive` scope)

### "Invalid document ID"

- Verify the Google Docs URL is correct
- Extract ID from URL format: `https://docs.google.com/document/d/{ID}/edit`
- Check for extra characters or typos

### Authentication expired

- Run: `gcloud auth application-default login`
- Or: `gcloud auth application-default login --scopes=openid,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/accounts.reauth`

### Dependencies not installing

- The runner uses PEP 723 inline metadata — `uv run --script` handles installation automatically
- If deps fail to resolve, try: `uv cache clean` and re-run
