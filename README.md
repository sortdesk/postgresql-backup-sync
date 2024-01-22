# PostgreSQL Backup Sync

Companion container to your Postgres database.

## Core Functionality
- Create local backup of your Postgres database
- Sync backup file to various external storage platforms
- Rotate old backups

## Installation
This is a docker container. Example installation with docker compose:

```yml
version: '3.5'

services:
  pg-backup-sync:
    container_name: "pg-backup-sync"
    restart: unless-stopped
    image: ghcr.io/sortdesk/postgresql-backup-sync
    volumes:
    - pgbackup:/backup
    environment:
    - POSTGRES_USER=postgres_user
    - POSTGRES_PASSWORD=xxxxxxxxxxxxxxxxxxxxx
    - POSTGRES_DB=postgres_db
    - POSTGRES_HOST=postgres
    - SCHEDULE="0 0 * * *"

    # optionally configure backup retention
    # - FILES_TO_KEEP=5

    # optionally configure Azure Blob Storage cloud connector
    # - AZ_CONNECTION_STR=
    # - AZ_CONTAINER_NAME=pg-backup-sync

    # optionally configure AWS S3 bucket cloud connector
    # - AWS_BUCKET_NAME=pg-backup-sync
    # - AWS_ACCESS_KEY_ID=XXXXXXX
    # - AWS_SECRET_ACCESS_KEY=yyyyyyy

volumes:
  pgbackup:
```

This expects a volume at `/backup` to store the backup files.

## Usage
By default this runs in the `schedule` mode, meaning the container is idle until woken up by the cron schedule configured.

Additionally the container has a minimal CLI for additional interactions:

- `python main.py backup`: Create an ad-hoc backup now, use this to test that everything is working as expected.
- `python main.py restore`: Restore Postgres from backup. This takes two optional additional arguments:
	- `-n --name`: Define the file name of the backup to restore, defaults to the latest available
	- `-s --source`: Define the source from where to restore from, defaults to `local` as in local backups stored in `/backup` of the container, can also be `azure` for Azure Blob Storage or `s3` for AWS S3 bucket.

## Postgres Connection
Configure your postgres connection with these environment variables:

- `POSTGRES_USER`: User Name
- `POSTGRES_PASSWORD`: Password
- `POSTGRES_DB`: Database
- `POSTGRES_HOST`: Server Host
- `POSTGRES_PORT`: Server Port, optional, defaults to 5432

## Scheduler
Define a crontab schedule when the backup task should get triggered with the `SCHEDULE` environment variable.

## Backup Retention
Optionally specify how many backups you want to keep by setting the `FILES_TO_KEEP` environment variable. This will both rotate local backup files and configured cloud connectors.

## Cloud Connectors
Add one or more cloud connectors to sync your backups to external storage providers. Define separate buckets/containers for different deployments to avoid conflicting behavior.

### Azure Blob Storage
Configure your connector details by setting the following environment variables:

- `AZ_CONNECTION_STR`: Get your connection string from your storage account Access Keys
- `AZ_CONTAINER_NAME`: Container Name from your data storage account

### Amazon S3 Storage
Set your credentials to use an Amazon S3 bucket for external storage.

- `AWS_BUCKET_NAME`: Name of the bucket
- `AWS_ACCESS_KEY_ID`: Your access key ID
- `AWS_SECRET_ACCESS_KEY`: Your secret access key
