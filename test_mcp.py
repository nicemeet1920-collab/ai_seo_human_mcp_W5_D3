import sys
import asyncio

from autogen_ext.tools.mcp import (
    StdioServerParams,
    mcp_server_tools
)


async def main():

    print("Connecting to MCP server...")

    server = StdioServerParams(
        command=sys.executable,
        args=["mcp_server.py"],
        read_timeout_seconds=30,
    )

    tools = await mcp_server_tools(server)

    print("\nMCP connection successful!")
    print("\nAvailable tools:")

    for tool in tools:
        print(f"- {tool.name}")


if __name__ == "__main__":
    asyncio.run(main())