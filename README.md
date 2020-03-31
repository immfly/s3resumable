# S3Resumable

This modules provides a helper class to download files from S3 using boto3.
To be able to recover incomplete downloads, it downloads files in parts of
the configured size.

# Installation

Using `pip`:

```bash
pip install .
```

Using `docker-compose`:

```bash
docker-compose build
```

# QA

In order to check QA, you can use docker-compose:

```bash
docker-compose build
docker-compose run py27 qa
docker-compose run py37 qa
```
