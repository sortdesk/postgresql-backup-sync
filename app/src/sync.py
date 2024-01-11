"""sync up to cloud storage"""

from pathlib import Path

from src.connector.amazon import AmazonS3Connector
from src.connector.azure import AzureConnector


def sync_to_cloud(backup_path: Path) -> None:
    """sync to cloud with connectors"""
    az_connector = AzureConnector()
    if az_connector.is_active():
        az_connector.get_blob_service_client()
        az_connector.save_backup(backup_path)
        az_connector.rotate_backups()

    aws_connector = AmazonS3Connector()
    if aws_connector.is_active():
        aws_connector.get_s3_resource()
        aws_connector.save_backup(backup_path)
        aws_connector.rotate_backups()
