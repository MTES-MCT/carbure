import argparse
import datetime
import os
import sys

import boto3


def dl_backup(bucket, date):
    if not date:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        date = yesterday.strftime("%Y/%m/%d")
    print(date)
    filename = "/tmp/backup.tgz"
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_S3_REGION_NAME"],
        endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
        use_ssl=os.environ["AWS_S3_USE_SSL"],
    )
    print("will download %s from %s" % (date, bucket))
    with open(filename, "wb") as f:
        s3.download_fileobj(bucket, date, f)


def main():
    parser = argparse.ArgumentParser(description="Download a previous database backup from an s3 bucket")
    parser.add_argument("-b", dest="bucket", action="store", default="tradivari.database.backup", help="bucket name")
    parser.add_argument("-d", dest="date", action="store", default=None, help="Date YYYY/MM/DD", nargs="?")
    args = parser.parse_args()
    return dl_backup(args.bucket, args.date)


if __name__ == "__main__":
    sys.exit(main())
