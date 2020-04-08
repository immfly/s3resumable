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
"""Cli for download S3 in parts.

Command line interface for S3resumable.
"""
from __future__ import absolute_import

import argparse
import logging
import os
import re

import boto3

from s3resumable import S3Resumable, S3ResumableObserver, S3ResumableError

S3_URL = r"^s3://([^/]+)/(.*?([^/]+)/?)$"


class Cli(S3ResumableObserver):
    """Command line interface for S3resumable."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--aws-access-key-id", dest="aws_access_key_id", type=str,
                                 help="AWS access key")
        self.parser.add_argument("--aws-secret-access-key", dest="aws_secret_access_key", type=str,
                                 help="AWS secret access key")
        self.parser.add_argument("--aws-session-token", dest="aws_session_token", type=str,
                                 help="AWS session token")
        self.parser.add_argument("--debug", action="store_true", help="increase output verbosity")
        self.parser.add_argument("--logfile", dest='logfile', help="set log file")
        self.parser.add_argument("--temp-dir", dest='temp_dir', help="temporal dir for parts")
        self.parser.add_argument("--part-size", dest='part_size', default=15, type=int,
                                 help="maximum size of temporary parts in MB")
        self.parser.add_argument("source", nargs=1, help="source object")
        self.parser.add_argument("target", nargs='?', default=os.getcwd(),
                                 help="target dir or file")

    def update(self, file_info):
        self.logger.debug("downloaded part %d of %d", file_info['part'], file_info['total_parts'])

    def start(self):
        """Starts here."""
        args = self.parser.parse_args()
        logging.basicConfig(filename=args.logfile,
                            format='%(asctime)-15s %(levelname)s: %(message)s')
        self.logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

        s3client = boto3.client('s3', aws_access_key_id=args.aws_access_key_id,
                                aws_secret_access_key=args.aws_secret_access_key,
                                aws_session_token=args.aws_session_token)
        s3resumable = S3Resumable(s3client, part_size_megabytes=args.part_size)
        s3resumable.attach(self)

        s3_url_re = re.match(S3_URL, args.source[0])
        if not s3_url_re:
            self.logger.error("invalid argument for s3 url")
            return -1

        bucket = s3_url_re.group(1)
        key = s3_url_re.group(2)

        if os.path.isdir(args.target) or args.target.endswith(os.sep):
            download_dir = args.target
            download_file = None
        else:
            download_dir = os.path.dirname(args.target[0])
            download_file = os.path.basename(args.target[0])

        self.logger.debug("bucket: %s", bucket)
        self.logger.debug("key: %s", key)
        self.logger.debug("download_dir: %s", download_dir)
        self.logger.debug("download_file: %s", download_file or os.path.basename(key))
        self.logger.debug("temp_dir: %s", args.temp_dir or download_dir)

        try:
            downloaded_file = s3resumable.download_file(bucket, key, download_dir,
                                                        download_file=download_file,
                                                        temp_dir=args.temp_dir)
            self.logger.info("%s downloaded", downloaded_file)
        except S3ResumableError as err:
            self.logger.error(str(err))
        return 0


def main():
    """Main function."""
    cli = Cli()
    cli.start()


if __name__ == "__main__":
    main()
