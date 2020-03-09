# S3Resumable

This modules provides a helper class to download files from S3 using boto3.
To be able to recover incomplete downloads, it downloads files in parts of
the configured size.
