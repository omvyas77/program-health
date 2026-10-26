from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
RAW = ROOT / "data" / "raw"
EXTRACTS = ROOT / "data" / "extracts"
SNAPSHOTS = ROOT / "data" / "snapshots" / "cis"
STATUS_SNAPSHOTS = ROOT / "data" / "snapshots" / "cis_status"
TRANSFORM = ROOT / "transform"
WAREHOUSE = ROOT / "warehouse" / "gph.duckdb"
DOCS = ROOT / "docs"
MARTS = ROOT / "data" / "marts"
