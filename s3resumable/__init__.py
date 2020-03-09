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
from .s3resumable import S3Resumable
from .exceptions import S3ResumableError
from .exceptions import S3ResumableIncompatible
from .exceptions import S3ResumableDownloadError
from .exceptions import S3ResumableBloqued
from .observer import S3ResumableObserver


__all__ = ["S3Resumable", "S3ResumableObserver", "S3ResumableError",
           "S3ResumableIncompatible", "S3ResumableBloqued",
           "S3ResumableDownloadError"]
