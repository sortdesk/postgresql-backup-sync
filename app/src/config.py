"""config handling"""

from datetime import datetime
from os import environ
from pathlib import Path

DB_USER = environ.get("POSTGRES_USER")
DB_PW = environ.get("POSTGRES_PASSWORD")
DB_HOST = environ.get("POSTGRES_HOST")
DB_PORT = environ.get("POSTGRES_PORT", 5432)
DB_NAME = environ.get("POSTGRES_DB")
BACKUP_FOLDER = "/backup"


def get_connection_str() -> str:
    """get connection string for PG from env vars"""

    return f"postgres://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_backup_path() -> Path:
    """build path object from timestamp"""

    time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return Path(BACKUP_FOLDER) / f"{DB_HOST}_{time_stamp}.gz"


def get_local_backups() -> list[Path]:
    """get available local backup files"""

    folder = Path(BACKUP_FOLDER)
    local_files = list(folder.glob("**/*.gz"))
    local_files.sort()

    return local_files
