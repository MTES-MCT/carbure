from huey import SqliteHuey, crontab

huey = SqliteHuey(filename="huey-cron.db")


@huey.periodic_task(crontab(minute="*/1"))
def try_something_out() -> None:
    print("Hello all.")
