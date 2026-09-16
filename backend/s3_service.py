import os
import boto3
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)


def download_file(s3_key, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    s3.download_file(
        BUCKET_NAME,
        s3_key,
        local_path
    )

    return local_path