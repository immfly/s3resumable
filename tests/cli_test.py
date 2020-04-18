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

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from mock import patch
from mock import MagicMock
from mock import mock_open

from s3resumable.cli import Cli
from s3resumable.cli import main

from botocore.exceptions import ClientError
from filelock import Timeout

BUILTIN_OPEN = '__builtin__.open' if sys.version_info.major < 3 else 'builtins.open'


class CliTests(unittest.TestCase):
    def test_updates(self):
        cli = Cli()
        cli.logger.setLevel('DEBUG')
        file_info = {
            'part': 1,
            'total_parts': 10
        }
        with self.assertLogs(level='DEBUG') as cm:
            cli.update(file_info)
        self.assertEqual(cm.output, ['DEBUG:s3resumable.cli:downloaded part 1 of 10'])
        file_info = {
            'part': 2,
            'total_parts': 10
        }
        with self.assertLogs(level='DEBUG') as cm:
            cli.update(file_info)
        self.assertEqual(cm.output, ['DEBUG:s3resumable.cli:downloaded part 2 of 10'])

    @patch('s3resumable.cli.S3Resumable')
    def test_start(self, mock_s3r):
        cli = Cli()
        with patch('argparse._sys.argv', ['s3resumable', 's://my_bucket/test']),\
                self.assertLogs() as cm:
            cli.start()
        self.assertEqual(cm.output, ['ERROR:s3resumable.cli:invalid argument for s3 url'])
        with patch('argparse._sys.argv', ['s3resumable', 's3://my_bucket/test']),\
                self.assertLogs() as cm:
            cli.start()
        self.assertIn('downloaded', cm.output[0])


if __name__ == '__main__':
    unittest.main()
