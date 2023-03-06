import os

import boto3

bucketName = os.getenv("KLOTHO_PROXY_RESOURCE_NAME")


def open(url: str, **kwargs):
    return s3ContextManager(str(url), **kwargs)


class s3ContextManager(object):
    def __init__(self, file_name: str, **kwargs):
        self.client = boto3.client('s3')
        self.bucket_name = bucketName
        self.file_name = file_name
        self.kwargs = kwargs

    async def __aenter__(self):
        return FsItem(bucket_name=self.bucket_name, file_name=self.file_name, client=self.client, **self.kwargs)

    async def __aexit__(self, exc_type, exc_val, traceback):
        pass


class FsItem(object):
    def __init__(self, file_name: str, bucket_name: str, client: boto3.client, **kwargs):
        self.client = client
        self.bucket_name = bucket_name
        self.file_name = file_name
        mode = kwargs.get("mode", "r")
        self.is_readable = "r" in mode
        self.is_writeable = "w" in mode or "+" in mode or "x" in mode
        self.is_binary = "b" in mode

        if "a" in mode:
            raise IOError('@klotho::persist does not support append mode')

        self.encoding = kwargs.get("encoding", "utf-8")

    async def write(self, content: str):
        if not self.is_writeable:
            raise IOError(f"{self.file_name} is not writeable")
        self.client.put_object(Key=self.file_name, Bucket=self.bucket_name, Body=content)

    async def read(self):
        if not self.is_readable:
            raise IOError(f"{self.file_name} is not readable")
        response = self.client.get_object(Key=self.file_name, Bucket=self.bucket_name)
        body = response["Body"].read()
        if not self.is_binary:
            body = body.decode(self.encoding)
        return body
