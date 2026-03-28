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

from cloud_dog_llm.compat.response_adapter import ProviderMapping, ResponseAdapter, ResponseNormalisationError


def test_normalises_ollama_openrouter_openai_and_anthropic() -> None:
    adapter = ResponseAdapter()

    ollama = adapter.normalise(
        "ollama",
        {
            "id": "o1",
            "model": "qwen3:14b",
            "message": {"content": "hello"},
            "prompt_eval_count": 5,
            "eval_count": 7,
        },
    )
    assert ollama.content == "hello"
    assert ollama.usage.total_tokens == 12

    openrouter = adapter.normalise(
        "openrouter",
        {
            "id": "or1",
            "model": "qwen/qwen3-14b",
            "choices": [{"message": {"content": "or"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
        },
    )
    assert openrouter.content == "or"
    assert openrouter.usage.total_tokens == 3

    openai = adapter.normalise(
        "openai",
        {
            "id": "oa1",
            "model": "gpt-4o-mini",
            "choices": [{"message": {"content": "oa"}}],
            "usage": {"prompt_tokens": 4, "completion_tokens": 3},
        },
    )
    assert openai.content == "oa"
    assert openai.usage.total_tokens == 7

    anthropic = adapter.normalise(
        "anthropic",
        {
            "id": "an1",
            "model": "claude-3-5-sonnet",
            "content": [{"type": "text", "text": "anthropic"}],
            "usage": {"input_tokens": 8, "output_tokens": 9},
            "stop_reason": "end_turn",
        },
    )
    assert anthropic.content == "anthropic"
    assert anthropic.usage.total_tokens == 17


def test_unknown_provider_raises() -> None:
    with pytest.raises(ResponseNormalisationError):
        ResponseAdapter().normalise("unknown", {"x": 1})


def test_custom_mapping_and_raw_payload_preserved() -> None:
    adapter = ResponseAdapter(
        mappings={
            "custom": ProviderMapping(
                content_path="result.text",
                model_path="meta.model",
                request_id_path="meta.request_id",
                usage_prompt_path="meta.usage.prompt",
                usage_completion_path="meta.usage.completion",
            )
        }
    )
    payload = {
        "meta": {"request_id": "r1", "model": "m1", "usage": {"prompt": 2, "completion": 3}},
        "result": {"text": "ok"},
    }
    rsp = adapter.normalise("custom", payload)
    assert rsp.request_id == "r1"
    assert rsp.model_id == "m1"
    assert rsp.content == "ok"
    assert rsp.usage.total_tokens == 5
    assert rsp.raw_provider_response == payload
