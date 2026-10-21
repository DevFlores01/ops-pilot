import asyncio
import json
import sys

from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    backend_root = Path(__file__).resolve().parents[2]

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.server"],
        cwd=str(backend_root),
    )

    async with stdio_client(server_params) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            # Discover available tools.
            tools = await session.list_tools()

            print("\nAvailable MCP tools:")

            for tool in tools.tools:
                print(f"- {tool.name}")

            # Call the read-only status tool.
            status_result = await session.call_tool(
                "get_operations_status",
                arguments={},
            )

            if status_result.isError:
                raise RuntimeError(f"Status tool failed {status_result.content}")

            print("\nOperations status:")
            for block in status_result.content:
                if block.type == "text":
                    print(block.text)

            # List runbooks from Floci S3
            list_result = await session.call_tool(
                "list_runbooks",
                arguments={},
            )

            if list_result.isError:
                raise RuntimeError(f"List runbooks failed: {list_result.content}")

            print("\nS3 runbooks:")

            for block in list_result.content:
                if block.type == "text":
                    print(block.text)

            # Read one approved runbook.
            read_result = await session.call_tool(
                "read_runbook",
                arguments={"document_key": "runbooks/redis-cache-runbook.md"},
            )

            if read_result.isError:
                raise RuntimeError(f"Read runbook failed {read_result.content}")

            print("\nRedis runbook content:")

            for block in read_result.content:
                if block.type == "text":
                    print(block.text)

            # Search existing runbooks.
            search_result = await session.call_tool(
                "search_runbooks",
                arguments={
                    "query": ("Why is my kubernetes pod in CrashLoopBackOff?"),
                    "top_k": 3,
                },
            )

            if search_result.isError:
                raise RuntimeError(f"Runbook search failed: {search_result.content}")

            print("\nRunbook search results:")

            if search_result.structuredContent is not None:
                print(
                    json.dumps(
                        search_result.structuredContent,
                        indent=2,
                    )
                )
            else:
                for block in search_result.content:
                    if block.type == "text":
                        print(block.text)

            invalid_result = await session.call_tool(
                "read_runbook",
                arguments={"document_key": "private/secrets.md"},
            )

            assert invalid_result.isError
            print("PASS: Unauthorized S3 key rejected")


if __name__ == "__main__":
    asyncio.run(main())
