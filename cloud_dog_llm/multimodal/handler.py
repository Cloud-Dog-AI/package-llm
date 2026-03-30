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

# cloud_dog_llm — Multimodal content handler
"""Normalise mixed content into portable parts and provider-safe text."""

from __future__ import annotations

from typing import Any

from cloud_dog_llm.multimodal.models import ContentPart, ContentPartType


def normalise_content(content: str | list[dict[str, Any]] | list[ContentPart]) -> list[ContentPart]:
    """Handle normalise content."""
    if isinstance(content, str):
        part = ContentPart(type=ContentPartType.TEXT, text=content)
        part.validate()
        return [part]

    out: list[ContentPart] = []
    for item in content:
        if isinstance(item, ContentPart):
            item.validate()
            out.append(item)
            continue
        if not isinstance(item, dict):
            raise ValueError("Unsupported multimodal content item")
        raw_type = str(item.get("type", "text")).lower()
        if raw_type == "text":
            part = ContentPart(type=ContentPartType.TEXT, text=str(item.get("text", "")))
        elif raw_type == "image_url":
            part = ContentPart(type=ContentPartType.IMAGE_URL, image_url=str(item.get("image_url", "")))
        elif raw_type == "file_ref":
            part = ContentPart(type=ContentPartType.FILE_REF, file_ref=str(item.get("file_ref", "")))
        else:
            raise ValueError(f"Unsupported content part type: {raw_type}")
        part.validate()
        out.append(part)
    return out


def to_provider_text(content: str | list[dict[str, Any]] | list[ContentPart]) -> str:
    """Handle to provider text."""
    parts = normalise_content(content)
    segments: list[str] = []
    for part in parts:
        if part.type is ContentPartType.TEXT:
            segments.append(part.text)
        elif part.type is ContentPartType.IMAGE_URL:
            segments.append(f"[image:{part.image_url}]")
        elif part.type is ContentPartType.FILE_REF:
            segments.append(f"[file:{part.file_ref}]")
    return "\n".join(s for s in segments if s)
