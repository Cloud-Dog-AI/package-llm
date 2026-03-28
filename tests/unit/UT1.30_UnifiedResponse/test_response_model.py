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

import httpx

from cloud_dog_llm.multimodal.handler import normalise_content, to_provider_text
from cloud_dog_llm.domain.models import LLMResponse, Usage
from cloud_dog_llm.testing.vcr import SimpleVCR


def test_response_model_has_usage_and_metadata() -> None:
    rsp = LLMResponse(
        request_id="r1",
        provider_id="ollama",
        model_id="qwen",
        content="ok",
        usage=Usage(total_tokens=3),
    )
    assert rsp.request_id == "r1"
    assert rsp.usage.total_tokens == 3


def test_multimodal_content_normalisation() -> None:
    parts = normalise_content(
        [
            {"type": "text", "text": "hello"},
            {"type": "image_url", "image_url": "https://img/1.png"},
        ]
    )
    assert len(parts) == 2
    text = to_provider_text(parts)
    assert "hello" in text
    assert "[image:https://img/1.png]" in text


def test_simple_vcr_records_and_replays(tmp_path) -> None:
    cassette = tmp_path / "llm.json"
    vcr = SimpleVCR(str(cassette))
    req = httpx.Request("POST", "https://example.test/chat", content=b'{"a":1}')
    resp = httpx.Response(200, content=b'{"ok":true}', request=req, headers={"Content-Type": "application/json"})
    vcr.record(req, resp)
    vcr.save()

    reloaded = SimpleVCR(str(cassette))
    replayed = reloaded.replay(req)
    assert replayed is not None
    assert replayed.status_code == 200
    assert replayed.text == '{"ok":true}'
