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

from cloud_dog_llm.availability.gating import AvailabilityState, QueueAwareAvailabilityGate


def test_available_degraded_unavailable_states() -> None:
    gate = QueueAwareAvailabilityGate(default_threshold=10, degraded_ratio=0.8)

    gate.update_queue_depth("m1", 0)
    assert gate.check_availability("m1").state is AvailabilityState.AVAILABLE

    gate.update_queue_depth("m1", 8)
    assert gate.check_availability("m1").state is AvailabilityState.DEGRADED

    gate.update_queue_depth("m1", 10)
    assert gate.check_availability("m1").state is AvailabilityState.UNAVAILABLE


def test_per_model_thresholds_and_rate_limit_override() -> None:
    gate = QueueAwareAvailabilityGate(default_threshold=100, model_thresholds={"m2": 3})

    gate.update_queue_depth("m2", 2)
    assert gate.check_availability("m2").state is AvailabilityState.DEGRADED

    status = gate.check_availability("m2", rate_limit_remaining=0)
    assert status.state is AvailabilityState.UNAVAILABLE
    assert status.rate_limit_remaining == 0
