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
"""Setup file for S3Resumable."""
import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="s3resumable",
    version="0.0.1",
    author="Immfly",
    author_email="francesc.gordillo@immfly.com",
    description="Resumable S3 download",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://git.immfly.com/immfly/s3resumable",
    packages=['s3resumable'],
    entry_points={
        'console_scripts': ['s3resumable=s3resumable.cli:main'],
    },
    install_requires=[
        'six',
        'boto3',
        'filelock==3.0.12'],
    extras_require={
        'dev': [
            'pylint',
            'flake8',
            'pytest',
            'mock',
            'coverage'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License"
    ],
    python_requires='>=2.6',
)
