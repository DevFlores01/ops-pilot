from pathlib import Path

from app.services.s3_service import S3Service

def main():
    root = Path(__file__).resolve().parents[1]
    s3 = S3Service()
    
    s3.ensure_bucket()
    
    for name in [
        "redis-cache-runbook.md",
        "kubernetes-pod-runbook.md",
    ]:
        source = root / "data" / "documents" / name
        key = f"runbooks/{name}"
        
        s3.upload_file(source, key)
        print(f"Uploaded: {key}")
        
if __name__ == "__main__":
    main()