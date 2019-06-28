import os
import boto3







def main():

    # make sure path to bucket is available
    s3_connection = boto.connect_s3()
    bucket = s3_connection.get_bucket('your bucket name')
    key = boto.s3.key.Key(bucket, 'some_file.zip')

    annotation_files = [
        os.path.join(path, af)
        for af in os.listdir(path)
        if af.ends_with('yaml')
    ]

    for annotation_file in annotation_files:
        with open(annotation_file) as af:
            key.send_file(af)


if __name__ == "__main__":
    main()
