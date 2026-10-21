import logging

from botocore.exceptions import ClientError
from mcp.server.fastmcp import FastMCP

from app.core.config import settings
from app.services.retrieval_service import RetrievalService
from app.services.s3_service import S3Service

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

mcp = FastMCP("OpsPilot Operation Tools")


@mcp.tool()
async def search_runbooks(
    query: str,
    top_k: int = 3,
) -> list[dict]:
    """
    Search operational runbooks using semantic similarity.

    Read-only operation. Returns matching document
    references and passages. Does not execute remediation.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if len(query) > 2000:
        raise ValueError("Query exceeds maximum length")

    if not 1 <= top_k <= 5:
        raise ValueError("top_k must be between 1 and 5")

    service = RetrievalService()

    results = await service.search(
        query=query,
        top_k=top_k,
    )

    filtered = [
        result
        for result in results
        if result["similarity"] >= settings.rag_min_similarity
    ]

    return [
        {
            "document_key": item["document_key"],
            "chunk_index": item["chunk_index"],
            "content": item["content"][:4000],
            "similarity": round(item["similarity"], 4),
        }
        for item in filtered
    ]


@mcp.tool()
def get_operations_status() -> dict:
    """
    Return static MCP service information.
    Does not claim to inspect live infrastructure.
    """

    return {
        "service": "OpsPilot MCP",
        "status": "ready",
        "capabilities": [
            "search_runbooks",
            "get_operations_status",
            "list_runbooks",
            "read_runbook",
        ],
        "read_only": True,
    }


@mcp.tool()
def list_runbooks() -> list[str]:
    """
    List runbooks from the configured S3 bucket.

    Read-only. Only Markdown files under runbooks/ are listed.
    """

    s3 = S3Service()
    keys = []

    paginator = s3.client.get_paginator("list_objects_v2")

    for page in paginator.paginate(
        Bucket=s3.bucket,
        Prefix="runbooks/",
        PaginationConfig={"MaxItems": 100},
    ):
        for obj in page.get("Contents", []):
            key = obj["Key"]

            if key.endswith(".md"):
                keys.append(key)

    return keys


@mcp.tool()
def read_runbook(document_key: str) -> str:
    """
    Read a Markdown runbook from S3.

    Read-only. Maximum object size: 64 KiB.
    """

    if (
        not document_key.startswith("runbooks/")
        or not document_key.endswith(".md")
        or ".." in document_key
        or "\\" in document_key
        or len(document_key) > 256
    ):
        raise ValueError("Invalid runbook key")

    s3 = S3Service()

    try:
        metadata = s3.client.head_object(
            Bucket=s3.bucket,
            Key=document_key,
        )

        if metadata["ContentLength"] > 65536:
            raise ValueError("Runbook exceeds 64 KiB limit")

        response = s3.client.get_object(
            Bucket=s3.bucket,
            Key=document_key,
            Range="bytes=0-65535",
        )

        try:
            data = response["Body"].read(65537)
        finally:
            response["Body"].close()

        if len(data) > 65536:
            raise ValueError("Runbook exceeds 64 KiB limit")

        return data.decode("utf-8")

    except ClientError:
        logger.exception("S3 runbook access failed")
        raise RuntimeError("Unable to read requested runbook") from None

    except UnicodeDecodeError:
        raise ValueError("Runbook is not valid UTF-8") from None


if __name__ == "__main__":
    logger.info("Starting OpsPilot MCP Server")
    mcp.run(transport="stdio")
