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

This modules provides functions utils for S3Resumable.
"""
import errno
import hashlib
import os
import tempfile


def create_directory_tree(path):
    """Create directory tree."""
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


def get_filelock_path(filename):
    """Calculate filelock path from filename."""
    basename = "s3resumable_{}".format(hashlib.md5(filename.encode('utf-8')).hexdigest())
    basedir = tempfile.gettempdir()
    return os.path.join(basedir, basename)
