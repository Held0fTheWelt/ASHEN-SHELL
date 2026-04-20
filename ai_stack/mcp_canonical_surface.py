"""Canonical MCP surface for AI agents."""

from typing import Dict, List, Any


class CanonicalMCPSurface:
    """Defines MCP surface for AI agent use."""

    TOOLS: List[Dict[str, Any]] = [
        {
            "name": "wos.session.get",
            "description": "Get full session state including players, history, and current world state",
            "input_schema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID"}
                },
                "required": ["session_id"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "state": {"type": "object"},
                    "turn_number": {"type": "integer"}
                }
            }
        },
        {
            "name": "wos.session.state",
            "description": "Get current game state snapshot (lightweight)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"}
                },
                "required": ["session_id"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "state": {"type": "object"},
                    "version": {"type": "integer"}
                }
            }
        },
        {
            "name": "wos.session.logs",
            "description": "Get turn history and logs",
            "input_schema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["session_id"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "history": {"type": "array"}
                }
            }
        },
        {
            "name": "wos.session.diag",
            "description": "Get diagnostic info (errors, degraded states)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"}
                },
                "required": ["session_id"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "diagnostics": {"type": "object"},
                    "errors": {"type": "array"},
                    "degraded": {"type": "boolean"}
                }
            }
        },
        {
            "name": "wos.session.execute_turn",
            "description": "Execute a player action and advance the session",
            "input_schema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "player_id": {"type": "string"},
                    "action": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "target": {"type": "string"},
                            "parameters": {"type": "object"}
                        },
                        "required": ["type"]
                    }
                },
                "required": ["session_id", "player_id", "action"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "new_turn_number": {"type": "integer"},
                    "state_delta": {"type": "object"}
                }
            }
        }
    ]

    def list_tool_specs(self) -> List[Dict[str, Any]]:
        """List all tool specifications."""
        return self.TOOLS

    def get_tool_spec(self, tool_name: str) -> Dict[str, Any]:
        """Get spec for a specific tool."""
        for tool in self.TOOLS:
            if tool["name"] == tool_name:
                return tool
        return None
