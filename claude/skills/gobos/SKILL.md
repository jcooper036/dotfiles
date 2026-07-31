---
name: gobos
description: Answer anything about Jacob's cron-driven agent workers ("gobos") — what ran, what it cost, what is in flight, why one failed, what a given agent actually did. They all live in /Users/jacob/workers and record to one sqlite file; this skill is the map to that record. Use it whenever a question touches the workers repo, a gobo, the overseer, worker_instances, gobo.sqlite, or one of the named workers (proteus-canary, proteus-feedback-to-issues, proteus-domain-annotation, proteus-ground-truth-import, proteus-erd-updater, leash-trunk-build, leash-issue-solver, leash-pr-fixer, worktree-pruner) — including from a session in some other repo that noticed an agent-created issue, PR, branch or worktree and wants to know which worker made it.
when_to_use: >-
  Triggers include: what ran overnight; why did the canary go red; what have the workers
  cost this week; is anything stuck; who opened this PR or this worktree; what did that
  agent actually do; read the agent transcript; check the gobo logs; what is in flight
  right now; and any mention of gobo, gobos, the overseer, tick, or worker_instances.
allowed-tools: Read Grep Glob Bash(sqlite3 /Users/jacob/workers/var/gobo.sqlite *) Bash(tmux list-windows *) Bash(tmux capture-pane *) Bash(crontab -l)
---

# Gobos: where the record lives

Gobos are agent workers started by cron on this machine. Everything about them — code,
database, logs, transcripts — is under `/Users/jacob/workers`. Nothing about them is on a
server, in a cloud log, or in GitHub Actions. Work from absolute paths; you are usually
invoked from some other repo.

Read `/Users/jacob/workers/AGENTS.md` before drawing conclusions about design. It is the
authority on why the system is shaped this way, and it is shorter than this file.

## Three records answer three different questions

| Question | Look at |
| --- | --- |
| What ran, what it cost, what it decided | `var/gobo.sqlite` |
| Did cron even reach the code | `logs/<gobo>-log.txt` (raw cron stdout) |
| What did the agent actually *do* | `logs/agents/<session_id>.jsonl` |

The flat cron log is the safety net that sits outside the thing it catches. When `tick`
dies before it can write to the database — broken `uv`, import error, a command not on
cron's bare PATH — the database has no row, because nothing ran. The one line in
`logs/*-log.txt` is the only evidence.

## Start at the database

```bash
sqlite3 /Users/jacob/workers/var/gobo.sqlite
```

`.schema` and `PRAGMA table_info(<t>)` are authoritative — the tables grow as gobos are
added. Four core tables (`workers`, `worker_instances`, `logs`, and one `<gobo>_data` per
gobo that returns a verdict) and a view per interesting gobo (`v_canary`, `v_feedback`,
`v_trunk_build`, plus `v_orphans`).

Foreign keys are named `<table>_<column>`: `worker_instances_id` joins
`worker_instances(id)`, `workers_name` joins `workers(name)`. Ids are uuid7, so
`ORDER BY id` is `ORDER BY time`. Timestamps are UTC, so `datetime('now', ...)` compares
directly against `started_at`.

**Never write to it.** Live gobos are writing to that file through WAL right now.

## worker_instances is measurement; <gobo>_data is testimony

`worker_instances` holds what the harness observed around the agent — duration, cost,
which models ran, what the permission system denied. The agent cannot forge any of it.
`<gobo>_data` holds what the agent claimed: the verdict, the action taken, the evidence.
Different tables so you always know which one you are reading. When they disagree, the
instance row wins.

`logs` is narration; `source` says whether a line came from the overseer (cron, `tick`) or
the gobo (the tmux window, `run`).

## An instance row means work was found

A tick that surveys and finds nothing writes a `no work` log line and no instance. Counting
rows counts work, not cron firings. The registry (`workers`) is re-synced on every tick, so
it is always current.

## Recipes

```sql
-- what ran in the last day
SELECT workers_name, status, count(*) n
FROM worker_instances WHERE started_at > datetime('now','-1 day')
GROUP BY 1,2 ORDER BY 1;

-- spend and wall time, last week. GROUP BY runtime is not optional: codex reports no
-- price, so total_cost_usd is NULL for it and any cross-runtime SUM undercounts.
SELECT runtime, count(*) n, round(sum(total_cost_usd),2) usd,
       round(sum(duration_ms)/60000.0,1) minutes
FROM worker_instances WHERE started_at > datetime('now','-7 day') GROUP BY 1;

-- most recent failures, with the error the harness captured
SELECT id, workers_name, work_key, substr(error,1,400) err
FROM worker_instances WHERE status='error' ORDER BY id DESC LIMIT 5;

-- the transcript for a run
SELECT ts, workers_name, json_extract(data,'$.path')
FROM logs WHERE event='transcript' ORDER BY id DESC LIMIT 10;

-- per-model cost inside one run
SELECT json_extract(usage,'$.by_model."claude-opus-4-8".costUSD') FROM worker_instances WHERE id=?;

-- runs where the permission system blocked something
SELECT id, workers_name, permission_denials FROM worker_instances
WHERE json_array_length(permission_denials) > 0 ORDER BY id DESC;

-- everything one instance narrated, in order
SELECT ts, source, event, data FROM logs WHERE worker_instances_id=? ORDER BY id;
```

Registry and schedule:

```bash
/Users/jacob/workers/scripts/gobo.sh list   # registered gobos, variants, descriptions
crontab -l                                  # who ticks, how often, and to which log file
```

## In flight is a tmux fact, not a database fact

Agents outlive the cron interval by a wide margin, so the process table is the only thing
that knows what is already claimed. Each window carries its work key as `[key]`, and each
survey excludes those.

```bash
tmux list-windows -t workers -F '#{window_id} #{window_name}'
```

`status='running'` in the database means "no terminal row was ever written" — which is
also what a window that died looks like. Cross-check against tmux before believing it.
`v_orphans` names instances still open past two hours and hands you the `tmux_window_id`
to ask with. That gap is deliberate: a confident `failed`, written by something that never
observed the failure, would be worth less than nothing.

## Symptom to evidence

| Symptom | Where to look |
| --- | --- |
| Nothing ran at all, no rows | `logs/<gobo>-log.txt` — tick died before the sink |
| Dispatched, then silence | tmux window gone; `logs/agents/<session>.jsonl` for how far it got |
| Stuck `running` for hours | `v_orphans`, then `tmux list-windows` |
| Agent ran but no verdict row | `logs` event `no structured output` — holds the raw text it returned instead |
| Agent refused to do something | `permission_denials` on the instance |
| `models` shows a model you did not expect | For claude that is what the harness *observed*; believe it. For codex it is only what was requested with `-m`. |

## Read, do not run

Answer from the record. Do not run `gobo tick` or `gobo run` by hand, do not touch the
crontab, and do not clean up worktrees or windows unless Jacob asks in this session — a
window you kill is an agent someone is paying for. Reporting "four pr-fixer instances have
been open eleven hours and their windows are gone" is the job; reaping them is not.

## Transcripts are large — delegate

`logs/agents/*.jsonl` runs to megabytes for a single run. To answer "what did this agent
actually do", dispatch a subagent with the specific path and question rather than grepping
it into your own context.
