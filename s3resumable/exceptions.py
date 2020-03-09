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

This modules provides exceptions classes for S3Resumable.
"""

__all__ = ["S3ResumableError", "S3ResumableIncompatible", "S3ResumableDownloadError",
           "S3ResumableBloqued"]


class S3ResumableError(Exception):
    """Generic S3 Resumable exception."""


class S3ResumableIncompatible(S3ResumableError):
    """Can't download byte range of key."""


class S3ResumableDownloadError(S3ResumableError):
    """Error downloading a file part."""


class S3ResumableBloqued(S3ResumableError):
    """Another instance is downloading the same file."""
