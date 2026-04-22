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

import pytest

from cloud_dog_llm.domain.enums import EventType
from cloud_dog_llm.domain.models import LLMEvent
from cloud_dog_llm.runtime.streaming import StreamBuffer


@pytest.mark.asyncio
async def test_stream_buffer_sequence() -> None:
    buf = StreamBuffer(max_events=3)
    await buf.push(LLMEvent(EventType.RESPONSE_STARTED, "r", "p", "m"))
    await buf.push(LLMEvent(EventType.DELTA_TEXT, "r", "p", "m", text="hi"))
    await buf.close()
    events = [e async for e in buf.events()]
    assert [e.type.value for e in events] == ["response_started", "delta_text"]
