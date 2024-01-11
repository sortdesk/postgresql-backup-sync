"""base connector"""

from io import BytesIO
from os import environ
from pathlib import Path


class BaseConnector:
    """shared functionality"""

    FILES_TO_KEEP = int(environ.get("FILES_TO_KEEP", 0))

    def is_active(self) -> bool:
        """check if all needed env vars are set for connector"""

        raise NotImplementedError

    def save_backup(self, path: Path) -> None:
        """upload file from path object"""

        raise NotImplementedError

    def get_backups(self) -> list[str]:
        """return a list of available backups"""

        raise NotImplementedError

    def rotate_backups(self) -> None:
        """rotate remote backups"""

        raise NotImplementedError

    def get_backup_io(self, name: str | None) -> BytesIO:
        """return bytes IO object based on name or latest"""

        raise NotImplementedError
