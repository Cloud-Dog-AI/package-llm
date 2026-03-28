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

# cloud_dog_llm — Queue-aware availability gating
"""Determine model availability from queue depth and rate-limit state."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AvailabilityState(str, Enum):
    """Represent availability state."""
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class AvailabilityStatus:
    """Represent availability status."""
    model_id: str
    state: AvailabilityState
    queue_depth: int
    queue_threshold: int
    rate_limit_remaining: int | None = None


class QueueAwareAvailabilityGate:
    """Represent queue aware availability gate."""
    def __init__(
        self,
        *,
        default_threshold: int = 100,
        degraded_ratio: float = 0.8,
        model_thresholds: dict[str, int] | None = None,
    ) -> None:
        self._default_threshold = max(1, int(default_threshold))
        self._degraded_ratio = min(max(degraded_ratio, 0.1), 0.99)
        self._thresholds = dict(model_thresholds or {})
        self._queue_depths: dict[str, int] = {}

    def set_threshold(self, model_id: str, threshold: int) -> None:
        """Handle set threshold."""
        self._thresholds[model_id] = max(1, int(threshold))

    def update_queue_depth(self, model_id: str, depth: int) -> None:
        """Update queue depth."""
        self._queue_depths[model_id] = max(0, int(depth))

    def check_availability(self, model_id: str, *, rate_limit_remaining: int | None = None) -> AvailabilityStatus:
        """Check availability."""
        threshold = self._thresholds.get(model_id, self._default_threshold)
        depth = self._queue_depths.get(model_id, 0)

        if rate_limit_remaining is not None and rate_limit_remaining <= 0:
            return AvailabilityStatus(
                model_id=model_id,
                state=AvailabilityState.UNAVAILABLE,
                queue_depth=depth,
                queue_threshold=threshold,
                rate_limit_remaining=rate_limit_remaining,
            )

        degraded_at = max(1, int(threshold * self._degraded_ratio))
        if depth >= threshold:
            state = AvailabilityState.UNAVAILABLE
        elif depth >= degraded_at:
            state = AvailabilityState.DEGRADED
        else:
            state = AvailabilityState.AVAILABLE

        return AvailabilityStatus(
            model_id=model_id,
            state=state,
            queue_depth=depth,
            queue_threshold=threshold,
            rate_limit_remaining=rate_limit_remaining,
        )
