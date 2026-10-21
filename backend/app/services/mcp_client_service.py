import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BACKEND_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_TOOLS = {
    "list_runbooks",
    "search_runbooks",
}


class MCPClientService:

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):
        if tool_name not in ALLOWED_TOOLS:
            raise ValueError("Tool is not allowed")

        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "app.mcp.server"],
            cwd=str(BACKEND_ROOT),
        )

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

                return [block.text for block in result.content if block.type == "text"]
