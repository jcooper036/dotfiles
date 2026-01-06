# User persona
The user you are interacting with is named Jacob. He is a data scientist with broad experience in data science, software engineering, and has a Ph.D focused on genetics, genomics, molecular bio, and cell bio. He has the most experience with writing in python and sql. He is very curious and eager to learn. For coding, he loves to learn new languages, tools, and packages - he is always interested in learning and using the best tool for the job. 

# Coding
## All programming
- no function should be longer than 60 lines of code. If it is, refactor
- large if / elif / else statements are generally an anti-pattern, and demonstrate that something is wrong (lacking generalization, parameterizations, encapsulation, etc.)
- functions should contain at a minimum one assertion per 20 lines of code that guard against cases that should never happen
- whever language you are in, use type hinting on inputs and outputs
- always 0 index counters
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
