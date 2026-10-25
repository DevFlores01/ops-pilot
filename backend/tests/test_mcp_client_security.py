import pytest

from app.services.mcp_client_service import MCPClientService


@pytest.mark.asyncio
async def test_disallowed_tool_rejected():
    service = MCPClientService()

    with pytest.raises(
        ValueError,
        match="Tool is not allowed",
    ):
        await service.call_tool("delete_runbook", arguments={})


@pytest.mark.asyncio
async def test_arbitrary_shell_tool_rejected():
    service = MCPClientService()

    with pytest.raises(
        ValueError,
        match="Tool is not allowed",
    ):
        await service.call_tool(
            "execute_shell_command",
            arguments={"command": "whoami"},
        )
