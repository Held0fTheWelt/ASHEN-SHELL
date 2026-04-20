"""Backend MCP client."""

from typing import Dict, Any
import sys
from pathlib import Path

# Import registry from tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tools"))

from mcp_server.registry import MCPRegistry, ToolSpec
from mcp_server.operating_profile import OperatingProfile, check_tool_access
from mcp_server.handlers import (
    session_get_handler,
    session_state_handler,
    session_logs_handler,
    session_diag_handler,
    session_execute_turn_handler,
)


class MCPClient:
    """Backend client for MCP tools."""

    def __init__(self):
        """Initialize MCP client."""
        self.registry = MCPRegistry()
        self._setup_tools()

    def _setup_tools(self):
        """Register all tools."""
        # Register session tools
        tools = [
            ToolSpec(
                name="get",
                description="Get full session state",
                input_schema={"type": "object", "properties": {"session_id": {"type": "string"}}},
                output_schema={"type": "object"},
                handler=session_get_handler
            ),
            ToolSpec(
                name="state",
                description="Get current game state snapshot",
                input_schema={"type": "object", "properties": {"session_id": {"type": "string"}}},
                output_schema={"type": "object"},
                handler=session_state_handler
            ),
            ToolSpec(
                name="logs",
                description="Get turn history",
                input_schema={"type": "object", "properties": {"session_id": {"type": "string"}, "limit": {"type": "integer"}}},
                output_schema={"type": "object"},
                handler=session_logs_handler
            ),
            ToolSpec(
                name="diag",
                description="Get diagnostic information",
                input_schema={"type": "object", "properties": {"session_id": {"type": "string"}}},
                output_schema={"type": "object"},
                handler=session_diag_handler
            ),
            ToolSpec(
                name="execute_turn",
                description="Execute a turn",
                input_schema={"type": "object", "properties": {"session_id": {"type": "string"}, "player_id": {"type": "string"}, "action": {"type": "object"}}},
                output_schema={"type": "object"},
                handler=session_execute_turn_handler
            ),
        ]

        for tool in tools:
            self.registry.register_tool(tool)

    def call_tool(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        operating_profile: str = "execute"
    ) -> Dict[str, Any]:
        """
        Call an MCP tool.

        Args:
            tool_name: Name of tool (e.g., "wos.session.get")
            input_data: Input parameters
            operating_profile: Operating profile (read_only, execute, admin)

        Returns:
            Result dict with success status
        """
        # Check authorization
        try:
            profile = OperatingProfile(operating_profile)
        except ValueError:
            # Unknown profile -> fail closed (Law 6)
            return {
                "success": False,
                "error": f"Unknown operating profile: {operating_profile}"
            }

        short_name = tool_name.split(".")[-1]  # Get "get" from "wos.session.get"

        if not check_tool_access(profile, short_name):
            return {
                "success": False,
                "error": f"Unauthorized: Tool {tool_name} not available in {operating_profile} profile"
            }

        # Call tool through registry
        registry_result = self.registry.call_tool(short_name, input_data)

        # Flatten result for client
        if registry_result["success"]:
            return {"success": True, **registry_result["result"]}
        else:
            return registry_result
