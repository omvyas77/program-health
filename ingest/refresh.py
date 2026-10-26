# Weekly refresh, first step: decide which sources changed since data/extracts/manifest.csv was
# written, rerun the ingest for those only, and list files that have newly appeared upstream.
# A HEAD request comes first; when its Last-Modified or ETag differs from the manifest's, the file
# is downloaded and checked. An IPEDS file counts as changed only if the peer rows it yields (or,
# for a dictionary, its title and release line) differ from what is committed: NCES serves copies
# of the same file zipped at different times to different networks, so neither headers nor zip
# bytes settle it (HD2024 on Oct 25, 2026). Other files count as changed when their SHA-256
# differs. New files are listed, not ingested: a new IPEDS year needs its
# dictionary read and a new catalog term needs a code change, so both
# wait for a person. Writes a JSON summary for the workflow's later steps.

import argparse
import csv
import hashlib
import json
import logging
import sys
import tempfile
from pathlib import Path

import pandas as pd

from ingest import catalog, gpa, ipeds, tre, wiche
from ingest.http import fetch, new_session, require_ok
from ingest.paths import CONFIG
from ingest.sources import MANIFEST, WADEFAGEN_REPO, github_head, wadefagen_url

log = logging.getLogger("refresh")

IPEDS_FOLDER = "https://nces.ed.gov/ipeds/complete-data-files"
CATALOG_LISTING = "https://api.github.com/repos/wadefagen/datasets/contents/course-catalog/data"
# How each IPEDS family names its files, and how many years apart they come (EF CP is reported
# in even years only).
IPEDS_NAMES = {
    "hd": ("HD{y}", 1),
    "adm": ("ADM{y}", 1),
    "ef_d": ("EF{y}D", 1),
    "gr": ("GR{y}", 1),
    "gr_pell": ("GR{y}_PELL_SSL", 1),
    "c_a": ("C{y}_A", 1),
    "ef_cp": ("EF{y}CP", 2),
    "ef_dist": ("EF{y}A_DIST", 1),
}
# Sources the refresh can't check: the DMI pages are frozen Internet Archive captures, and the
# DAIR crosstabs and Common Data Set files are downloaded by hand (docs/runbook.md).
MANUAL = ["dmi", "dair", "cds"]


def read_manifest():
    with MANIFEST.open(newline="") as f:
        return {row["source"]: row for row in csv.DictReader(f)}


def differs(row, headers):
    return (headers.get("Last-Modified", ""), headers.get("ETag", "")) != (
        row["last_modified"],
        row["etag"],
    )


def head(session, url):
    response = fetch(session, url, method="HEAD")
    assert response.status_code == 200, f"{url}: HTTP {response.status_code}"
    return response.headers


def content_differs(session, url, source, row):
    content = require_ok(fetch(session, url))
    return hashlib.sha256(content).hexdigest() != row["sha256"]


def ipeds_extract_differs(session, url, source, row):
    name = Path(source).stem
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / Path(source).name
        path.write_bytes(require_ok(fetch(session, url)))
        if name.endswith("_Dict"):
            dictionary = ipeds.read_dictionary(path)
            with ipeds.DICTIONARY_TITLES.open(newline="") as f:
                stored = {r["file"]: r for r in csv.DictReader(f)}[name.removesuffix("_Dict")]
            return (str(dictionary["title"]), str(dictionary["release"])) != (
                stored["title"],
                stored["release"],
            )
        _, _, _, kept = ipeds.peer_rows(path, ipeds.read_peer_unitids())
    return not kept.equals(pd.read_parquet(ipeds.EXTRACTS_IPEDS / f"{name}.parquet"))


def changed_files(session, manifest, prefix, url_for, confirm=content_differs):
    changed = []
    for source, row in manifest.items():
        if not source.startswith(prefix):
            continue
        url = url_for(source, row)
        if differs(row, head(session, url)):
            if confirm(session, url, source, row):
                log.info("%s changed", source)
                changed.append(source)
            else:
                log.info("%s: new headers, same content", source)
    return changed


def check_wadefagen(session, manifest):
    # The manifest's URLs pin the commit that was read; the same paths at the current commit
    # return an ETag that is a hash of the content, so unchanged files match.
    commit = github_head(WADEFAGEN_REPO)

    def at_head(source, row):
        return wadefagen_url(commit, source)

    return {
        "gpa": changed_files(session, manifest, "gpa/", at_head),
        "tre": changed_files(session, manifest, "teachers-ranked-as-excellent/", at_head),
        "catalog": changed_files(session, manifest, "course-catalog/", at_head),
    }


def new_catalog_terms(session, manifest):
    response = fetch(session, CATALOG_LISTING)
    assert response.status_code == 200, f"{CATALOG_LISTING}: HTTP {response.status_code}"
    upstream = {f"course-catalog/data/{item['name']}" for item in response.json()}
    known = {source for source in manifest if source.startswith("course-catalog/")}
    return sorted(source.rsplit("/", 1)[1] for source in upstream - known)


def next_ipeds_names(files):
    latest = {}
    for row in files:
        year = int("".join(ch for ch in row["file"] if ch.isdigit())[:4])
        latest[row["family"]] = max(latest.get(row["family"], 0), year)
    names = []
    for family, year in sorted(latest.items()):
        pattern, step = IPEDS_NAMES[family]
        names.append(pattern.format(y=year + step))
    return sorted(names)


def new_ipeds_files(session, files):
    found = []
    for name in next_ipeds_names(files):
        response = fetch(session, f"{IPEDS_FOLDER}/{name}.zip", method="HEAD")
        if response.status_code == 200:
            log.info("new IPEDS file: %s", name)
            found.append(name)
        else:
            assert response.status_code == 404, f"{name}: HTTP {response.status_code}"
    return found


def read_ipeds_files():
    with (CONFIG / "ipeds_files.csv").open(newline="") as f:
        return list(csv.DictReader(f))


def check(session):
    manifest = read_manifest()
    files = read_ipeds_files()
    changed = {
        "ipeds": changed_files(
            session, manifest, "ipeds/", lambda source, row: row["url"], ipeds_extract_differs
        ),
        "wiche": changed_files(session, manifest, "wiche/", lambda source, row: row["url"]),
    } | check_wadefagen(session, manifest)
    return {
        "changed": {source: files for source, files in changed.items() if files},
        "new_ipeds_files": new_ipeds_files(session, files),
        "new_catalog_terms": new_catalog_terms(session, manifest),
        "manual": MANUAL,
        "checked": sum(1 for source in manifest if source.split("/")[0] not in MANUAL),
    }


def ingest(changed):
    if "ipeds" in changed:
        # The runner starts without data/raw, so the extract step needs every file downloaded.
        ipeds.download_dictionaries()
        ipeds.download_data()
        ipeds.extract_all()
    for source, module in (("gpa", gpa), ("tre", tre), ("catalog", catalog), ("wiche", wiche)):
        if source in changed:
            module.main()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="where to write the JSON summary")
    parser.add_argument("--check-only", action="store_true", help="detect changes, ingest nothing")
    args = parser.parse_args()
    summary = check(new_session())
    log.info(
        "%d sources checked; changed: %s; new IPEDS files: %s; new catalog terms: %s",
        summary["checked"],
        ", ".join(summary["changed"]) or "none",
        ", ".join(summary["new_ipeds_files"]) or "none",
        ", ".join(summary["new_catalog_terms"]) or "none",
    )
    if not args.check_only:
        ingest(summary["changed"])
    with open(args.out, "w") as f:
        json.dump(summary, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
