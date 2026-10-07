import sys
from pathlib import Path

import jedi
from jedi.inference import references

root = Path(sys.argv[1])
target = root / "src/api/auth.py"
for parsed in (references._PARSED_FILE_LIMIT, 100000):
    references._PARSED_FILE_LIMIT = parsed
    refs = jedi.Script(path=str(target), project=jedi.Project(str(root))).get_references(4, 5)
    print("parsed limit", parsed, "->", sorted({(r.module_path.name, r.line) for r in refs}))
