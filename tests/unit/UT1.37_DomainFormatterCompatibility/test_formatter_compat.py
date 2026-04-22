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

from cloud_dog_llm.compat.formatter_compat import FormatterCompatibilityAdapter
from cloud_dog_llm.prompts.registry import PromptTemplate


def test_wrap_and_render_preserves_formatter_output() -> None:
    adapter = FormatterCompatibilityAdapter()

    def domain_formatter(values: dict[str, object]) -> str:
        return f"Hello {values['name']}"

    template = adapter.wrap(name="greet", version="1", formatter=domain_formatter)
    assert adapter.render(template, {"name": "Gary"}) == "Hello Gary"


def test_chain_order_is_preserved() -> None:
    adapter = FormatterCompatibilityAdapter()

    t1 = adapter.wrap(name="first", version="1", formatter=lambda v: f"A:{v['x']}")
    t2 = PromptTemplate(name="second", version="1", template="B:{{ x }}")
    out = adapter.render_chain([t1, t2], {"x": "ok"})
    assert out == ["A:ok", "B:ok"]


def test_missing_formatter_raises() -> None:
    adapter = FormatterCompatibilityAdapter()
    missing = PromptTemplate(name="missing", version="1", template="{{compat:missing@1}}")
    with pytest.raises(KeyError):
        adapter.render(missing, {})
