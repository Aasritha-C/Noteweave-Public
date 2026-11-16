"""Standalone Noteweave demo. Requires Python 3.10+ and its standard library."""
import json
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "public-demo.sqlite3"
HOST, PORT = "127.0.0.1", 8000
URL = f"http://{HOST}:{PORT}"
STATIC = {
    "/": ("extension/popup.html", "text/html; charset=utf-8"),
    "/popup.js": ("extension/popup.js", "text/javascript; charset=utf-8"),
}
NAME = r"[\w][\w '\u2019-]{0,99}?"
RULES = (
    ("IS_IN", re.compile(rf"({NAME})\s+(?:is\s+(?:located\s+)?in|lies\s+in)\s+({NAME})", re.I)),
    ("HOLDS", re.compile(rf"({NAME})\s+holds\s+({NAME})", re.I)),
    ("CONTAINS", re.compile(rf"({NAME})\s+contains\s+({NAME})", re.I)),
)
WHERE = re.compile(r"(?:where is|(?:which|what) room is)\s+(.+?)(?:\s+in)?\??", re.I)


def entity(text):
    text = re.sub(r"^(?:the|an?)\s+", "", text.strip(), flags=re.I)
    return " ".join(text.split()).title()


def initialize():
    DATA.parent.mkdir(exist_ok=True)
    with closing(sqlite3.connect(DATA)) as db, db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS facts (
                subject TEXT, predicate TEXT, object TEXT,
                PRIMARY KEY (subject, predicate, object)
            );
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY, text TEXT, created_at TEXT
            );
        """)
        db.executemany("INSERT OR IGNORE INTO facts VALUES (?, ?, ?)", [
            ("Demo Notebook", "IS_IN", "Demo Bag"),
            ("Demo Bag", "IS_IN", "Demo Lab"),
        ])


def fact(subject, predicate, target):
    return {"subject": subject, "predicate": predicate, "object": target}


def ingest(db, text):
    facts = []
    for sentence in re.split(r"[.!?\n]+", text):
        for predicate, rule in RULES:
            match = rule.fullmatch(sentence.strip())
            if match:
                facts.append((entity(match[1]), predicate, entity(match[2])))
                break
    db.executemany("INSERT OR IGNORE INTO facts VALUES (?, ?, ?)", facts)
    if not facts:
        return {"status": "data_deficient", "message": "Try a sentence such as The notebook is in the bag."}
    return {"status": "success", "triplets": [fact(*row) for row in facts]}


def lookup(db, subject):
    rows = db.execute(
        "SELECT subject, predicate, object FROM facts WHERE subject = ? ORDER BY predicate, object",
        (subject,),
    )
    return [fact(*row) for row in rows]


def location_answer(db, question):
    match = WHERE.fullmatch(question.strip())
    if not match:
        return {"status": "data_deficient", "message": "Try Where is Demo Notebook?"}
    anchor = entity(match[1])
    rows = db.execute("""
        SELECT first.subject, first.object, second.object
        FROM facts AS first
        LEFT JOIN facts AS second ON second.subject = first.object
            AND second.predicate = 'IS_IN'
            AND second.object <> first.subject AND second.object <> first.object
        WHERE first.subject = ? AND first.predicate = 'IS_IN'
            AND first.object <> first.subject
        ORDER BY first.object, second.object
    """, (anchor,))
    evidence = []
    for subject, middle, target in rows:
        path = [fact(subject, "IS_IN", middle)]
        if target is not None:
            path.append(fact(middle, "IS_IN", target))
        evidence.append(path)
    if not evidence:
        return {"status": "data_deficient", "message": f"No location facts for {anchor}."}
    return {
        "status": "success",
        "results": sorted({path[-1]["object"] for path in evidence}),
        "answer": "\n".join(
            " → ".join([anchor, *(edge["object"] for edge in path)]) for path in evidence
        ),
        "evidence_paths": evidence,
    }


class DemoHandler(BaseHTTPRequestHandler):
    def permitted(self):
        host = self.headers.get("Host", "")
        origin = self.headers.get("Origin")
        return host in {f"{HOST}:{PORT}", f"localhost:{PORT}"} and (
            origin is None
            or origin in {URL, f"http://localhost:{PORT}"}
            or re.fullmatch(r"chrome-extension://[a-p]{32}", origin) is not None
        )

    def respond(self, code, body=b"", content_type="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        origin = self.headers.get("Origin")
        if origin and self.permitted():
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)

    def json(self, payload, code=200):
        self.respond(code, json.dumps(payload).encode("utf-8"))

    def do_OPTIONS(self):
        self.respond(204 if self.permitted() else 403)

    def do_GET(self):
        if not self.permitted():
            return self.json({"status": "error"}, 403)
        url = urlsplit(self.path)
        if url.path in STATIC:
            path, mime = STATIC[url.path]
            return self.respond(200, (ROOT / path).read_bytes(), mime)
        if url.path == "/health":
            return self.json({"status": "ok", "service": "noteweave-public-demo"})
        with closing(sqlite3.connect(DATA)) as db:
            if url.path == "/query":
                question = parse_qs(url.query).get("q", [""])[0][:500]
                return self.json(location_answer(db, question))
            if url.path.startswith("/query/"):
                triplets = lookup(db, entity(unquote(url.path[len("/query/"):])))
                return self.json({"status": "success" if triplets else "data_deficient",
                                  "triplets": triplets})
            if url.path == "/notes":
                db.row_factory = sqlite3.Row
                rows = db.execute(
                    "SELECT id, text, created_at FROM notes ORDER BY created_at DESC, id DESC LIMIT 20"
                )
                return self.json({"notes": [dict(row) for row in rows]})
        return self.json({"status": "error", "message": "Unknown route."}, 404)

    def do_POST(self):
        if not self.permitted():
            return self.json({"status": "error"}, 403)
        route = urlsplit(self.path).path
        if route not in {"/ingest", "/notes"}:
            return self.json({"status": "error", "message": "Unknown route."}, 404)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 65000 or self.headers.get_content_type() != "application/json":
                raise ValueError
            payload = json.loads(self.rfile.read(size))
            text = payload.get("text") if isinstance(payload, dict) else None
        except (ValueError, UnicodeError, RecursionError):
            text = None
        limit = 5000 if route == "/notes" else 10000
        if not isinstance(text, str) or not text.strip() or len(text) > limit:
            return self.json({"status": "error", "message": f"Enter 1 to {limit} characters."}, 422)
        with closing(sqlite3.connect(DATA)) as db, db:
            if route == "/ingest":
                payload = ingest(db, text)
                code = 200
            else:
                payload = {"id": str(uuid4()), "text": text.strip(),
                           "created_at": datetime.now(timezone.utc).isoformat(timespec="microseconds")}
                db.execute("INSERT INTO notes VALUES (:id, :text, :created_at)", payload)
                code = 201
        return self.json(payload, code)


def main():
    try:
        with ThreadingHTTPServer((HOST, PORT), DemoHandler) as server:
            initialize()
            print(f"Noteweave public demo: {URL}", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    except OSError as error:
        raise SystemExit(f"Could not start Noteweave on {URL}. {error}") from error


if __name__ == "__main__":
    main()
