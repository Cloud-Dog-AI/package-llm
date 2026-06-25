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

from cloud_dog_llm.security.redaction import redact_secrets


def test_no_secret_literals_in_defaults() -> None:
    text = open("defaults.yaml", "r", encoding="utf-8").read().lower()
    assert "sk-" not in text
    assert "password=" not in text


def test_redaction_masks_common_secret_patterns() -> None:
    msg = "Authorization: Bearer abcdefghijkl api_key=sk-test-1234"
    redacted = redact_secrets(msg)
    assert "abcdefgh" not in redacted
    assert "sk-test-1234" not in redacted
