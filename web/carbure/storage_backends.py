from django.conf import settings
import django
from django.utils.encoding import force_str, smart_str
django.utils.encoding.force_text = force_str
django.utils.encoding.smart_text = smart_str

from storages.backends.s3boto3 import S3Boto3Storage

class AWSStorage(S3Boto3Storage):
    bucket_name = settings.AWS_DCDOCS_STORAGE_BUCKET_NAME
