import sys
import os
import boto3
import datetime
import argparse

def cleanup_s3db(args):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(args.bucket)

    today = datetime.date.today()
    last_month = today - datetime.timedelta(days=30)
    prefix = last_month.strftime('%Y/%m')
    backups = [o for o in bucket.objects.filter(Prefix=prefix)]

    to_delete = backups[0:-1]
    client = boto3.client('s3')
    deleted = 0
    for o in to_delete:
        logger.debug('Delete object %s' % o)
        deleted += 1
        o.delete()

    if deleted:
        print('%d backups deleted' % (deleted))
    return 0

def main():
    parser = argparse.ArgumentParser(description='Delete old database backups')
    parser.add_argument('-b', dest='bucket', action='store', help='bucket name')
    args = parser.parse_args()

    env = os.environ['IMAGE_TAG']
    if env != 'prod':
        return 0
    else:
        return cleanup_s3db(args)

if __name__ == '__main__':
    sys.exit(main())
