import sys
import os
import boto3
import datetime
import argparse

from common import logger
logger.setupLogger('s3dbcheck')
import logging
logger = logging.getLogger('s3dbcheck')

def check_backup(args):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(args.bucket)

    if args.date:
        date = args.date
    else:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        date = yesterday.strftime('%Y/%m/%d')

    found = False
    for o in bucket.objects.filter(Prefix=date):
        found = True

    if not found:
        logger.info('Database backup missing for date %s' % (date))
        return 1
    else:
        logger.info('OK. Last backup: %s' % (date))
        return 0

def main():
    parser = argparse.ArgumentParser(description='Check the presence of database backup in s3 bucket')
    parser.add_argument('-b', dest='bucket', action='store', default='tradivari.database.backup', help='bucket name')
    parser.add_argument('date', action='store', default=None, help='Date YYYY/MM/DD', nargs='?')
    parser.add_argument('--force', action='store_true', default=False, help='Force check even if not in production environment')    
    args = parser.parse_args()
    
    env = os.environ['TRADIVARI_ENV']
    if env != 'prod' and not args.force:
        logger.info('Passed')
        return 0
    else:
        return check_backup(args)

if __name__ == '__main__':
    sys.exit(main())
