"""application entry point"""

import argparse
from os import environ
from time import sleep

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from src.backup import rotate_local_backup, run_local_backup
from src.restore import Restore
from src.sync import sync_to_cloud


def main():
    """run backup routine"""
    print("--- start backup task")
    backup_path = run_local_backup()
    sync_to_cloud(backup_path)
    rotate_local_backup()
    print("--- backup task completed")


def init_schedule():
    """create schedule for background task mode"""
    print("--- START PostgreSQL Backup Sync ---")
    cron_schedule = environ.get("SCHEDULE")
    if not cron_schedule:
        print("SCHEDULE env var is not set")
        while True:
            sleep(60)

        return

    print(f"set schedule to {cron_schedule}")
    trigger = CronTrigger.from_crontab(cron_schedule)
    scheduler = BlockingScheduler(timezone=environ.get("TZ", "UTC"))
    scheduler.add_job(main, trigger=trigger, name="pg_backup")
    scheduler.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="pg backup sync CLI interface")
    parser.add_argument("action", choices=["schedule", "backup", "restore"])
    parser.add_argument("-n", "--name")
    parser.add_argument("-s", "--source")
    args = parser.parse_args()

    if args.action == "schedule":
        init_schedule()
    elif args.action == "backup":
        main()
    elif args.action == "restore":
        handler = Restore(args.name, args.source)
        to_restore = handler.get_backup_io()
        handler.restore(to_restore)
