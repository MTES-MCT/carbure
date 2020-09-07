import sys, os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CheckRule

filename = '%s/web/fixtures/csv/rules.csv' % (os.environ['CARBURE_HOME'])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=';', quotechar='"')
    for row in reader:
        if len(row) < 10:
            print('Incomplete row:')
            print(row)
            continue
        cond_col = row[0]
        cond = row[1]
        cond_value = row[2]
        check_col = row[3]
        check = row[4]
        check_value = row[5]
        warning_to_user = bool(row[6])
        warning_to_admin = bool(row[7])
        block_validation = bool(row[8])
        message = row[9]

        if cond_col == 'condition_col':
            # header
            continue


        obj, created = CheckRule.objects.update_or_create(condition_col=cond_col, condition=cond, condition_value=cond_value, check_col=check_col, check=check, check_value=check_value, defaults={'check_value': check_value, 'warning_to_user': warning_to_user, 'warning_to_admin': warning_to_admin, 'message': message})
