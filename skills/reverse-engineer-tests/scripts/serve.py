#!/usr/bin/env python3
"""
serve.py: a local web page for the whole pipeline. Drop past papers and their
answer keys, get the report.

  python3 serve.py [--port 8765] [--host 127.0.0.1]     (or: ret.py serve)

then open http://127.0.0.1:8765

How it handles files: each upload is written to a temporary folder, parsed
with the `auto` adapter, analyzed, and the folder is deleted before the
response is sent. Nothing is kept and nothing is sent anywhere else.

It listens on 127.0.0.1 only unless you pass --host. Before putting it on a
public address (the Dockerfile does this with --host 0.0.0.0), put it behind
something that adds sign-in and rate limits: this server has neither.

Standard library only.
"""
import base64
import json
import os
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from adapters import ADAPTERS  # noqa: E402
from report import analyze, render  # noqa: E402
from validate_items import validate  # noqa: E402

UI = os.path.join(HERE, "..", "assets", "ui.html")
MAX_BODY = 80 * 1024 * 1024   # about 60 MB of files once base64 is undone
MAX_SAMPLES = 60
EXTENSIONS = (".pdf", ".docx", ".txt", ".md")


class Refused(Exception):
    """A problem the person uploading can fix; the message is shown to them."""


def _save(folder, stem, part):
    """Write one uploaded file under a name we choose. Only the extension of
    the uploaded name is used, and only if it is on the allowed list."""
    ext = os.path.splitext(str(part.get("name") or ""))[1].lower()
    if ext not in EXTENSIONS:
        raise Refused(f"\"{part.get('name')}\" is not a PDF, Word (.docx) or text file.")
    try:
        data = base64.b64decode(part.get("data") or "", validate=True)
    except Exception:
        raise Refused(f"\"{part.get('name')}\" did not upload correctly. Try again.")
    path = os.path.join(folder, stem + ext)
    with open(path, "wb") as f:
        f.write(data)
    return path


def crack(payload):
    """The whole pipeline for one request. -> a JSON-ready dict."""
    samples = payload.get("samples") or []
    if not samples:
        raise Refused("Add at least one paper.")
    if len(samples) > MAX_SAMPLES:
        raise Refused(f"That is {len(samples)} papers; the limit is {MAX_SAMPLES} at a time.")
    exam = (str(payload.get("exam") or "").strip() or "This exam")[:80]
    items, log, papers = [], [], []
    with tempfile.TemporaryDirectory(prefix="ret-") as folder:
        for n, s in enumerate(samples, 1):
            form = f"P{n}"
            name = str((s.get("paper") or {}).get("name") or form)
            inputs = [_save(folder, f"paper{n}", s.get("paper") or {})]
            if s.get("key"):
                inputs.append(_save(folder, f"key{n}", s["key"]))
            opts = {"exam": exam}
            try:
                got = ADAPTERS["auto"].parse(inputs, form, opts)
            except (Exception, SystemExit) as e:
                got, opts["log"] = [], [f"{form}: could not be read ({type(e).__name__})."]
            usable = sum(1 for i in got if len(i["choices"]) >= 3 and i["answer"] in i["choices"])
            papers.append({"form": form, "name": name[:120], "found": len(got), "usable": usable})
            log += [l.replace(form + ":", name[:60] + ":", 1) for l in opts.get("log", [])]
            items += got
    usable = sum(p["usable"] for p in papers)
    out = {"exam": exam, "papers": papers, "log": log, "usable": usable, "report": None}
    if not usable:
        out["problem"] = ("No question could be matched to a key answer. Check that each "
                          "paper has its answer key, and that PDFs contain real text "
                          "(a scanned PDF needs OCR first).")
        return out
    flags = validate(items)[1]
    out["flags"] = {k: len(v) for k, v in flags.items() if v and k != "no-answer"}
    out["report"] = analyze(items)
    out["markdown"] = render(out["report"])
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "ret"

    def _send(self, code, body, kind="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", kind + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, open(UI, "rb").read(), "text/html")
        elif self.path == "/healthz":
            self._send(200, {"ok": True})
        else:
            self._send(404, {"error": "Not found."})

    def do_POST(self):
        if self.path != "/api/crack":
            return self._send(404, {"error": "Not found."})
        try:
            size = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            size = 0
        if size <= 0 or size > MAX_BODY:
            return self._send(413, {"error": "That upload is too large. The limit is about "
                                             "60 MB in total; send fewer papers at a time."})
        try:
            payload = json.loads(self.rfile.read(size))
            self._send(200, crack(payload))
        except Refused as e:
            self._send(400, {"error": str(e)})
        except json.JSONDecodeError:
            self._send(400, {"error": "The upload was not understood. Reload the page and try again."})
        except Exception as e:  # never leak a traceback to the page
            sys.stderr.write(f"crack failed: {type(e).__name__}: {e}\n")
            self._send(500, {"error": "The analysis failed on these files. The terminal "
                                      "running the server shows the cause."})

    def log_message(self, fmt, *args):  # one quiet line per request, no file names
        sys.stderr.write("%s %s\n" % (self.command, self.path))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    val = lambda name, d: argv[argv.index(name) + 1] if name in argv else d
    host = val("--host", "127.0.0.1")
    port = int(val("--port", os.environ.get("PORT", 8765)))
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Upload page: http://{'127.0.0.1' if host in ('0.0.0.0', '') else host}:{port}")
    print("Files are analyzed on this machine and deleted after each request. Ctrl+C stops.")
    if host not in ("127.0.0.1", "localhost"):
        print("WARNING: listening on a network address with no sign-in and no rate limit.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
