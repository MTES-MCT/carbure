import argparse
import datetime
import os
import sys

import boto3


def check_backup(args):
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_S3_REGION_NAME"],
        endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
        use_ssl=os.environ["AWS_S3_USE_SSL"],
    )
    bucket = s3.Bucket(args.bucket)

    if args.date:
        date = args.date
    else:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        date = yesterday.strftime("%Y/%m/%d")

    found = False
    for o in bucket.objects.filter(Prefix=date):
        found = True

    if not found:
        print("Database backup missing for date %s" % (date))
        return 1
    else:
        print("OK. Last backup: %s" % (date))
        return 0


def main():
    parser = argparse.ArgumentParser(description="Check the presence of database backup in s3 bucket")
    parser.add_argument("-b", dest="bucket", action="store", default="tradivari.database.backup", help="bucket name")
    parser.add_argument("date", action="store", default=None, help="Date YYYY/MM/DD", nargs="?")
    parser.add_argument(
        "--force", action="store_true", default=False, help="Force check even if not in production environment"
    )
    args = parser.parse_args()

    env = os.environ["IMAGE_TAG"]
    if env != "prod" and not args.force:
        print("Passed")
        return 0
    else:
        return check_backup(args)


if __name__ == "__main__":
    sys.exit(main())
