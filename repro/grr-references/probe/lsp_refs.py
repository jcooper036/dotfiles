import json
import subprocess
import sys
from pathlib import Path


def send(proc: subprocess.Popen, msg: dict) -> None:
    body = json.dumps(msg).encode()
    proc.stdin.write(b"Content-Length: %d\r\n\r\n" % len(body) + body)
    proc.stdin.flush()


def read(proc: subprocess.Popen) -> dict:
    length = 0
    while (line := proc.stdout.readline().strip()):
        if line.lower().startswith(b"content-length"):
            length = int(line.split(b":")[1])
    return json.loads(proc.stdout.read(length))


def request(proc: subprocess.Popen, id_: int, method: str, params: dict) -> dict:
    send(proc, {"jsonrpc": "2.0", "id": id_, "method": method, "params": params})
    while (msg := read(proc)).get("id") != id_ or "method" in msg:
        if "method" in msg and "id" in msg:
            send(proc, {"jsonrpc": "2.0", "id": msg["id"], "result": None})
    return msg


def main(cmd: str, root: str, file: str, line: int, col: int) -> None:
    proc = subprocess.Popen([cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    root_uri = Path(root).resolve().as_uri()
    request(proc, 1, "initialize", {"processId": None, "rootUri": root_uri, "capabilities": {}})
    send(proc, {"jsonrpc": "2.0", "method": "initialized", "params": {}})
    path = Path(root).resolve() / file
    uri = path.as_uri()
    send(proc, {"jsonrpc": "2.0", "method": "textDocument/didOpen", "params": {"textDocument": {"uri": uri, "languageId": "python", "version": 1, "text": path.read_text()}}})
    res = request(proc, 2, "textDocument/references", {"textDocument": {"uri": uri}, "position": {"line": line - 1, "character": col}, "context": {"includeDeclaration": True}})
    locs = res.get("result") or []
    for loc in sorted(locs, key=lambda l: (l["uri"], l["range"]["start"]["line"])):
        print(loc["uri"].replace(root_uri, "") + ":" + str(loc["range"]["start"]["line"] + 1))
    print("total", len(locs))
    proc.kill()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
