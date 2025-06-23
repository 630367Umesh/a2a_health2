# =============================================================================
# utilities/mcp/mcp_connect.py
# =============================================================================
# 🎯 Purpose:
# Connect to each MCP server defined in mcp_config.json,
# list available tools, and expose each as an async callable.
# =============================================================================

import os
import json
import asyncio
import logging
from typing import List

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from utilities.mcp.mcp_discovery import MCPDiscovery

# Load environment variables from .env
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MCPTool:
    """
    🛠️ A single callable tool provided by a remote MCP agent.

    Methods:
        - run(args): Calls the tool with arguments via a temporary session.
    """
    def __init__(self, name: str, description: str, input_schema: dict, server_cmd: str, server_args: List[str]):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self._params = StdioServerParameters(command=server_cmd, args=server_args)

    async def run(self, args: dict) -> str:
        """
        Executes the tool via a stdio MCP session.

        Args:
            args (dict): Arguments conforming to input_schema

        Returns:
            str: Tool's response content or raw response string
        """
        async with stdio_client(self._params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                response = await session.call_tool(self.name, args)
                return getattr(response, "content", str(response))


class MCPConnector:
    """
    🔗 Manages discovery and invocation of tools from multiple MCP agents.

    Attributes:
        tools (List[MCPTool]): List of all discovered tools.
    """

    def __init__(self, config_file: str = None):
        self.discovery = MCPDiscovery(config_file=config_file)
        self.tools: List[MCPTool] = []
        self._load_all_tools()

    def _load_all_tools(self):
        """
        Synchronously loads all tools from each MCP server listed in config.
        """
        async def _fetch():
            servers = self.discovery.list_servers()
            for name, info in servers.items():
                cmd = info.get("command")
                args = info.get("args", [])
                logger.info(f"[MCPConnector] Connecting to MCP server: {name}")
                params = StdioServerParameters(command=cmd, args=args)

                try:
                    async with stdio_client(params) as (reader, writer):
                        async with ClientSession(reader, writer) as session:
                            await session.initialize()
                            tool_list = (await session.list_tools()).tools

                            for t in tool_list:
                                tool = MCPTool(
                                    name=t.name,
                                    description=t.description,
                                    input_schema=t.inputSchema,
                                    server_cmd=cmd,
                                    server_args=args
                                )
                                self.tools.append(tool)

                            logger.info(f"[MCPConnector] Loaded {len(tool_list)} tools from {name}")
                except Exception as e:
                    logger.warning(f"[MCPConnector] Failed to load tools from {name}: {e}")

        asyncio.run(_fetch())

    def get_tools(self) -> List[MCPTool]:
        """
        Returns a copy of all registered MCPTool objects.
        """
        return self.tools.copy()

    def get_tool_by_name(self, name: str) -> MCPTool | None:
        """
        Retrieve a tool by its exact name.

        Args:
            name (str): The name of the tool

        Returns:
            MCPTool or None
        """
        return next((tool for tool in self.tools if tool.name == name), None)
