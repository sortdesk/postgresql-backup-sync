"""backup sync to amazon s3"""

from io import BytesIO
from os import environ
from pathlib import Path

import boto3
from src.connector.base import BaseConnector


class AmazonS3Connector(BaseConnector):
    """amazon s3 connector"""

    AWS_BUCKET_NAME = environ.get("AWS_BUCKET_NAME")
    AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY")

    def __init__(self):
        self.s3 = None

    def is_active(self):
        """check if s3 connector is active"""
        return all((self.AWS_BUCKET_NAME, self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY))

    def get_s3_resource(self) -> None:
        """get boto session s3 resource"""
        session = boto3.Session(
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
        )
        self.s3 = session.resource("s3")

    def save_backup(self, path: Path) -> None:
        """upload file to s3 bucket"""
        print("upload backup to AWS S3 bucket")
        self.s3.Bucket(self.AWS_BUCKET_NAME).upload_file(path, path.name)
        print(f"uploaded {path} to {self.AWS_BUCKET_NAME}")

    def get_backups(self) -> list[str]:
        """get available backups"""
        bucket = self.s3.Bucket(self.AWS_BUCKET_NAME)
        backups = [i.key for i in bucket.objects.all()]

        return backups

    def rotate_backups(self):
        """rotate"""
        if not self.FILES_TO_KEEP:
            return

        print("rotating AWS S3 backups")
        backups = self.get_backups()
        if len(backups) < self.FILES_TO_KEEP:
            return

        backups.sort()
        to_delete = backups[: -self.FILES_TO_KEEP]
        if not to_delete:
            return

        print(f"deleting {len(to_delete)} S3 objects")
        bucket = self.s3.Bucket(self.AWS_BUCKET_NAME)
        for file_name in to_delete:
            bucket.Object(key=file_name).delete()

    def get_backup_io(self, name: str | None) -> BytesIO:
        """get IO object of s3 bucket item by name"""
        if not name:
            name = self.get_backups()[-1]

        print(f"download {name} from s3 bucket {self.AWS_BUCKET_NAME}")
        bucket = self.s3.Bucket(self.AWS_BUCKET_NAME)
        obj = bucket.Object(name)
        file_content = obj.get()["Body"].read()

        return BytesIO(file_content)
