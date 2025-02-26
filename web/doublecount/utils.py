import os
from urllib.parse import urlparse

import boto3


def generate_presigned_url(file_url, expiration=60):
    parsed_url = urlparse(file_url)
    if not parsed_url.path:
        return None
    bucket_name = parsed_url.netloc.split(".")[0]  # Bucket name
    object_key = parsed_url.path.lstrip("/")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_S3_REGION_NAME"],
    )
    try:
        url = s3.generate_presigned_url(
            "get_object", Params={"Bucket": bucket_name, "Key": object_key}, ExpiresIn=expiration
        )
        return url
    except Exception as e:
        print("Error generating presigned URL:", e)
        return None
