[![Build Status](https://travis-ci.org/immfly/s3resumable.svg?branch=master)](https://travis-ci.org/immfly/s3resumable)]

# S3Resumable

This modules provides a helper class to download files from S3 using boto3.
To be able to recover incomplete downloads, it downloads files in parts of
the configured size.

## Installation

Using `pip`:

```bash
pip install .
```

Using `docker-compose`:

```bash
docker-compose build
```

## Usage

The basic usage of s3resumable module can be summarized as declare a `boto3`
client and pass it on `S3Resumable` class:
 
```python
import boto3
from s3resumable import S3Resumable 

s3client = boto3.client('s3')
s3resumable = S3Resumable(s3client)
s3resumable.download_file('my_bucket', 'my_key', 'my_download_dir')
```

This will download the file in parts (15mb by default) and once downloaded
all the parts will join them in one file.

A CLI can also be used. Check the help:

```bash
s3resumable --help
```

## QA

In order to check QA, you can use docker-compose:

```bash
docker-compose build
docker-compose run py27 qa
docker-compose run py37 qa
```
