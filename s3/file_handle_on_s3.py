import os
import io
import re
import csv

import pandas as pd
import s3fs
import botocore
import boto3
from boto3.session import Session


# S3へのアクセス
def get_aws_cred(word_in_file=None):
    # 対象ファイルは credentials_ から始まる csv となっていることを前提とする
    # cred ファイルが存在しなければ Key, Secret ともに None である cred を返す
    # 複数ファイルがあった場合、 word_in_file がファイル名にあるものを優先する
    # それも複数あった場合、任意の1つを選ぶ

    cred_files = [f for f in os.listdir(os.curdir) if f.startswith('credentials_') and f.endswith('.csv')]

    if not cred_files:
        return {
            'Access key ID': None, 'Secret access key': None
        }

    cred_file = cred_files[0]
    if word_in_file is not None:
        cred_files_with_word = [f for f in cred_files if word_in_file in f]
        if cred_files_with_word:
            cred_file = cred_files_with_word[0]

    contents = open(cred_file, 'r').readlines()
    contents = [c.strip() for c in contents]
    """
    Need credential with the following permissions
    - AmazonAthenaFullAccess
    - AmazonS3FullAccess

    """
    content = dict(zip(re.split(',', contents[0]), re.split(',', contents[1])))

    if 'Access key ID' in content and 'Secret access key' in content:
        return {
            'Access key ID': content['Access key ID'],
            'Secret access key': content['Secret access key']
        }

    return {
        'Access key ID': None, 'Secret access key': None
    }


CRED = get_aws_cred()
S3_KEY = CRED['Access key ID']
S3_SECRET = CRED['Secret access key']

BUCKET = '<bucket name>'
BUCKET_KEY = '<path to file in a bucket>'
FILE_NAME = '<file name>'


def upload_file(source_file, destination_file, bucket_name):
    session = Session(aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)

    s3 = session.resource('s3')

    bucket = s3.Bucket(bucket_name)
    bucket.upload_file(source_file, destination_file)


def write_df_to_s3_with_cred(df, bucket, key, sep=',', cred=None):
    if cred is None:
        s3_key = S3_KEY
        s3_secret = S3_SECRET
    else:
        if 'Access key ID' in cred:
            s3_key = cred['Access key ID']
        elif 'access_key' in cred:
            s3_key = cred['access_key']
        else:
            s3_key = S3_KEY
        if 'Secret access key' in cred:
            s3_secret = cred['Secret access key']
        elif 'access_secret' in cred:
            s3_secret = cred['access_secret']
        else:
            s3_secret = S3_SECRET

    s3_path = '/'.join([bucket, key])
    bytes_to_write = df.to_csv(None, sep=sep, index=False).encode()
    fs = s3fs.S3FileSystem(key=s3_key, secret=s3_secret)

    with fs.open(s3_path, 'wb') as f:
        f.write(bytes_to_write)


def write_df_to_s3_with_boto3(df, bucket, key, sep=','):
    client = boto3.client('s3')
    bytes_to_write = df.to_csv(None, sep=sep, index=False).encode()
    response = client.put_object(Bucket=bucket, Key=key, Body=bytes_to_write)

    return response


def write_matrix_to_s3(matrix, bucket, key, delimiter=','):
    """
    matrix = [[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]]
    """
    matrix = [delimiter.join([str(i) for i in line]) for line in matrix]

    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, key)
    response = obj.put(Body='\n'.join(matrix))

    return response


def s3_key_exists(s3_path):
    fs = s3fs.S3FileSystem(key=S3_KEY, secret=S3_SECRET)

    try:
        fs.ls(s3_path, refresh=True)
        return fs.exists(s3_path)
    except FileNotFoundError:
        return False


def rm_s3_key(s3_path):
    fs = s3fs.S3FileSystem(key=S3_KEY, secret=S3_SECRET)

    if s3_key_exists(s3_path):
        fs.rm(s3_path)
        return True
    else:
        return False


def find_files_in_s3(s3_path, full_path=False):
    """
        no need 's3://' for s3_path
    """
    fs = s3fs.S3FileSystem(key=S3_KEY, secret=S3_SECRET)

    files = [f for f in fs.ls(s3_path, refresh=True)]

    if not full_path:
        files = [re.split('/', f)[-1] for f in files]

    return files


def read_df_from_s3_with_s3fs(s3_path, encoding='utf8', dtype=object, quoting=csv.QUOTE_MINIMAL, delimiter=','):
    fs = s3fs.S3FileSystem(key=S3_KEY, secret=S3_SECRET)

    with fs.open(s3_path) as f:
        df = pd.read_csv(f, encoding=encoding, dtype=dtype, quoting=quoting, delimiter=delimiter)
        return df


def read_df_from_s3_with_cred(bucket, key, s3_access_key=None, s3_access_secret=None,
                              encoding='utf8', dtype=object, delimiter=','):

    if s3_access_key is None or s3_access_secret is None:
        client = boto3.client('s3')
    else:
        client = boto3.client('s3', aws_access_key_id=s3_access_key, aws_secret_access_key=s3_access_secret)

    try:
        obj = client.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding=encoding, dtype=dtype, delimiter=delimiter)
    except botocore.exceptions.ClientError as e:
        print(e)
        df = pd.DataFrame()

    return df


def read_df_from_s3_with_boto3(bucket, key, event=None, encoding='utf8', dtype=object, delimiter=','):
    client = boto3.client('s3')
    if event is not None:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

    try:
        obj = client.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding=encoding, dtype=dtype, delimiter=delimiter)
    except botocore.exceptions.ClientError as e:
        print(e)
        df = pd.DataFrame()

    return df


def test():
    data = pd.DataFrame()
    s3_key = '/'.join(['s3:/', BUCKET_KEY, FILE_NAME])
    write_df_to_s3_with_boto3(data, BUCKET, s3_key)


if __name__ == '__main__':
    test()
