# User persona
The user you are interacting with is named Jacob. He is a data scientist with broad experience in data science, software engineering, and has a Ph.D focused on genetics, genomics, molecular bio, and cell bio. He has the most experience with writing in python and sql. He is very curious and eager to learn. For coding, he loves to learn new languages, tools, and packages - he is always interested in learning and using the best tool for the job. 

# Common writing locations
Every project should have a `.worktrees` folder and a `tmp` folder at the git project root, and they should be git ignored

# Coding

## All programming
- no function should be longer than 60 lines of code. If it is, refactor
- large if / elif / else statements are generally an anti-pattern, and demonstrate that something is wrong (lacking generalization, parameterizations, encapsulation, etc.)
- whever language you are in, use type hinting on inputs and outputs
- always 0 index counters
- ALWAYS use UUID7 if generating random ids if possible

### service probing
- when writing code that interfaces with other services, write `probe` calls that hit the service the first time the service is contacted from the environment
- ex: 
```pseudocode
def probe(endpoint:str = "<my-service>/api/v1/healthz", headers=headers):
    r = request.get(endpoint, headers)
    r.raise_for_status
```
- look for health check endpoints
- the logic is that it is almost always saves time because the call is super fast and we resolve connection errors seperate of other interactions
- note: if this is not fast (i.e. multiple seconds to resolve the probe), then that is a problem sign alone
- the only time we wouldn't do this is if performance can actually be improved with one less call

### Writing logs / surfacing info
It's CRTICAL that we surface information, not answers. Information gives future actors a chance to reason about what is happening. Attempting to give answers is biased in the context of the current work. An example
- We wrote a database table where we had a column called "error". If there was an error, we attempted to write the error
- Though sensible, this caused days of lost progress. You have to be 100% correct about how you write the error for this to work, otherwise it will mislead people and agents to no end.
- The solution was to change the column to "log_query" - and provide the query to the GCP logs (in this case it was running on GCP). This changes from someone looking at the table and saying "oh I think I know what happened", to going and reading the primary resource that tells them what happened.

## Comments and docstrings
- NEVER use comments or docstrings when writing code
- They serve as dead weight when code changes
- know that the USER will handle writing comments or docstrings. If you see comments or docstrings, that's because the user wrote them, not because you should.

## Git and github
- ALWAYS use the `gh` tool to interact with github

### git hygene
- ALWAYS work in worktrees
- ALL worktrees should be kept in .worktrees/ (in the project, not in the users folder)
- .worktrees should always be git ignored
- before doing any git operations, check what branch you are on
- never git add or git commit or git push to the "trunk" or "main" branch unless explicity approved to do so
- instead, if you find yourself on one of those branches, make a new worktree for the current changes first
- once PRs are merged, remove old worktrees

### writing commits
- ALWAYS include the commit trailer "Co-Authored-By: {model} <noreply@anthropic.com>"

## Python
- enforce pep8 conventions by using `ruff`
- ALWAYS use `uv` to manage python env and installs
    - `uv add`, `uv sync`, `uv lock`
    - assume the uv env in active, but if it isn't `source .venv/bin/activate`
    - https://docs.astral.sh/uv/
    - python scripts in a project must ALWAYS be runnable without setting the python path. because we are running in uv, that should always look like python <script> <arguments>
    - NEVER USE `pip install`. Only fall back to `uv pip install` if `uv add` fails to install the package
    - all python installs are manged by `uv`, and the command `python` is aliased to `uv run python` if a .venv is present and `uv run --python 3.13 python` if not. NEVER use `python3`, as that points to the system python, which is not what we want
- configure the project via pyproject.toml. If this doesn't exit, STOP and ask the user what to do
- always use type hints. HOWEVER, do not use the `typing` module for builtin types like list, dict, str, etc. You are usually working in python 3.12+
- put tests in `./tests`. Tests are written with the `pytest` framework and are configured in `pyproject.toml`
- `pytest` is expected to resolve all tests in 2 seconds unless stated otherwise
- use `ruff` for linting and formatting
- type checkers are not _required_, but are encouraged. use `ty`, NEVER use `mypy`
- always prefer `structlog` over the standard library logging module. Don't use print statements for logging
- use `tqdm` for progress bars, never custom implementations
- imports should ALWAYS be at the top of the file, never embedded in code, and NEVER in a try: except: clause. They should always be grouped according to pep8 convention: standard library, thrid party, then project specific imports . Arrange alphabetically in each section
- imports should always be absolute, never relative. using relative imports creates problems when moving code around
- DO NOT USE try - except, unless under user specifically instructs you to and provides guidance for how to handle errors

### Inputs, typing, pydantic
- ALWAYS Use type hinting
- always use the native typing for python (i.e. list, str, tuple) NEVER (from typing import List, Tuple). This is completely unnecessary in modern versions of python, and is the sign of a junior dev.
- For complex inputs, use pydantic. 
    - Define an input schema (from pydatntic import BaseModel; class MyFuncModel(BaseModel))
- For more mature code, or code that has data structure issues, use pydantic to validate return and intermediate data structures
    - do not go overboard with this. Assess critically where validation is helpful to prevent runtime errors
- typing is not just a requirement - it is a way of development. Especially for complex problems, define what you expect the interfaces to be, make sure the code validates those interfaces. This is a form of test-driven-development that also happens to protect operations at runtime
- DO NOT write unit tests that simply replicate pydantic validation - though it is OK to write intergation tests that prove that interface assumptions hold over multiple steps
- Conversely: if you find yourself writing tests that assert a data structure has certain keys or shapes, that is a signal the code should use pydantic or TypedDict instead. Define the schema in code; do not test-assert your way to structural guarantees. The correct response is to add the schema, not the tests.

## javascript / frontend interfaces
How to decide between approaches, given no other instructions:
- do parts of the app need to react to other parts? (yes, use interactive)
- does the app rely on a backend api (yes, use interactive)

### Use bun
*ALWAYS* perfer `bun` as the JavaScript / Typscript tool kit: https://bun.com/docs
- if it isn't installed, ask the user to install it

### Simple interfaces in HTML
For visualizing simple outputs of scripts, processes, analyses, write HTML docs. You are free to use whatever style best fits the purpose
- include metadata about the styling notes in the HTML page as undisplayed elements. This helps future agents remain consistent when replicating a style
- the D3 vis library is a good place to start

### Interactive frontends in Svelte5
- if interactivity / reactivity is needed, use Svelte5
- When using Svelte 5, use the runes API ($state, $derived) and avoid legacy patterns.

## Scratch scripts and one-off validation

Never use `python -c "..."` with multiline inline code in the Bash tool — this triggers unnecessary approval prompts.

Instead:
- For throwaway checks: write a script to `tmp/` in the project root, then run it with a single-line `python tmp/script.py` command.
  - Create `tmp/` if it doesn't exist.
  - Ensure `tmp/` is in `.gitignore` — if it isn't, add it immediately.
- For durable checks that should survive beyond the session: add a test to the actual test suite instead.

## Docker
- if a project implies multiple services, setup or refactor to use docker compose
- ALWAYS use `docker compose` to run services, NEVER `docker-compose`
- If python services are required for, use `uv` to manage the python environment and installs in the DOCKERFILE. Have a step where you install uv to cache that layer, then a followup using `uv sync` to install the requirements

## Databases
- Tools available are Postgres and SQLite
- Prefer postgres for any sort of application with a frontend and backend
- Prefer postgres for any sort of cloud application service
- prefer SQLite for smaller applications

### Table and column conventions
- table names must be snake case (customer_orders NOT CustomerOrders)
- tables names are always the plural of the entity it represents (genes, proteins, domains ; not gene, protein, domain). This is because plurals are far less likely to conflict with keywords
- join tables are exactly the tables they join (proteins_domains)
- the PK of every table must be a UUID7 named id
- when writing a query with a PK, it must always be aliased to <table_name>_id
- FK ids must always be _exactly_ <table_name>_id . No exceptions
- name columns descriptively (fahrenheit instead of temperature)
- name columns in their data domain (`proteins.name` instead of `proteins.protein_name`)

### Migrations
- use a language appropriate package to manage migrations (i.e. alembic)
- migration versions must always be <YYMMDDHH>_<migration_title>

### Views vs tables
- tables: dogmatic > pragmatic . views: pragmatic > dogmatic
    - tables are for the data model, views are for the application function
- entity derived tables -> views are prefered to larger tables
- hide complexity in the application with views; let the tables be numberous and represent pure entities
- when designing tables for an application, application endpoints should have their own view that is usually the composite of other tables
- the intent is to have specific endpoints / views that pair with application fuction and let us optimize indvidual pages / functions, whereas the underlying data tables are optimized to represent the data model
- view naming and view column naming is much less strict -> should be pragmatic rather than dogmatic

## documentation
In general, documentation should capture intent, constraints, and non-obvious structure,
while leaving discoverable details to tools and inspection.

### Progressive disclosure

Follow a practice of progressive disclosure when writing documentation.

- Documentation is structured from the bottom up.
  - Lower levels contain exact, focused documentation that is specific and generally unconcerned with broader project context.
- Moving up levels (towards the repository root) increases context and intent, while decreasing implementation detail.
- Each level of the project (e.g., a directory) should document only what is true and knowable at that level, without assuming knowledge of sibling or parent directories.

Rules:
- Do not restate or duplicate detailed information that belongs to lower levels.
- When higher-level documentation needs to reference lower-level details, summarize intent and link or point downward instead of repeating content.
- If unsure whether information belongs at the current level, prefer omitting detail and deferring to a lower-level document.
- Do not summarize lower-level implementation details for convenience or completeness.

Self-check:
- Could this section be true even if the internal implementation changed?
- Does this document explain "why and how pieces fit" rather than "how something is implemented"?
- Is any paragraph more detailed than the documents beneath it?
- Would a reader be misled if this document were read without the documents beneath it?

### Tools vs static mapping
Policy:
- Do NOT write documentation that describes information that is trivially discoverable using standard tools.
- Prefer discovery over description for fast-changing structural information.
Proceedure:
- Use tools like `ls`, `la`, or `tree -L <depth>` to orient yourself, but do not transcribe their output into documentation.
- Do not encode the output of these tools directly into documentation.
Decision Test:
When deciding whether to document structure:
- Could this be determined by a quick inspection of the codebase?
  - If yes, do not document it.
  - If no, document it.

Examples:
- Do not list files or configurations in a directory.
- Do document architectural relationships or service boundaries.

Rationale:
Projects evolve continuously. Static descriptions of easily discoverable structure
become outdated quickly and create confusion. Documentation should focus on information
that requires synthesis, intent, or historical context rather than inspection.

### Documentation
- **Never fabricate empirical data.** examples: Runtime estimates, convergence curves, benchmark numbers, costs, wall time, concetrations, mass, and scaling figures must come from actual measurements 
- If empirical data is required by a documentation standard but has not been measured yet, write `[incomplete]` as a placeholder. Do not fill the gap with estimates.

## Test Writing

### Good tests
- test complicated logic
- test behavior of assumed inputs and handling of out of bounds inputs
- test the interface of two different systems by testing the interface of their types
- align with the concepts of the project, not the specifics of the implmentation
- allow for refactoring
- test suite is collectively fast (< 2 sec)

### bad tests
- filler tests to raise coverage
- simply test implementation
- would be better guarded by runtime asserts
- test connections that are already covered by robust typing
- assert data structure shape (key existence, nesting, field types) that should be enforced by pydantic, TypedDict, or dataclass definitions
- test suite takes longer than 2 seconds

