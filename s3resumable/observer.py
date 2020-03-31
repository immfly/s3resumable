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

This modules provides observer class for S3Resumable.
"""
import abc
import six

__all__ = ["S3ResumableObserver"]


@six.add_metaclass(abc.ABCMeta)
class S3ResumableObserver():  # pylint: disable=too-few-public-methods
    """Observer interface declares the update method, used by S3Resumable."""

    @abc.abstractmethod
    def update(self, file_info):
        """Receive update from S3Resumable."""
