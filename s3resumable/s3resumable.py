# -*- coding: utf-8 -*-
# Copyright 2020 Immfly.com. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""Download S3 in parts.

This modules provides a helper class to download files from S3 using boto3.
To be able to recover incomplete downloads, it downloads files in parts of
the configured size.
"""
import math
import os

import filelock
from botocore.exceptions import ClientError
from botocore.compat import six

from s3resumable.utils import create_directory_tree
from s3resumable.utils import get_filelock_path
from s3resumable.exceptions import S3ResumableIncompatible
from s3resumable.observer import S3ResumableObserver
from s3resumable.exceptions import S3ResumableDownloadError
from s3resumable.exceptions import S3ResumableBloqued

__all__ = ["S3Resumable"]


class S3Resumable:
    """
    S3 resumable download class helper.
    """
    _observers = []

    def __init__(self, client, part_size_megabytes=15):
        """Class initializator.

        :param client: boto3 client, defaults to None
        :type client: boto3.Client
        :param part_size_bytes: size of parts in bytes, defaults to 15mb.
        :type part_size_bytes: int
        """
        if int(part_size_megabytes) < 1:
            raise ValueError('Invalid value for part_size_megabytes')

        self._client = client
        self._part_size_bytes = int(part_size_megabytes) * 1000000

    def attach(self, observer):
        """Attach observer to notifications."""
        if isinstance(observer, S3ResumableObserver):
            self._observers.append(observer)
        else:
            raise TypeError("Invalid type for observer")

    def detach(self, observer):
        """Detach observer from notifications."""
        self._observers.remove(observer)

    def notify(self, file_info):
        """Notify file info to observers."""
        for observer in self._observers:
            observer.update(file_info)

    def _check_part_size(self, file_part, part, file_info):
        total_parts = file_info["total_parts"]
        content_length = file_info["content_length"]
        if os.path.isfile(file_part):
            part_size = os.path.getsize(file_part)
            if part < (total_parts - 1):
                if part_size != self._part_size_bytes:
                    return False
            else:
                if part_size != content_length - (part * self._part_size_bytes):
                    return False
        else:
            return False
        return True

    def get_file_info(self, bucket, key):
        """Get file information from S3 in order to calculate the total number of parts to
        download.

        :param bucket: S3 Bucket.
        :param key: S3 Key.
        :raises S3ResumableIncompatible: Can't download byte range of key.
        :return: content length and total parts.
        :rtype: dict
        """
        accept_ranges = None
        content_length = 0
        total_parts = 0
        metadata = None
        http_headers = None

        head = self._client.head_object(Bucket=bucket, Key=key)

        if head is not None:
            metadata = head.get('ResponseMetadata')
        if metadata is not None:
            http_headers = metadata.get('HTTPHeaders')
        if http_headers is not None:
            content_length = int(http_headers.get('content-length', 0))
            accept_ranges = http_headers.get('accept-ranges')

        # Calculate total parts
        total_parts = 0
        if content_length != 0 and "bytes" in accept_ranges:
            total_parts = math.ceil(content_length / self._part_size_bytes)
        else:
            raise S3ResumableIncompatible()

        return {"key": key,
                "content_length": content_length,
                "total_parts": total_parts}

    def _download_part(self, bucket, key, part, file_info):
        file_part = file_info["part_path"].format(part=part)
        content_length = file_info["content_length"]

        if self._check_part_size(file_part, part, file_info):
            return
        start_range = part * self._part_size_bytes
        end_range = start_range + self._part_size_bytes - 1
        if end_range > content_length:
            end_range = content_length

        part_range = 'bytes={start}-{end}'.format(start=start_range, end=end_range)
        try:
            response = self._client.get_object(Bucket=bucket, Key=key, Range=part_range)
        except ClientError as client_error:
            if client_error.response['Error']['Code'] == '404':
                raise S3ResumableDownloadError("Key {} does not exist in s3".format(key))
        body = response.get('Body')
        if body is not None:
            with open(file_part, "wb") as part_buffer:
                part_buffer.write(body.read())

        if not self._check_part_size(file_part, part, file_info):
            raise S3ResumableDownloadError("Error with part...")

        file_info.update({"part": part + 1})
        self.notify(file_info)

    def _download_parts(self, bucket, key, download_file, temp_dir):
        local_file_path = os.path.join(temp_dir, download_file)

        # Resumable download
        part_path = "{path}.part{{part}}".format(path=local_file_path)

        file_info = self.get_file_info(bucket, key)
        file_info.update({"part_path": part_path})
        total_parts = file_info["total_parts"]
        content_length = file_info["content_length"]

        # Download parts
        for part in range(total_parts):
            self._download_part(bucket, key, part, file_info)

        # Concatenate parts
        with open(local_file_path, "wb") as result_file:
            for part in range(total_parts):
                file_part = part_path.format(part=part)
                try:
                    with open(file_part, "rb") as part_file:
                        result_file.write(part_file.read())
                finally:
                    if os.path.exists(file_part):
                        os.remove(file_part)

        # Check file size
        if os.path.getsize(local_file_path) != content_length:
            os.remove(local_file_path)
            raise S3ResumableDownloadError("key %s fail to download" % key)

        return local_file_path

    # pylint: disable=too-many-arguments
    def download_file(self, bucket, key, download_dir, download_file=None, temp_dir=None):
        """Download a file from s3 in parts in order to be able to resume incomplete downloads.

        :param bucket: s3 bucket.
        :param key: s3 key.
        :param download_dir: directory to download file.
        :param download_file: filename for downloaded file, defaults to None.
        :param temp_dir: directory to download file parts, defaults to None.
        :return: string with downloaded file path.
        """
        for argument in [("Bucket", bucket), ("Key", key)]:
            if not isinstance(argument[1], six.string_types):
                raise ValueError('{} must be a string'.format(argument[0]))

        if not temp_dir:
            temp_dir = download_dir

        if not download_file:
            download_file = os.path.basename(key)

        create_directory_tree(temp_dir)
        create_directory_tree(download_dir)

        local_file_path = os.path.join(download_dir, download_file)

        # The file was already downloaded
        if os.path.isfile(local_file_path):
            return local_file_path

        # Avoid other instances to download the same file
        filelock_filepath = get_filelock_path(download_file)
        lock = filelock.FileLock(filelock_filepath)
        try:
            with lock.acquire(timeout=10):
                downloaded_file = self._download_parts(bucket, key, download_file, temp_dir)
                if downloaded_file is not None and downloaded_file != local_file_path:
                    os.rename(downloaded_file, local_file_path)
        except filelock.Timeout:
            raise S3ResumableBloqued("Another instance is currently downloading {}.".format(
                local_file_path))

        return local_file_path
