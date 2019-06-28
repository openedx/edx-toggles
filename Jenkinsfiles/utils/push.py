from __future__ import print_function

import os
import sys

import boto


def main():

    bucket_name = os.environ.get('BUCKET')
    if not bucket_name:
        print("Missing environment variable")
        sys.exit(1)

    try:
        conn = boto.connect_s3()
    except boto.exception.NoAuthHandlerFound:
        print("No AWS credentials found.")
        sys.exit(1)
    try:
        bucket = conn.get_bucket(bucket_name)
    except boto.exception.S3ResponseError:
        print("Unable to connect to cache bucket with these credentials.")
        sys.exit(1)

    annotation_files = [
        os.path.join(path, af), "annotation_reports/{}".format(af)
        for af in os.listdir(path)
        if af.ends_with('yaml') or af.ends_with('yml')
    ]

    for annotation_file_src, annotation_file_dest in annotation_files:
        key = boto.s3.key.Key(bucket=bucket, name=annotation_file, dest)
        bytes_written = key.set_contents_from_filename(
            annotation_file_dest, replace=True, policy='private'
        )
        if bytes_written:
            print(u"Wrote {} bytes to {}.".format(bytes_written, key.name))

if __name__ == "__main__":
    main()
