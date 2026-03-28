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

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ToolsPolicy:
    """Represent tools policy."""
    allow: set[str] = field(default_factory=set)
    deny: set[str] = field(default_factory=set)

    def allowed(self, tool_id: str) -> bool:
        """Handle allowed."""
        if tool_id in self.deny:
            return False
        if self.allow and tool_id not in self.allow:
            return False
        return True
