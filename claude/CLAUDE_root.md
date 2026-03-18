# User persona
The user you are interacting with is named Jacob. He is a data scientist with broad experience in data science, software engineering, and has a Ph.D focused on genetics, genomics, molecular bio, and cell bio. He has the most experience with writing in python and sql. He is very curious and eager to learn. For coding, he loves to learn new languages, tools, and packages - he is always interested in learning and using the best tool for the job. 

# Coding

## All programming
- no function should be longer than 60 lines of code. If it is, refactor
- large if / elif / else statements are generally an anti-pattern, and demonstrate that something is wrong (lacking generalization, parameterizations, encapsulation, etc.)
- functions should contain at a minimum one assertion per 20 lines of code that guard against cases that should never happen
- whever language you are in, use type hinting on inputs and outputs
- always 0 index counters

## Comments
Take the attitude that comments are to be used lightly. Comments are tech debt for two reasons:
- they imply constraints without enforcing them
- they only claim to know what the code is / should be doing - but the code is the authoritative source of what it is doing

When you must use them:
- First drafts should almost never have comments
- Comments should only be used when code has already caused confusion
- Comments should NEVER contain numbered steps

**Documentation** is still ok - comments are suspect because of their proximity to the code

## Git and github
- ALWAYS use the `gh` tool to interact with github
- if the tool is missing, stop and walk the user through setup
- if auth doesn't work, try running `load_secrets` (user alias for loading env secrets) and try again
    - if it still doesn't work, or that alias doesn't exist, prompt the user to fix 

### versioning
- if any type of versioning exists, all branches need to progress the version.
- always use semantic versioning <breaking change>.<major feature>.<minor feature / bugfix>
- major features are any that are visible to a user
    - but you MUST interpret this in the context of the project
- breaking changes mean that the new version will no longer be compatible with old versions
    - again must interpret this in the context of the project
- error on the side of declaring a bigger change than a smaller one
- look for versioning information in the language appropriate locations (pyproject.toml for python)

## git hygene
- before doing any git operations, check what branch you are on
- never git add or git commit or git push to the "trunk" or "main" branch unless explicity approved to do so
- instead, if you find yourself on one of those branches, make a new branch for the current changes first
### writing commits
- always start your commit messagees with "claude: ..."
### creating PRs
- ALWAYS check if there is a PR template in the project in the .github folder - make sure to include the requiremetns of that template in your PRs
- you may (and usually should) add additional detail based on the complexity of the PR. You are free to format that however is best given the nature of the change.
- very simple changes should have short PR messages, longer changes can have more complicated messages

## Python
- ALWAYS follow pep8 conventions
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
- ALWAYS make sure there is a /tests file in a project for storing tests, run this with `pytest`
- ALWAYS run `ruff check . --fix` after adding or editing python files to make sure they are format complient
- ALWAYS run `mypy` (exactly that command, don't add arguments). it MUST complete with no errors in less than 5 seconds
- always prefer `structlog` over the standard library logging module. Don't use print statements for logging, ever, use structlog
- use `tqdm` for progress bars, never custom implementations
- imports should ALWAYS be at the top of the file, never embedded in code, and NEVER in a try: except: clause. They should always be grouped according to pep8 convention: standard library, thrid party, then project specific imports . Arrange alphabetically in each section
- imports should always be absolute, never relative. using relative imports creates problems when moving code around
- Use try - except as sparingly as possible. You should only ever use it when interfacting with external services, and that service should be wrapped in a contained interface. Most logic functions should never have a try except, only specifically service interface functions

## Docker
- if a project implies multiple services, setup or refactor to use docker compose
- ALWAYS use `docker compose` to run services, NEVER `docker-compose`
- If python services are required for, use `uv` to manage the python environment and installs in the DOCKERFILE. Have a step where you install uv to cache that layer, then a followup using `uv sync` to install the requirements

## testing
- write tests, but only write _good_ tests. Do not write filler tests. There is no expectation for test coverage, but there is an expectation that you use tests to speed up and harden development.

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

### Documentation honesty
- **Never fabricate empirical data.** examples: Runtime estimates, convergence curves, benchmark numbers, costs, wall time, concetrations, mass, and scaling figures must come from actual measurements 
- If empirical data is required by a documentation standard but has not been measured yet, write `[incomplete]` as a placeholder. Do not fill the gap with estimates.

## Test Writing
### Good tests
- test complicated logic
- test behavior of assumed inputs and handling of out of bounds inputs
- test the interface of two different systems by testing the interface of their types
- align with the concepts of the project, not the specifics of the implmentation
- allow for refactoring
- are collectively fast (< 2 sec)

### bad tests
- filler tests to raise coverage
- simply test implementation
- would be better guarded by runtime asserts
- test connections that are already covered by robust typing
- are collectively slow (> 2 sec)
