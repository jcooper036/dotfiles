# grr-references
Minimal repro: `grr` on `api.auth.identity` returns only the definition. `src/api/app.py` uses it three times.

jedi (behind pylsp) scans the project in directory order and stops after parsing 30 files that contain the name. 40 files under `tests/` contain the word `identity` and are scanned before `src/`, so `src/api/app.py` is never reached.

```sh
M=~/.local/share/nvim/mason
python probe/lsp_refs.py $M/bin/pylsp . src/api/auth.py 4 5
$M/packages/python-lsp-server/venv/bin/python probe/jedi_limits.py .
$M/packages/python-lsp-server/venv/bin/python probe/jedi_order.py . src/api/auth.py 4 5
```

`lsp_refs.py` is the real pylsp response. `jedi_limits.py` shows 1 reference at the default limit and 4 with it lifted. `jedi_order.py` lists files in scan order.
