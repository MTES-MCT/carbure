from django.db import connection


def truncate_tables():
    tables = ["carbure_notifications", "carbure_lots_events"]
    with connection.cursor() as cursor:
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
