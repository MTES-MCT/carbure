import argparse
import datetime
import os

import boto3


def upload_db_dump(bucket_name, filename):
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_S3_REGION_NAME"],
        endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
        use_ssl=os.environ["AWS_S3_USE_SSL"],
    )
    bucket = s3.Bucket(bucket_name)
    today = datetime.date.today().strftime("%Y/%m/%d")
    object = s3.Object(bucket.name, today)
    with open(filename, "rb") as data:
        object.upload_fileobj(data)


def main():
    parser = argparse.ArgumentParser(description="Delete old database backups")
    parser.add_argument("-b", dest="bucket", action="store", help="bucket name")
    parser.add_argument("-f", dest="filename", action="store", help="dump filename")
    args = parser.parse_args()

    env = os.environ["IMAGE_TAG"]
    if env != "prod":
        return 0
    else:
        upload_db_dump(args.bucket, args.filename)


if __name__ == "__main__":
    main()
