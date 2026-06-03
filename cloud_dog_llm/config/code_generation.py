# Copyright 2026 Cloud-Dog, Viewdeck Engineering Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# cloud_dog_llm - Code-generation model selection
"""Config-only model selection for PS-96 code generation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CodeGenerationModelChoice:
    """Represent the selected model for code generation."""

    model: str
    provider_id: str | None = None
    source: str = "caller"
    config_key: str | None = None


def select_code_generation_model(
    config: dict[str, Any] | None,
    *,
    caller_model: str | None,
    caller_provider_id: str | None = None,
    service_name: str | None = None,
) -> CodeGenerationModelChoice:
    """Select the code-generation model, defaulting to the caller model.

    The caller supplies a config dictionary already resolved by the platform
    config layer. This helper does not read environment variables, Vault, or
    provider APIs.
    """
    raw_config = config if isinstance(config, dict) else {}
    for key, value in _candidate_values(raw_config, service_name=service_name):
        choice = _choice_from_value(
            value,
            source="config",
            config_key=key,
            fallback_provider_id=caller_provider_id,
        )
        if choice is not None:
            return choice

    if caller_model and caller_model.strip():
        return CodeGenerationModelChoice(
            model=caller_model,
            provider_id=caller_provider_id,
            source="caller",
            config_key=None,
        )

    raise ValueError("No code-generation model configured and caller_model was empty")


def _candidate_values(config: dict[str, Any], *, service_name: str | None) -> list[tuple[str, Any]]:
    """Return config candidates in precedence order."""
    candidates: list[tuple[str, Any]] = []
    service_key = _normalise_service_key(service_name)
    if service_key:
        candidates.extend(
            [
                (
                    f"models.code_generation_{service_key}",
                    _get_nested(config, "models", f"code_generation_{service_key}"),
                ),
                (
                    f"llm.code_generation.services.{service_key}",
                    _get_nested(config, "llm", "code_generation", "services", service_key),
                ),
                (
                    f"code_generation.services.{service_key}",
                    _get_nested(config, "code_generation", "services", service_key),
                ),
            ]
        )

    candidates.extend(
        [
            ("models.code_generation_default", _get_nested(config, "models", "code_generation_default")),
            ("llm.code_generation", _get_nested(config, "llm", "code_generation")),
            ("code_generation", _get_nested(config, "code_generation")),
        ]
    )
    return candidates


def _choice_from_value(
    value: Any,
    *,
    source: str,
    config_key: str,
    fallback_provider_id: str | None,
) -> CodeGenerationModelChoice | None:
    """Build a choice from a supported config value."""
    if isinstance(value, str):
        model = value.strip()
        if model:
            return CodeGenerationModelChoice(
                model=model,
                provider_id=fallback_provider_id,
                source=source,
                config_key=config_key,
            )
        return None

    if not isinstance(value, dict):
        return None

    model = str(value.get("model") or value.get("model_id") or "").strip()
    if not model:
        return None

    provider_id = value.get("provider_id") or value.get("provider") or fallback_provider_id
    return CodeGenerationModelChoice(
        model=model,
        provider_id=str(provider_id) if provider_id else None,
        source=source,
        config_key=config_key,
    )


def _get_nested(config: dict[str, Any], *keys: str) -> Any:
    """Read a nested config value."""
    current: Any = config
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _normalise_service_key(service_name: str | None) -> str:
    """Normalise service names for config keys."""
    if not service_name:
        return ""
    return re.sub(r"[^a-z0-9]+", "_", service_name.lower()).strip("_")
