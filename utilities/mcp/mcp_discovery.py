# =============================================================================
# utilities/mcp/mcp_discovery.py
# =============================================================================
# 🎯 Purpose:
# Loads an MCP (Model Context Protocol) configuration file listing one or
# more MCP servers, and exposes a simple API to retrieve their definitions.
# =============================================================================

import os
import json
import logging
from typing import Dict, Any

# Setup logger for diagnostics
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MCPDiscovery:
    """
    🔍 Reads a JSON config file defining MCP servers and provides access
    to the server definitions under the "mcpServers" key.

    Usage:
        discovery = MCPDiscovery()
        servers = discovery.list_servers()
        # -> {'symptom_checker': {...}, 'appointment': {...}}
    """

    def __init__(self, config_file: str = None):
        """
        Args:
            config_file (str, optional): Path to config file. Defaults to `mcp_config.json`
                                         in the same directory as this script.
        """
        self.config_file = config_file or os.path.join(
            os.path.dirname(__file__), "mcp_config.json"
        )
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load and parse the MCP config file.

        Returns:
            dict: Parsed config, or empty dict on failure.
        """
        try:
            with open(self.config_file, "r") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("Expected JSON object at top level.")

            return data

        except FileNotFoundError:
            logger.warning(f"[MCPDiscovery] Config file not found: {self.config_file}")
            return {}

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"[MCPDiscovery] Error parsing config: {e}")
            return {}

    def list_servers(self) -> Dict[str, Any]:
        """
        Returns:
            dict: Mapping of server names to {command, args} entries.
                  Example:
                    {
                        "symptom_checker": {
                            "command": "python",
                            "args": ["symptom_checker.py"]
                        }
                    }
        """
        return self.config.get("mcpServers", {})
