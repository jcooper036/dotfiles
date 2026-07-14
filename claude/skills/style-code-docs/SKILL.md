---
name: style-code-docs
description: Edit documentation, READMEs, AGENTS.md/CLAUDE.md, docstrings, and config
  comments into Jacob's voice. Cut hard, restructure rules into scannable assertion
  headings, delete dead history, and keep only comments that state intent. Use when
  writing or revising any prose that ships next to code.
when_to_use: Writing or editing a README, AGENTS.md, CLAUDE.md, design doc, module
  docstring, or config-file comments. Also when asked to "clean up the docs", "make
  this sound like me", or before committing new documentation.
---

# Style code docs

Prose that ships next to code is a liability until proven otherwise. Every line must survive the question: *would a reader be misled if this were stale?* Default to cutting.

## People and agents are good at discovery - do NOT over-reference
Dead references are a bad an likely outcome of referencing paths, documents, etc. too heavily. 
- You do NOT need to list the modules in a folder - people and agents know how to `ls`. 
- You do NOT need to reference code specifics, or provide code examples - they are likely to be out of date with the real code
- Comments are ALWAYS tech-debt. They provide a confusing reference that ONLY has the potential to differ from the code. They should only be used when FOR SOME REASON the code you are writing cannot clearly express what will happen when it's run. This is ALWAYS to be emperical - comments should only clarify instances where existing and for some reason un-changeable code has already caused confusion. 

## The ratio

A real pass over agent-written docs deletes far more than it adds — 10:1 is normal. If your edit is net-additive, you have not done this pass. Say what you cut.

## Formatting

### One paragraph is one line
Never hard-wrap prose. Editors soft-wrap; hard wraps make prose diffs unreadable.

### Rules become headings that assert the rule
Replace the `- **Thing.** <four lines of explanation>` bullet with a `### Thing` heading and a plain paragraph. Write the heading as the claim itself:

- `### Stages persist nothing`
- `### Done = the product does something new, end-to-end`
- `### Residue positions are 1-indexed`

A reader skimming only the headings should collect every rule in the document. Reserve bullets for lists of genuinely parallel short items.

### Ration bold
Bold marks the word that changes the meaning of the sentence (`**NEVER**`, `**not**`), not the topic of every clause.

## Cut these on sight

### The sermon
Once a rule is stated, do not re-argue it. Analogies, restatements, and "the two are easy to confuse precisely because..." paragraphs go.

### Gravestones for dead designs.
No `> **Historical:** we used to use X. Do not build against X.` Delete the whole thing — the tool, the comparison doc, the docstring reference. Git has the history; the docs describe what is. Think of the naive user - it's far better for them to not need to know that the old thing ever existed.

### Inventories of discoverable state
Route lists, file lists, table-of-columns dumps, release-log tables. `ls` and the schema are the source of truth.

### Duplication across levels
If a fact belongs to a lower-level doc, it lives there and only there. Higher levels summarize intent and point downward. Move it down rather than restating it.

### Navigation filler
"See X for the service shape, and Y for running the stack." Link where it's load-bearing, not as a courtesy.

## Keep and strengthen these

- Concepts, in plain words, where the reader lands. 
- Hard rules, stated absolutely 
- Safety rails, with a blunt do-not-touch 
- The causal mechanism. How the pieces actually hand off to each other, in plain declarative sentences, is worth more than any amount of decoration.

## Comments and docstrings

A comment earns its place only by stating intent or a constraint the code cannot show.

- Module docstring: what it's for and how to run it. Not an essay on the architecture, not a history of what it replaced. Often one line. Often none.
- Config files: no comment essays above a block. A trailing comment survives only if it explains *why this value* — `backoffLimit: 1  # one retry; a genuinely broken migration should fail fast, not thrash`. Explaining *what a value is* is noise and tech debt.
- Never numbered steps, "Step X", or "Phase X" labels.
- Rationale that belongs in an issue or design doc goes in the issue or design doc.

## Voice

Plain declarative sentences. First-person plural for team decisions ("we know to cross reference..."). Explain mechanism causally. Do not perform. Do not hedge. Do not compress into arrow-chains or jargon — readable beats terse.
