from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class AWSStorage(S3Boto3Storage):
    bucket_name = settings.AWS_DCDOCS_STORAGE_BUCKET_NAME