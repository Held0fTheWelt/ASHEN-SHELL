"""Compact MCP-safe session surface integrated into the runnable MVP."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class BackendTransport(Protocol):
    """Protocol for invoking backend HTTP-like calls."""

    def get(self, path: str, headers: dict[str, str] | None = None) -> dict[str, Any]: ...
    def post(self, path: str, json_body: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]: ...


@dataclass(frozen=True, slots=True)
class ToolDescriptor:
    name: str
    tool_class: str
    implementation_status: str
    authority_source: str
    permission: str


@dataclass(slots=True)
class ToolDefinition:
    descriptor: ToolDescriptor
    description: str
    handler: Any
    input_schema: dict[str, Any]

    @property
    def name(self) -> str:
        return self.descriptor.name

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.descriptor.name,
            "description": self.description,
            "tool_class": self.descriptor.tool_class,
            "implementation_status": self.descriptor.implementation_status,
            "authority_source": self.descriptor.authority_source,
            "permission": self.descriptor.permission,
            "inputSchema": self.input_schema,
            "governance": {
                "reviewable_posture": "read_only" if self.descriptor.tool_class == "read_only" else "authority_gated",
                "runtime_authority": self.descriptor.authority_source,
            },
        }


TOOL_DESCRIPTORS: tuple[ToolDescriptor, ...] = (
    ToolDescriptor("wos.system.health", "read_only", "implemented", "api_gateway", "read"),
    ToolDescriptor("wos.session.create", "write_capable", "implemented", "world_engine_via_api", "write"),
    ToolDescriptor("wos.session.get", "read_only", "implemented", "world_engine_via_api", "read"),
    ToolDescriptor("wos.session.logs", "read_only", "implemented", "world_engine_via_api", "read"),
    ToolDescriptor("wos.session.state", "read_only", "implemented", "world_engine_via_api", "read"),
    ToolDescriptor("wos.session.diag", "read_only", "implemented", "world_engine_via_api", "read"),
    ToolDescriptor("wos.session.execute_turn", "review_bound", "implemented", "world_engine_via_api", "write"),
)

TOOL_INPUTS: dict[str, dict[str, Any]] = {
    "wos.system.health": {"type": "object", "properties": {}, "required": []},
    "wos.session.create": {"type": "object", "properties": {"module_id": {"type": "string"}}, "required": ["module_id"]},
    "wos.session.get": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    "wos.session.logs": {"type": "object", "properties": {"session_id": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["session_id"]},
    "wos.session.state": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    "wos.session.diag": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    "wos.session.execute_turn": {"type": "object", "properties": {"session_id": {"type": "string"}, "player_input": {"type": "string"}, "prompt": {"type": "string"}}, "required": ["session_id"]},
}

TOOL_DESCRIPTIONS: dict[str, str] = {
    "wos.system.health": "Check runtime health.",
    "wos.session.create": "Create a publish-bound session.",
    "wos.session.get": "Read player-safe session snapshot.",
    "wos.session.logs": "Read operator logs for a session.",
    "wos.session.state": "Read runtime state for a session.",
    "wos.session.diag": "Read operator diagnostics for a session.",
    "wos.session.execute_turn": "Execute a committed player turn via the world-engine authority path.",
}


class ToolRegistry:
    """Simple registry for integrated MCP-safe tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        return [tool.to_dict() for tool in self._tools.values()]


def build_registry(transport: BackendTransport, *, internal_api_key: str) -> ToolRegistry:
    """Build integrated registry and handlers against the runnable service."""

    def internal_headers() -> dict[str, str]:
        return {"X-Internal-API-Key": internal_api_key}

    registry = ToolRegistry()

    handlers = {
        "wos.system.health": lambda arguments: transport.get("/api/v1/health"),
        "wos.session.create": lambda arguments: transport.post(
            "/api/v1/sessions",
            {"module_id": arguments.get("module_id", "god_of_carnage")},
        ),
        "wos.session.get": lambda arguments: transport.get(f"/api/v1/sessions/{arguments['session_id']}"),
        "wos.session.logs": lambda arguments: transport.get(
            f"/api/v1/sessions/{arguments['session_id']}/logs?limit={arguments.get('limit', 100)}",
            headers=internal_headers(),
        ),
        "wos.session.state": lambda arguments: transport.get(
            f"/api/v1/sessions/{arguments['session_id']}/state",
            headers=internal_headers(),
        ),
        "wos.session.diag": lambda arguments: transport.get(
            f"/api/v1/sessions/{arguments['session_id']}/diagnostics",
            headers=internal_headers(),
        ),
        "wos.session.execute_turn": lambda arguments: transport.post(
            f"/api/v1/sessions/{arguments['session_id']}/turns",
            {"player_input": (arguments.get('player_input') or arguments.get('prompt') or '').strip()},
        ),
    }

    for descriptor in TOOL_DESCRIPTORS:
        registry.register(
            ToolDefinition(
                descriptor=descriptor,
                description=TOOL_DESCRIPTIONS[descriptor.name],
                handler=handlers[descriptor.name],
                input_schema=TOOL_INPUTS[descriptor.name],
            )
        )
    return registry
