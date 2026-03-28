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

# cloud_dog_llm — Domain errors
"""Portable error taxonomy for provider-agnostic callers."""

from __future__ import annotations


class LLMError(Exception):
    """Base error for all cloud_dog_llm failures."""

    def __init__(self, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


class AuthError(LLMError):
    """Represent auth error."""
    pass


class RateLimitError(LLMError):
    """Represent rate limit error."""
    def __init__(self, message: str) -> None:
        super().__init__(message, retryable=True)


class TimeoutError(LLMError):
    """Represent timeout error."""
    def __init__(self, message: str) -> None:
        super().__init__(message, retryable=True)


class ProviderUnavailableError(LLMError):
    """Represent provider unavailable error."""
    def __init__(self, message: str) -> None:
        super().__init__(message, retryable=True)


class InvalidRequestError(LLMError):
    """Represent invalid request error."""
    pass


class StreamingProtocolError(LLMError):
    """Represent streaming protocol error."""
    pass


class ToolExecutionError(LLMError):
    """Represent tool execution error."""
    pass


class CancelledError(LLMError):
    """Represent cancelled error."""
    pass
