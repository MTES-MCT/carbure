from huey.contrib.djhuey import db_task

from api.v4.sanity_checks import bulk_sanity_checks, bulk_scoring


@db_task()
def background_bulk_sanity_checks(lots, prefetched_data=None):
    bulk_sanity_checks(lots, prefetched_data)


@db_task()
def background_bulk_scoring(lots, prefetched_data=None):
    bulk_scoring(lots, prefetched_data)
