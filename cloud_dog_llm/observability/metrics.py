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

import time


class MetricsHooks:
    """Represent metrics hooks."""
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}
        self.timings_ms: dict[str, list[float]] = {}

    def inc(self, key: str) -> None:
        """Handle inc."""
        self.counts[key] = self.counts.get(key, 0) + 1

    def observe_ms(self, key: str, value_ms: float) -> None:
        """Handle observe ms."""
        self.timings_ms.setdefault(key, []).append(float(value_ms))

    def avg_ms(self, key: str) -> float:
        """Handle avg ms."""
        values = self.timings_ms.get(key, [])
        if not values:
            return 0.0
        return sum(values) / len(values)

    def timed(self, key: str):
        """Handle timed."""
        start = time.perf_counter()

        def done() -> float:
            """Handle done."""
            elapsed = (time.perf_counter() - start) * 1000
            self.observe_ms(key, elapsed)
            return elapsed

        return done
