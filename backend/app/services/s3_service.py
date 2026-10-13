from pathlib import Path

import boto3
from botocore.config import Config 
from botocore.exceptions import ClientError

from app.core.config import settings

class S3Service:   
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.aws_endpoint_url,
            region_name=settings.aws_default_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            config=Config(
                s3={"addressing_style": "path"},
                connect_timeout=5,
                read_timeout=15,
                retries={"max_attempts": 2},
            ),
        )
        self.bucket = settings.s3_bucket
        
    def ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            
            if code not in ("404", "NoSuchBucket", "NotFound"):
                raise
            
            self.client.create_bucket(Bucket=self.bucket)
            
    def upload_file(self, file_path: Path, key: str) -> None:
        self.client.upload_file(
            str(file_path),
            self.bucket,
            key,
        )
        
    def list_files(self) -> list[str]:
        paginator = self.client.get_paginator("list_objects_v2")
        keys = []
        
        for page in paginator.paginate(Bucket=self.bucket):
            keys.extend(
                obj["Key"]
                for obj in page.get("Contents", [])
            )
            
        return keys
    
    def download_file(self, key: str, destination: Path) -> None:
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        
        self.client.download_file(
            self.bucket,
            key,
            str(destination),
        )