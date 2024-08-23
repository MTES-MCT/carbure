import argparse
import datetime
import os

import boto3


def upload_db_dump(filename):
    s3 = boto3.resource('s3', aws_access_key_id=os.environ['BACKBLAZE_KEY_ID'], aws_secret_access_key=os.environ['BACKBLAZE_APPLICATION_KEY'], endpoint_url=os.environ['BACKBLAZE_S3_ENDPOINT_URL'], use_ssl=True)
    bucket = s3.Bucket(os.environ['BACKBLAZE_BACKUP_BUCKET_NAME'])
    today = datetime.date.today().strftime('%Y/%m/%d')
    object = s3.Object(bucket.name, today)
    with open(filename, 'rb') as data:
        object.upload_fileobj(data)

def main():
    parser = argparse.ArgumentParser(description='Store backup to backblaze B2')
    parser.add_argument('-f', dest='filename', action='store', help='mysql dump filename')
    parser.add_argument('--force', dest='force', action='store_true', help='force upload even if not in prod')
    args = parser.parse_args()

    env = os.environ['IMAGE_TAG']
    if env == 'prod' or args.force:
        upload_db_dump(args.filename)
    else:
        print('not in prod and not --force, do nothing')
        return 0

if __name__ == '__main__':
    main()

