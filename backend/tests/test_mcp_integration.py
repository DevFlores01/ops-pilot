import sys
from pathlib import Path

import pytest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BACKEND_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.asyncio
async def test_mcp_tool_discovery():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.server"],
        cwd=str(BACKEND_ROOT),
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.list_tools()
            names = {tool.name for tool in result.tools}

            assert {
                "search_runbooks",
                "get_operations_status",
                "list_runbooks",
                "read_runbook",
            }.issubset(names)


@pytest.mark.asyncio
async def test_mcp_status_tool():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.server"],
        cwd=str(BACKEND_ROOT),
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "get_operations_status",
                arguments={},
            )

            assert not result.isError

            content = str(result.structuredContent or result.content)
            assert "OpsPilot MCP" in content


@pytest.mark.asyncio
async def test_mcp_rejects_invalid_s3_key():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.server"],
        cwd=str(BACKEND_ROOT),
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "read_runbook",
                arguments={"document_key": "private/secrets.md"},
            )

            assert result.isError
