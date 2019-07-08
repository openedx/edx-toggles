#!/usr/bin/env

# publish-to-s3.py
#
# push all of the files in 'annotation_reports' to an S3 bucket
# specified with the environment variable 'ANNOTATION_REPORT_BUCKET'

from __future__ import absolute_import
from __future__ import print_function
import os
import sys

import boto


def main():

    bucket_name = os.environ.get('ANNOTATION_REPORT_BUCKET')
    if not bucket_name:
        print("Missing environment variable 'ANNOTATION_REPORT_BUCKET'")
        sys.exit(1)

    try:
        conn = boto.connect_s3()
    except boto.exception.NoAuthHandlerFound:
        print("No AWS credentials/roles found on this server")
        sys.exit(1)
    try:
        bucket = conn.get_bucket(bucket_name)
    except boto.exception.S3ResponseError:
        print("Unable to connect to bucket with these credentials.")
        sys.exit(1)

    path = 'annotation_reports'
    annotation_files = [
        (os.path.join(path, af), "{}/{}".format(path, af))
        for af in os.listdir(path)
        if af.endswith('yaml') or af.endswith('yml')
    ]

    print("Writing data from {} to s3 bucket".format(path))
    for annotation_file_src, annotation_file_dest in annotation_files:
        key = boto.s3.key.Key(bucket=bucket, name=annotation_file_dest)
        bytes_written = key.set_contents_from_filename(
            annotation_file_dest, replace=True, policy='private'
        )
        if bytes_written:
            print(u"Wrote {} bytes to {}.".format(bytes_written, key.name))


if __name__ == "__main__":
    main()
