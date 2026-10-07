import sys
from pathlib import Path

import jedi
from jedi.inference import references as r

root = Path(sys.argv[1])
rel, line, col = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
orig = r._check_fs
seen = []

def spy(inference_state, file_io, regex):
    m = orig(inference_state, file_io, regex)
    seen.append((str(file_io.path).replace(str(root), ""), m is not None))
    return m

r._check_fs = spy
jedi.Script(path=str(root / rel), project=jedi.Project(str(root))).get_references(line, col)
hits = 0
for i, (p, matched) in enumerate(seen):
    hits += matched
    print(i, hits, "M" if matched else "-", p)
print("sys_path head:", jedi.Project(str(root)).get_environment().get_sys_path()[:3])
