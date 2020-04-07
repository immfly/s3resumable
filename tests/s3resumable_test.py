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
from __future__ import absolute_import

import sys

import unittest
from mock import patch
from mock import MagicMock
from mock import mock_open

from s3resumable import S3Resumable
from s3resumable import S3ResumableIncompatible
from s3resumable import S3ResumableObserver
from s3resumable import S3ResumableDownloadError
from s3resumable import S3ResumableBloqued

from botocore.exceptions import ClientError
from filelock import Timeout

BUILTIN_OPEN = '__builtin__.open' if sys.version_info.major < 3 else 'builtins.open'


class ObserverTest(S3ResumableObserver):
    def __init__(self):
        self.file_info = None

    def update(self, file_info):
        self.file_info = file_info


class S3ResumableTests(unittest.TestCase):
    def test_init_class(self):
        s3r = S3Resumable(None, part_size_megabytes=1)
        self.assertEqual(s3r._part_size_bytes, 1000000)
        s3r = S3Resumable(None)
        self.assertEqual(s3r._part_size_bytes, 15000000)
        with self.assertRaises(ValueError):
            S3Resumable(None, -1)
            S3Resumable(None, "fail")

    def test_attach_observer(self):
        s3r = S3Resumable(None)
        with self.assertRaises(TypeError):
            s3r.attach(object)
        self.assertEqual(0, len(s3r._observers))
        observer = ObserverTest()
        s3r.attach(observer)
        self.assertEqual(1, len(s3r._observers))
        s3r.detach(observer)
        self.assertEqual(0, len(s3r._observers))

    def test_notify_observer(self):
        s3r = S3Resumable(None)
        observer = ObserverTest()
        s3r.attach(observer)
        self.assertIsNone(observer.file_info)
        s3r.notify(True)
        self.assertTrue(observer.file_info)

    @patch('s3resumable.s3resumable.os')
    def test_check_part_size(self, mock_os):
        s3r = S3Resumable(None)
        file_info = {
            "total_parts": 4,
            "content_length": s3r._part_size_bytes * 3 + 1
        }
        mock_os.path.isfile.return_value = False
        self.assertFalse(s3r._check_part_size("test", 1, file_info))
        mock_os.path.isfile.return_value = True
        mock_os.path.getsize.return_value = 10
        self.assertFalse(s3r._check_part_size("test", 1, file_info))
        mock_os.path.getsize.return_value = s3r._part_size_bytes
        self.assertTrue(s3r._check_part_size("test", 1, file_info))
        self.assertFalse(s3r._check_part_size("test", 3, file_info))
        mock_os.path.getsize.return_value = 1
        self.assertTrue(s3r._check_part_size("test", 3, file_info))

    def test_get_file_info(self):
        boto3 = MagicMock()
        s3r = S3Resumable(boto3)
        boto3.head_object.return_value = {
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "124",
                    "accept-ranges": "bytes"
                }
            }
        }
        file_info = s3r.get_file_info("my_bucket", "my_key")
        self.assertEqual(file_info["key"], "my_key")
        self.assertEqual(file_info["content_length"], 124)
        self.assertEqual(file_info["total_parts"], 1)

        boto3.head_object.return_value = {
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": s3r._part_size_bytes + 1,
                    "accept-ranges": "bytes"
                }
            }
        }
        file_info = s3r.get_file_info("my_bucket", "my_key")
        self.assertEqual(file_info["content_length"], s3r._part_size_bytes + 1)
        self.assertEqual(file_info["total_parts"], 2)

        boto3.head_object.return_value = {
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": 1,
                    "accept-ranges": "other_value"
                }
            }
        }
        with self.assertRaises(S3ResumableIncompatible):
            s3r.get_file_info("my_bucket", "my_key")

    def test_download_part(self):
        boto3 = MagicMock()
        s3r = S3Resumable(boto3)
        s3r._check_part_size = MagicMock()
        s3r.notify = MagicMock()
        file_info = {
            'part_path': '/tmp/test.part{{part}}',
            'content_length': 100000
        }
        s3r._download_part("my_bucket", "my_key", 1, file_info)
        s3r._check_part_size.return_value = False
        boto3.get_object.side_effect = ClientError({'Error': {'Code': '404'}}, '')
        with self.assertRaises(S3ResumableDownloadError):
            s3r._download_part("my_bucket", "my_key", 1, file_info)
        boto3.get_object.side_effect = None
        body_mock = MagicMock()
        boto3.get_object.return_value = {'Body': body_mock}
        body_mock.read.return_value = b'1233455666'
        with self.assertRaises(S3ResumableDownloadError):
            s3r._download_part("my_bucket", "my_key", 1, file_info)
        s3r._check_part_size.side_effect = [False, True]
        s3r._download_part("my_bucket", "my_key", 1, file_info)
        self.assertEqual(file_info['part'], 2)

    @patch(BUILTIN_OPEN, new_callable=mock_open, read_data="se")
    @patch('s3resumable.s3resumable.os')
    def test_download_parts(self, mock_os, m_open):
        s3r = S3Resumable(None)
        s3r.get_file_info = MagicMock()
        s3r._download_part = MagicMock()
        s3r.get_file_info.return_value = {
            "total_parts": 2,
            "content_length": 10
        }
        mock_os.path.getsize.return_value = 9
        with self.assertRaises(S3ResumableDownloadError):
            s3r._download_parts("my_bucket", "my_key", "/tmp/download_file", "/tmp")
        mock_os.path.getsize.return_value = 10
        s3r._download_parts("my_bucket", "my_key", "/tmp/download_file", "/tmp")

    @patch('s3resumable.s3resumable.filelock')
    @patch('s3resumable.s3resumable.get_filelock_path')
    @patch('s3resumable.s3resumable.create_directory_tree')
    @patch('s3resumable.s3resumable.os')
    def test_download_file(self, mock_os, mock_dt, mock_fp, mock_filelock):
        s3r = S3Resumable(None)
        with self.assertRaises(ValueError):
            s3r.download_file(9, 1, 2)
            s3r.download_file("my_bucket", 1, 2)
            s3r.download_file("my_bucket", "my_key", 2)
        s3r._download_parts = MagicMock()
        s3r.download_file("my_bucket", "my_key", "/tmp")
        mock_os.path.isfile.return_value = False
        s3r.download_file("my_bucket", "my_key", "/tmp")


if __name__ == '__main__':
    unittest.main()
