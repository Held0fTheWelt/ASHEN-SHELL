"""Shared canonical story runtime core for World of Shadows.

Language I/O symbols imported from ``language_adapter`` are compatibility re-exports;
new code should use ``ai_stack.language_io`` directly (see SAD D2).
"""

from .language_adapter import (  # deprecated shim — prefer ai_stack.language_io
    build_player_attributed_visible_line,
    clear_language_adapter_caches,
    default_player_intent_commit_flags,
    greeting_imperative_addressee_fragment,
    greeting_imperative_visible_pair,
    load_session_language_model_directive,
    prepare_player_input_semantic_resolution,
    resolve_content_modules_root,
    resolve_string,
)
from .input_interpreter import interpret_player_input
from .model_registry import ModelRegistry, RoutingDecision, RoutingPolicy
from .models import InterpretedInputKind, PlayerInputInterpretation, RuntimeDeliveryHint
from .runtime_delivery import extract_spoken_text_for_delivery, natural_input_to_room_command

__all__ = [
    "build_player_attributed_visible_line",
    "clear_language_adapter_caches",
    "default_player_intent_commit_flags",
    "greeting_imperative_addressee_fragment",
    "greeting_imperative_visible_pair",
    "load_session_language_model_directive",
    "prepare_player_input_semantic_resolution",
    "resolve_content_modules_root",
    "resolve_string",
    "interpret_player_input",
    "ModelRegistry",
    "RoutingDecision",
    "RoutingPolicy",
    "InterpretedInputKind",
    "PlayerInputInterpretation",
    "RuntimeDeliveryHint",
    "extract_spoken_text_for_delivery",
    "natural_input_to_room_command",
]
