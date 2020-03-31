import os
import sys
import boto3
import datetime
import argparse

def upload_db_dump(bucket_name, filename):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    today = datetime.date.today().strftime('%Y/%m/%d')
    object = s3.Object(bucket.name, today)
    with open(filename, 'rb') as data:
        object.upload_fileobj(data)

def main():
    parser = argparse.ArgumentParser(description='Delete old database backups')
    parser.add_argument('-b', dest='bucket', action='store', help='bucket name')
    parser.add_argument('-f', dest='filename', action='store', help='dump filename')    
    args = parser.parse_args()

    env = os.environ['IMAGE_TAG']
    if env != 'prod':
        return 0
    else:
        upload_db_dump(args.bucket, args.filename)
    
if __name__ == '__main__':
    main()

