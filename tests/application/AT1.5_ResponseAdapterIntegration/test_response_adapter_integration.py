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

from cloud_dog_llm.compat.response_adapter import ResponseAdapter


def _downstream_projection(response_texts: list[str]) -> str:
    return " | ".join(response_texts)


def test_multi_provider_payloads_are_uniform_after_adaptation() -> None:
    adapter = ResponseAdapter()

    payloads = [
        (
            "ollama",
            {
                "id": "1",
                "model": "qwen3:14b",
                "message": {"content": "from ollama"},
                "prompt_eval_count": 2,
                "eval_count": 3,
            },
        ),
        (
            "openrouter",
            {
                "id": "2",
                "model": "qwen/qwen3-14b",
                "choices": [{"message": {"content": "from openrouter"}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
            },
        ),
        (
            "anthropic",
            {
                "id": "3",
                "model": "claude-3-5-sonnet",
                "content": [{"type": "text", "text": "from anthropic"}],
                "usage": {"input_tokens": 2, "output_tokens": 2},
                "stop_reason": "end_turn",
            },
        ),
    ]

    normalised = [adapter.normalise(provider, payload) for provider, payload in payloads]

    assert [item.provider_id for item in normalised] == ["ollama", "openrouter", "anthropic"]
    assert _downstream_projection([item.content for item in normalised]) == (
        "from ollama | from openrouter | from anthropic"
    )
    assert all(item.raw_provider_response is not None for item in normalised)
