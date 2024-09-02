import argparse
import os
import sys

import boto3


def cleanup_s3db(args):
    print("> Setup S3 connection to bucket")

    s3 = boto3.resource(
        "s3",
        aws_access_key_id=os.environ["BACKBLAZE_KEY_ID"],
        aws_secret_access_key=os.environ["BACKBLAZE_APPLICATION_KEY"],
        endpoint_url=os.environ["BACKBLAZE_S3_ENDPOINT_URL"],
        use_ssl=True,
    )

    bucket = s3.Bucket(args.bucket)

    backups = [o.key for o in bucket.objects.filter(Prefix=args.year)]

    backups_by_month = {}
    for key in backups:
        month = key[5:7]
        if month not in backups_by_month:
            backups_by_month[month] = []
        backups_by_month[month].append(key)

    print(f"> {len(backups)} backups found over {len(backups_by_month)} months")

    to_delete = []
    for month in backups_by_month:
        sorted(backups_by_month[month])
        all_but_last = backups_by_month[month][0:-1]
        to_delete += [{"Key": key} for key in all_but_last]

    if len(to_delete) > 0:
        bucket.delete_objects(Delete={"Objects": to_delete})
        print(f"> Deleted {len(to_delete)} backups from the bucket")
    else:
        print("> Backups are already cleaned")


def main():
    parser = argparse.ArgumentParser(description="Delete old database backups")
    parser.add_argument("-b", dest="bucket", action="store", help="bucket name")
    parser.add_argument(
        "--force", action="store_true", default=False, help="Force check even if not in production environment"
    )
    parser.add_argument("--year", action="store", help="Pick the year to be cleaned")
    args = parser.parse_args()

    env = os.environ["IMAGE_TAG"]
    if env == "prod" or args.force:
        cleanup_s3db(args)


if __name__ == "__main__":
    sys.exit(main())
