import argparse
import datetime
import os
import sys

import boto3


def cleanup_s3db(args):
    s3 = boto3.resource('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'], region_name=os.environ['AWS_S3_REGION_NAME'], endpoint_url=os.environ['AWS_S3_ENDPOINT_URL'], use_ssl=os.environ['AWS_S3_USE_SSL'])
    bucket = s3.Bucket(args.bucket)

    today = datetime.date.today()
    last_month = today - datetime.timedelta(days=30)
    prefix = last_month.strftime('%Y/%m')
    backups = [o for o in bucket.objects.filter(Prefix=prefix)]

    to_delete = backups[0:-1]
    client = boto3.client('s3')
    deleted = 0
    for o in to_delete:
        print('Delete object %s' % o)
        deleted += 1
        o.delete()

    if deleted:
        print('%d backups deleted' % (deleted))
    return 0

def main():
    parser = argparse.ArgumentParser(description='Delete old database backups')
    parser.add_argument('-b', dest='bucket', action='store', help='bucket name')
    parser.add_argument('--force', action='store_true', default=False, help='Force check even if not in production environment')
    args = parser.parse_args()

    env = os.environ['IMAGE_TAG']
    if env != 'prod' and not args.force:
        return 0
    else:
        return cleanup_s3db(args)

if __name__ == '__main__':
    sys.exit(main())
