# Download, manifest, and CSV helpers shared by the ingest modules.

import codecs
import csv
import hashlib
import io
import logging
import subprocess
from datetime import UTC, datetime

import pandas as pd

from ingest.http import fetch, require_ok
from ingest.paths import EXTRACTS

log = logging.getLogger("sources")

WADEFAGEN_REPO = "https://github.com/wadefagen/datasets.git"
MANIFEST = EXTRACTS / "manifest.csv"
MANIFEST_COLUMNS = [
    "source",
    "url",
    "retrieved_utc",
    "last_modified",
    "etag",
    "bytes",
    "sha256",
    "file_used",
]


def download(session, url, dest, source):
    response = fetch(session, url)
    content = require_ok(response)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    log.info("%s: %d bytes", source, len(content))
    return {
        "source": source,
        "url": url,
        "retrieved_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_modified": response.headers.get("Last-Modified", ""),
        "etag": response.headers.get("ETag", ""),
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def update_manifest(new_rows):
    rows = {}
    if MANIFEST.exists():
        with MANIFEST.open(newline="") as f:
            rows = {row["source"]: row for row in csv.DictReader(f)}
    rows.update({row["source"]: row for row in new_rows})
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows[source] for source in sorted(rows))


def github_head(repo_url):
    result = subprocess.run(
        ["git", "ls-remote", repo_url, "HEAD"], check=True, capture_output=True, text=True
    )
    sha = result.stdout.split()[0]
    assert len(sha) == 40, f"unexpected git ls-remote output: {result.stdout!r}"
    return sha


def wadefagen_url(commit, path):
    # Pinned to a commit, so the manifest's URL says exactly which version was read.
    return f"https://raw.githubusercontent.com/wadefagen/datasets/{commit}/{path}"


def decode_text(raw):
    # UTF-8, except that a line which isn't is read as Windows-1252. The GPA dataset's Oct 29, 2026
    # update put two Windows-1252 rows in an otherwise UTF-8 file, and decoding the whole file
    # one way would garble the other.
    raw = raw.removeprefix(codecs.BOM_UTF8)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        pass
    lines, fallback = [], 0
    for line in raw.split(b"\n"):
        try:
            lines.append(line.decode("utf-8"))
        except UnicodeDecodeError:
            lines.append(line.decode("cp1252", errors="replace"))
            fallback += 1
    log.warning("%d lines were not UTF-8 and were read as Windows-1252", fallback)
    return "\n".join(lines)


def read_text_csv(raw):
    # Every column stays text so nothing is coerced on the way in; typing happens in dbt.
    return pd.read_csv(io.StringIO(decode_text(raw)), dtype=str, keep_default_na=False)
