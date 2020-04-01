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

import unittest
import errno
from mock import patch
from mock import MagicMock

from s3resumable.utils import create_directory_tree
from s3resumable.utils import get_filelock_path


class UtilsTests(unittest.TestCase):
    @patch('s3resumable.utils.os')
    def test_create_directory_tree(self, mock_os):
        mock_os.path.exists.return_value = True
        mock_os.path.isdir.return_value = True
        create_directory_tree("/tmp/test")
        mock_os.path.exists.return_value = False
        mock_os.path.isdir.return_value = True
        create_directory_tree("/tmp/test")
        mock_os.makedirs.side_effect = Exception('test')
        mock_os.path.isdir.return_value = True
        with self.assertRaises(Exception):
            create_directory_tree("/tmp/test")
        mock_os.path.isdir.return_value = True
        mock_os.makedirs.side_effect = OSError(errno.EEXIST, "test")
        create_directory_tree("/tmp/test")
        mock_os.path.isdir.return_value = True
        mock_os.makedirs.side_effect = OSError(errno.EIO, "test")
        with self.assertRaises(OSError):
            create_directory_tree("/tmp/test")

    def test_get_filelock_path(self):
        filelock1 = get_filelock_path("test")
        filelock2 = get_filelock_path("test")
        filelock3 = get_filelock_path("other_test")
        self.assertEqual(filelock1, filelock2)
        self.assertNotEqual(filelock1, filelock3)
        self.assertNotEqual(filelock2, filelock3)


if __name__ == '__main__':
    unittest.main()
