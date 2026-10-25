# Writes every dbt mart to data/marts as parquet and csv, sorted so reruns on unchanged data give
# unchanged files. The Streamlit app reads these; mart_projection is written by forecast/.
# Names on the command line export only those marts, as the daily snapshot job does.

import argparse
import logging
import sys

import duckdb

from ingest.paths import MARTS, ROOT, TRANSFORM, WAREHOUSE

log = logging.getLogger("export")


def mart_names():
    names = sorted(p.stem for p in (TRANSFORM / "models" / "marts").glob("mart_*.sql"))
    assert names, "no mart models found"
    return names


def export(con, name):
    expected = con.sql(f"select count(*) from {name}").fetchone()[0]
    parquet, csv = MARTS / f"{name}.parquet", MARTS / f"{name}.csv"
    con.sql(f"copy (select * from {name} order by all) to '{parquet}' (format parquet)")
    con.sql(f"copy (select * from {name} order by all) to '{csv}' (header, delimiter ',')")
    for path, reader in ((parquet, "read_parquet"), (csv, "read_csv")):
        written = con.sql(f"select count(*) from {reader}('{path}')").fetchone()[0]
        assert written == expected, f"{path.name}: wrote {written} rows, mart has {expected}"
    log.info("%s: %d rows", name, expected)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("marts", nargs="*", help="marts to export; every mart if none")
    names = parser.parse_args().marts or mart_names()
    unknown = sorted(set(names) - set(mart_names()))
    assert not unknown, f"not dbt marts: {unknown}"
    MARTS.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    for name in names:
        export(con, name)
    log.info("wrote %s", MARTS.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
