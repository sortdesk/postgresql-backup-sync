# backup to local storage

import gzip
import os
import subprocess
from pathlib import Path

from src.config import get_backup_path, get_connection_str, get_local_backups


def run_local_backup() -> Path:
    print("run local backup")

    backup_path = get_backup_path()
    connection_str = get_connection_str()

    with gzip.open(backup_path, "wb") as f:
        popen = subprocess.Popen(["pg_dump", connection_str], stdout=subprocess.PIPE, universal_newlines=True)

        for stdout_line in iter(popen.stdout.readline, ""):
            f.write(stdout_line.encode("utf-8"))

        popen.stdout.close()
        popen.wait()

    print(f"created local backup at {backup_path}")

    return backup_path


def rotate_local_backup() -> None:
    """remove old local backups"""

    print("rotating local backups")

    files_to_keep = int(os.environ.get("FILES_TO_KEEP", 0))

    if not files_to_keep:
        return

    local_backups: list[Path] = get_local_backups()
    if not local_backups:
        return

    to_delete = local_backups[:-files_to_keep]
    if not to_delete:
        return

    print(f"deleting {len(to_delete)} local files")

    for path in to_delete:
        path.unlink()
