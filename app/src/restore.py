"""restore backup file"""

import gzip
import subprocess
from io import BytesIO

from src.config import get_connection_str, get_local_backups
from src.connector.amazon import AmazonS3Connector
from src.connector.azure import AzureConnector


class Restore:
    """handle restore functionality"""

    def __init__(self, name: str | None = None, source: str | None = None) -> None:
        self.name = name
        self.source = source

    def get_backup_io(self) -> BytesIO:
        """prepare backup file to restore"""
        if not self.source:
            to_restore = self._get_local()

        elif self.source == "azure":
            to_restore = self._get_azure()

        elif self.source == "s3":
            to_restore = self._get_s3()

        return to_restore

    def _get_local(self) -> BytesIO:
        """get local bytes IO object"""
        local_backups = get_local_backups()
        if not local_backups:
            raise FileNotFoundError("didn't find any local backup files")

        if self.name:
            matches = [i for i in local_backups if self.name in i.name]
            if not matches:
                raise FileNotFoundError(f"didn't find local file with name {self.name}")
            path = matches[0]
        else:
            path = local_backups[-1]

        with open(path, "rb") as file:
            file_content = file.read()

        return BytesIO(file_content)

    def _get_azure(self) -> BytesIO:
        """get azure bytes IO object"""
        az_connector = AzureConnector()
        if az_connector.is_active():
            az_connector.get_blob_service_client()

            return az_connector.get_backup_io(self.name)

        raise ValueError("azure connector not active")

    def _get_s3(self) -> BytesIO:
        """get s3 bytes IO object"""
        aws_connector = AmazonS3Connector()
        if aws_connector.is_active():
            aws_connector.get_s3_resource()

            return aws_connector.get_backup_io(self.name)

        raise ValueError("s3 connector not active")

    def restore(self, to_restore: BytesIO) -> None:
        """restore from io object"""
        connection_str = get_connection_str()
        command = ["psql", connection_str]
        print(f"run restore {command}")

        with gzip.open(to_restore, "rt") as f:
            decompressed_data: str = f.read()

        with subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ) as process:
            process.communicate(input=decompressed_data)

        print("restore process finished")
