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

from __future__ import annotations

import uuid

from cloud_dog_llm.domain.models import Message
from cloud_dog_llm.runtime.session import ensure_session


def sample_messages() -> list[Message]:
    """Handle sample messages."""
    return [Message(role="user", content="hello")]


def sample_session():
    """Handle sample session."""
    return ensure_session(None)


def random_correlation_id() -> str:
    """Handle random correlation id."""
    return uuid.uuid4().hex
