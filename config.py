"""Centralized filesystem configuration for the inventory system."""

from pathlib import Path


BASE_DIR: Path = Path(__file__).resolve().parent
STORAGE_DIR: Path = BASE_DIR / "storage"
DATABASE_PATH: Path = STORAGE_DIR / "database.json"
REPORTS_DIR: Path = BASE_DIR / "reports"
LOGS_DIR: Path = BASE_DIR / "logs"


for directory in (STORAGE_DIR, REPORTS_DIR, LOGS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
