---
name: blocked-sql-edit
description: Hand a SQL write to Jacob as two runnable commands — a dry run that ends in ROLLBACK, then the same change ending in COMMIT — when your own attempt to run it was denied. Use only after a SQL write or the database connection it needs was rejected (permission prompt declined, auto-mode classifier, missing role) AND you have explicitly checked that no sanctioned path exists — no running proxy with a write user, no writer credentials named in a skill or CLAUDE.md, no API endpoint that performs the write. - Triggers include: a psql / bq / sqlalchemy write denied by the harness; "Permission for this action was denied" on a database command; the user saying "give me a command to run" for a database change.
---

# Blocked SQL edit

You were denied a database write you still believe is correct. Do not route around the denial. Prepare the change so Jacob can run it in one command, see exactly what it does, and only then commit it.

## Check for a sanctioned path first

Before using this skill, confirm and say which of these you checked:
- a proxy or tunnel already running with a user that may write (`tun`, `ser`, skills such as `proteus-database`)
- writer credentials a skill or CLAUDE.md tells you to use
- an application API that performs the same write (e.g. `protcl`)

If one exists, use it. This skill is for when none does.

## Gather the facts read-only

Use whatever read path is allowed (BigQuery mirror, federated query, read-only role) to pull the current values of every row you will change. The script guards each update on these values, so they must be exact.

## Write one body, emit two files

Put the files in the scratchpad (or `tmp/` in the project). The body:
- opens a transaction
- loads every change into a temp table: key, old value, new value
- updates only rows whose current value still equals the old value
- counts updated rows and prints a before / after table
- rolls back and quits if the count is not the expected number

```sql
\set ON_ERROR_STOP 1
BEGIN;
CREATE TEMP TABLE changes (id bigint PRIMARY KEY, old_value text NOT NULL, new_value text NOT NULL) ON COMMIT DROP;
INSERT INTO changes VALUES
  (1234, 'old', 'new');
WITH updated AS (
  UPDATE <table> t SET <column> = c.new_value
  FROM changes c
  WHERE t.id = c.id AND t.<column> = c.old_value
  RETURNING t.id
)
SELECT count(*) AS updated FROM updated \gset
\echo updated :updated of <N>
SELECT c.id, c.old_value, t.<column> AS current_value, t.<column> = c.new_value AS changed
FROM changes c LEFT JOIN <table> t ON t.id = c.id ORDER BY c.id;
SELECT :updated = <N> AS all_rows \gset
\if :all_rows
\else
  \echo expected <N> rows updated; aborting
  ROLLBACK;
  \quit
\endif
```

Then:
```bash
{ cat body.sql; echo "ROLLBACK;"; } > <name>_dry_run.sql
{ cat body.sql; echo "COMMIT;"; } > <name>_commit.sql
```

Adapt the temp table to the change (several columns, composite keys, inserts with a `NOT EXISTS` guard, deletes guarded on the full old row). Keep the guard, the count, the abort, and the before / after table.

## Present it

In this order:
1. **Why you need it** — the denial you hit, in one line, and which sanctioned paths you checked.
2. **What it does** — a table of every row: key, old value, new value. Name anything the change assumes (e.g. "the sequence is truth, the name is wrong").
3. **Dry run** — one command that connects and runs `<name>_dry_run.sql`. Include the proxy line if one is needed, and fetch the password inline from the secret store; never print it.
4. **Commit** — the same command against `<name>_commit.sql`.

Tell Jacob to run the dry run first. Use full absolute paths to the files.

## After each run

- Dry run: read the output. Confirm the count and that every row shows the intended new value. Say so, or explain what differed and fix the body.
- Commit: verify through your read path, then carry on with whatever the edit was blocking.
