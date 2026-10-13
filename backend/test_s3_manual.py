from pathlib import Path

from app.core.config import settings
from app.services.s3_service import S3Service

def main():
    # Safe guard: Never run this on real AWS.
    if settings.aws_endpoint_url != "http://localhost:4566":
        raise RuntimeError("This lab requires local Floci")
    
    root = Path(__file__).resolve().parents[1]
    
    source = root / "data/documents/payment-api-runbook.md"
    destination = root / "data/downloads/payment-api-runbook.md"
    
    assert source.is_file(), f"Missing document: {source}"
    
    s3 = S3Service()
    s3.ensure_bucket()
    
    print("Bucket ready:", s3.bucket)
    
    key = "runbooks/payment-api-runbook.md"
    
    s3.upload_file(source, key)
    print("Upload successful")
    
    objects = s3.list_files()
    print("Stored objects", objects)
    
    assert key in objects
    
    s3.download_file(key, destination)
    print("Download successful")
    
    assert source.read_bytes() == destination.read_bytes()
    
    print("PASS: Downloaded file matches original")
    
if __name__ == "__main__":
    main()