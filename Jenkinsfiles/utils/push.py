from __future__ import print_function

import os
import sys

import boto


def main():

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
        os.path.join(path, af)
        for af in os.listdir(path)
        if af.ends_with('yaml')
    ]

    for annotation_file in annotation_files:
        with open(annotation_file) as af:
            key = boto.s3.key.Key(bucket=bucket, name=file_name)
            bytes_written = key.set_contents_from_filename(
                af, replace=True, policy='private'
            )
            if bytes_written:
                print(u"Wrote {} bytes to {}.".format(bytes_written, key.name))

if __name__ == "__main__":
    main()
