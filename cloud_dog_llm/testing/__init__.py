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

# cloud_dog_llm — testing package

from cloud_dog_llm.testing.conformance import adapter_has_required_methods
from cloud_dog_llm.testing.fixtures import sample_messages
from cloud_dog_llm.testing.mock_providers import MockProvider
from cloud_dog_llm.testing.vcr import SimpleVCR

__all__ = ["adapter_has_required_methods", "MockProvider", "sample_messages", "SimpleVCR"]
