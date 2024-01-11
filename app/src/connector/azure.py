"""backup storage on azure blob"""

from io import BytesIO
from os import environ
from pathlib import Path

from azure.storage.blob import BlobServiceClient
from src.connector.base import BaseConnector


class AzureConnector(BaseConnector):
    """azure blob storage connector"""

    CONNECTION_STR = environ.get("AZ_CONNECTION_STR")
    CONTAINER_NAME = environ.get("AZ_CONTAINER_NAME")

    def __init__(self):
        self.blob_service_client = None

    def is_active(self):
        """check if azure connector is active"""
        return all((self.CONNECTION_STR, self.CONTAINER_NAME))

    def get_blob_service_client(self):
        """get client"""
        self.blob_service_client = BlobServiceClient.from_connection_string(self.CONNECTION_STR)

    def save_backup(self, path: Path) -> None:
        """upload blob to AZ container"""
        print("upload backup to Azure Blob Storage")
        blob_client = self.blob_service_client.get_blob_client(container=self.CONTAINER_NAME, blob=path)

        with open(file=path, mode="rb") as data:
            blob_client.upload_blob(data)

        print(f"uploaded {path} to {self.CONTAINER_NAME}")

    def get_backups(self) -> list[str]:
        """get available backups"""
        container_client = self.blob_service_client.get_container_client(self.CONTAINER_NAME)
        backups = [i.name for i in container_client.list_blobs()]

        return backups

    def rotate_backups(self):
        """rotate"""
        if not self.FILES_TO_KEEP:
            return

        print("rotating Azure Blob backups")

        backups = self.get_backups()
        if len(backups) < self.FILES_TO_KEEP:
            return

        backups.sort()
        to_delete = backups[: -self.FILES_TO_KEEP]
        if not to_delete:
            return

        print(f"deleting {len(to_delete)} Azure Blob files")
        for file_name in to_delete:
            blob_client = self.blob_service_client.get_blob_client(container=self.CONTAINER_NAME, blob=file_name)
            blob_client.delete_blob()

    def get_backup_io(self, name: str | None) -> BytesIO:
        """get IO object of item by name"""
        if not name:
            name = self.get_backups()[-1]

        print(f"download {name} from azure container {self.CONTAINER_NAME}")
        container_client = self.blob_service_client.get_container_client(self.CONTAINER_NAME)
        blob_client = container_client.get_blob_client(name)
        blob_content = blob_client.download_blob().readall()

        return BytesIO(blob_content)
