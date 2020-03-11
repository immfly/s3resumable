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
import unittest
import mock

from s3resumable import S3Resumable


class S3ResumableTests(unittest.TestCase):
    def test_init_class(self):
        s3r = S3Resumable(None, part_size_megabytes=1)
        self.assertEqual(s3r._part_size_bytes, 1000000)
        s3r = S3Resumable(None)
        self.assertEqual(s3r._part_size_bytes, 15000000)

    def test_attach_observer(self):
        s3r = S3Resumable(None)
        self.assertRaises(TypeError, s3r.attach(object))

    def

if __name__ == '__main__':
    unittest.main()
