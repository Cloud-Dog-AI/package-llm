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

# cloud_dog_llm — Runtime parameter handling
"""Provider-agnostic parameter normalisation for request passthrough."""

from __future__ import annotations

from typing import Any


def split_provider_params(params: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Split general params from provider-scoped keys.

    Keys prefixed with ``x_provider.`` are kept in the provider-specific dict
    with the prefix removed.
    """
    common: dict[str, Any] = {}
    provider: dict[str, Any] = {}
    for key, value in params.items():
        if key.startswith("x_provider."):
            provider[key[len("x_provider.") :]] = value
        else:
            common[key] = value
    return common, provider
