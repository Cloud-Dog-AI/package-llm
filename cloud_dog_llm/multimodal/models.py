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

# cloud_dog_llm — Multimodal models
"""Typed content-part models for text/image/file payloads."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ContentPartType(str, Enum):
    """Represent content part type."""
    TEXT = "text"
    IMAGE_URL = "image_url"
    FILE_REF = "file_ref"


@dataclass(frozen=True, slots=True)
class ContentPart:
    """Represent content part."""
    type: ContentPartType
    text: str = ""
    image_url: str = ""
    file_ref: str = ""

    def validate(self) -> None:
        """Handle validate."""
        if self.type is ContentPartType.TEXT and not self.text:
            raise ValueError("Text content part requires non-empty text")
        if self.type is ContentPartType.IMAGE_URL and not self.image_url:
            raise ValueError("Image content part requires image_url")
        if self.type is ContentPartType.FILE_REF and not self.file_ref:
            raise ValueError("File-ref content part requires file_ref")
