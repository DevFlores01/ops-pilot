import os
from pathlib import Path

import pytest

from app.core.config import settings
from app.services.s3_service import S3Service

@pytest.mark.integration
def test_s3_upload_download(tmp_path: Path):
    if os.getenv("RUN_FLOCI_TESTS") != "1":
        pytest.skip("Enable with RUN_FLOCI_TESTS=1")
        
    if settings.aws_endpoint_url != "http://localhost:4566":
        pytest.skip("Only local Floci is permitted")
        
    s3 = S3Service()
    s3.ensure_bucket()
    
    source = tmp_path / "test-runbook.md"
    source.write_text(
        "# Test Runbook\nInvestigate API errors.",
        encoding="utf-8"
    )
    
    key = "tests/test-runbook.md"
    destination = tmp_path / "downloaded.md"
    
    s3.upload_file(source, key)
    assert key in s3.list_files()
    
    s3.download_file(key, destination)
    
    assert destination.read_bytes() == source.read_bytes()