import boto3

s3 = boto3.client(
    "s3",
    endpoint_url="http://127.0.0.1:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

response = s3.list_buckets()

print(response["Buckets"])