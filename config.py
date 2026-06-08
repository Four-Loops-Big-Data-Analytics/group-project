from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RECORDINGS_DIR = PROJECT_ROOT / "recordings"
REPORTS_DIR = PROJECT_ROOT / "reports"

# build all directories in config so we know they're there
for dir in [DATA_DIR, RECORDINGS_DIR, REPORTS_DIR]:
    dir.mkdir(parents=True, exist_ok=True)