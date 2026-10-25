import sys
import anyio
import logging
import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_TOOLS = {
    "list_runbooks",
    "search_runbooks",
}

MCP_TIMEOUT_SECONDS = 30
MCP_MAX_CONCURRENT_CALLS = 4

_mcp_semaphore = asyncio.Semaphore(MCP_MAX_CONCURRENT_CALLS)


class MCPClientService:

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):
        # Reject unauthorized tools before acquiring resources.
        if tool_name not in ALLOWED_TOOLS:
            raise ValueError("Tool is not allowed")

        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "app.mcp.server"],
            cwd=str(BACKEND_ROOT),
        )

        try:
            # Limit concurrent MCP subprocess operations.
            async with _mcp_semaphore:

                # Limit the execution time after acquiring a slot.
                with anyio.fail_after(MCP_TIMEOUT_SECONDS):

                    async with stdio_client(params) as (read, write):
                        async with ClientSession(read, write) as session:

                            await session.initialize()

                            result = await session.call_tool(
                                tool_name,
                                arguments=arguments,
                            )

                            if result.isError:
                                raise RuntimeError("MCP tool execution failed")

                            if result.structuredContent is not None:
                                return result.structuredContent

                            return [
                                block.text
                                for block in result.content
                                if block.type == "text"
                            ]

        except TimeoutError:
            logger.warning(
                "MCP execution timed out: %s",
                tool_name,
            )
            raise RuntimeError("MCP tool execution timed out") from None
