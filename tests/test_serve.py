"""The upload app: the pipeline behind one request, and the HTTP layer.

  python3 -m unittest discover tests
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "skills", "reverse-engineer-tests", "scripts"))

import serve  # noqa: E402


def demo_payload():
    """Four synthetic papers with keys (the demo exam: longest choice is
    right far above chance)."""
    d = tempfile.mkdtemp()
    subprocess.run([sys.executable, os.path.join(ROOT, "examples", "make_demo.py"), d],
                   check=True, capture_output=True)
    part = lambda name: {"name": name, "data": base64.b64encode(
        open(os.path.join(d, name), "rb").read()).decode()}
    return {"exam": "Demo exam",
            "samples": [{"paper": part(f"form{i}.txt"), "key": part(f"key{i}.txt")}
                        for i in range(1, 5)]}


class Crack(unittest.TestCase):
    def test_full_report_from_uploaded_papers(self):
        out = serve.crack(demo_payload())
        self.assertEqual(out["usable"], 160)
        self.assertEqual([p["usable"] for p in out["papers"]], [40] * 4)
        rep = out["report"]
        self.assertEqual(rep["title"], "Demo exam")
        self.assertTrue(rep["all"]["established"])
        self.assertIn("Favour", [r["verb"] for r in rep["rules"]])
        self.assertIn("**Favour** the longest choice", out["markdown"])
        json.dumps(out)  # the whole response must be JSON-serializable

    def test_paper_without_any_key_is_explained_not_crashed(self):
        p = demo_payload()
        for s in p["samples"]:
            s["key"] = None
        out = serve.crack(p)
        self.assertIsNone(out["report"])
        self.assertIn("answer key", out["problem"])

    def test_refuses_other_file_types_and_empty_requests(self):
        with self.assertRaises(serve.Refused):
            serve.crack({"samples": [{"paper": {"name": "run.sh", "data": ""}}]})
        with self.assertRaises(serve.Refused):
            serve.crack({"samples": []})

    def test_uploaded_names_never_become_paths(self):
        p = demo_payload()
        p["samples"][0]["paper"]["name"] = "../../../../tmp/escape.txt"
        out = serve.crack(p)
        self.assertEqual(out["usable"], 160)
        self.assertFalse(os.path.exists("/tmp/escape.txt"))


class Http(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), serve.Handler)
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def post(self, body):
        req = urllib.request.Request(self.base + "/api/crack", data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    def test_page_is_served(self):
        with urllib.request.urlopen(self.base + "/") as r:
            self.assertIn(b"<title>", r.read())

    def test_post_returns_the_report(self):
        code, out = self.post(json.dumps(demo_payload()).encode())
        self.assertEqual(code, 200)
        self.assertEqual(out["usable"], 160)

    def test_bad_requests_get_a_plain_message(self):
        code, out = self.post(b"not json")
        self.assertEqual(code, 400)
        self.assertNotIn("Traceback", out["error"])


if __name__ == "__main__":
    unittest.main()
