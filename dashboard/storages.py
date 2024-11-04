from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = "static"
    default_acl = None  # Ensure no ACL is set


class MediaStorage(S3Boto3Storage):
    location = "media"
    default_acl = None  # Ensure no ACL is set
