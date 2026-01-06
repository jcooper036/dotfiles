## When working in Python Projects
- use uv for python managment (`uv add <package>`, `uv sync`)
- configure the project via pyproject.toml. If this doesn't exit, STOP and ask the user what to do
- always use type hints. HOWEVER, do not use the `typing` module for builtin types like list, dict, str, etc. You are usually working in python 3.12+
- put tests in `./tests`. Tests are written with the `pytest` framework and are configured in `pyproject.toml`

## Testing
Aim for good tests, not just test coverage.
### Good tests

### Bad tests
