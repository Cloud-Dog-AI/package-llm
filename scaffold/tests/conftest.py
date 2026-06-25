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

# cloud_dog_llm — Shared test configuration
"""
Shared fixtures and --env enforcement for cloud_dog_llm tests.
"""

import os
import pytest


def pytest_addoption(parser):
    """Add --env option for test environment selection."""
    parser.addoption(
        "--env",
        action="store",
        default="UT",
        help="Test environment tier: UT, ST, IT, AT, QT",
    )


@pytest.fixture(scope="session")
def env_tier(request):
    """Return the current test environment tier."""
    return request.config.getoption("--env").upper()


@pytest.fixture(scope="session")
def vault_env():
    """Validate Vault environment variables are present for integration tests."""
    required = ["VAULT_ADDR", "VAULT_TOKEN", "VAULT_MOUNT_POINT"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        pytest.skip(
            f"Vault credentials not in environment (missing: {', '.join(missing)}). "
            f"Source env-vault first: set -a; source /opt/iac/Development/cloud-dog-ai/env-vault; set +a"
        )
    return {k: os.environ[k] for k in required}


@pytest.fixture(scope="session")
def ollama_env(vault_env):
    """Validate an Ollama instance is available for IT tests."""
    ollama_url = os.environ.get("OLLAMA_BASE_URL", "")
    if not ollama_url:
        pytest.skip(
            "OLLAMA_BASE_URL not set — skipping Ollama IT tests. Set via Vault config (dev.models.ollama_*) or env var."
        )
    return {"base_url": ollama_url, **vault_env}


@pytest.fixture(scope="session")
def openrouter_env(vault_env):
    """Validate OpenRouter API key is available for IT tests."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        pytest.skip(
            "OPENROUTER_API_KEY not set — skipping OpenRouter IT tests. "
            "Set via Vault config (dev.models.openai_*_openrouter_*) or env var."
        )
    return {"api_key": api_key, **vault_env}
