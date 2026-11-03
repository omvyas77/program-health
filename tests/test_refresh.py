import codecs
import csv

from ingest import refresh, sources
from ingest.paths import ROOT

MANIFEST = {
    row["source"]: row for row in csv.DictReader((ROOT / "data/extracts/manifest.csv").open())
}


def headers(source):
    row = MANIFEST[source]
    return {"Last-Modified": row["last_modified"], "ETag": row["etag"]}


def test_a_file_differs_only_when_its_headers_do():
    adm = MANIFEST["ipeds/ADM2024.zip"]
    assert not refresh.differs(adm, headers("ipeds/ADM2024.zip"))
    # The dictionary zip was published a day earlier with its own ETag.
    assert refresh.differs(adm, headers("ipeds/ADM2024_Dict.zip"))


def test_github_raw_files_compare_on_etag_alone():
    gpa = MANIFEST["gpa/uiuc-gpa-dataset.csv"]
    assert gpa["last_modified"] == ""
    assert not refresh.differs(gpa, {"ETag": gpa["etag"]})


def test_next_ipeds_files_follow_each_family():
    assert refresh.next_ipeds_names(refresh.read_ipeds_files()) == [
        "ADM2025",
        "C2026_A",
        "EF2025A_DIST",
        "EF2025D",
        "EF2026CP",
        "GR2025",
        "GR2025_PELL_SSL",
        "HD2026",
    ]


def test_snapshot_requirements_pin_the_same_versions():
    def pins(name):
        lines = (ROOT / name).read_text().split()
        return dict(line.split("==") for line in lines)

    main, snapshot = pins("requirements.txt"), pins("requirements-snapshot.txt")
    assert {package: main.get(package) for package in snapshot} == snapshot


def test_a_csv_with_a_few_windows_1252_lines_still_reads():
    raw = (
        codecs.BOM_UTF8
        + b"Subject,Course Title\n"
        + "ACCY,Café Économie\n".encode()
        + "SPAN,Política y sociedad\n".encode("cp1252")
    )
    data = sources.read_text_csv(raw)
    assert list(data.columns) == ["Subject", "Course Title"]
    assert list(data["Course Title"]) == ["Café Économie", "Política y sociedad"]
