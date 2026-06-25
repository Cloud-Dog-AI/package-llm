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

"""Shared fixtures and strict --env enforcement for cloud_dog_llm tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

_TIER_TOKENS = {"UT", "ST", "IT", "AT", "QT", "PT", "CT"}


def pytest_addoption(parser: pytest.Parser) -> None:
    try:
        parser.addoption(
            "--env",
            action="append",
            default=None,
            help="Path to env file(s) to load (repeatable).",
        )
    except ValueError:
        return


@pytest.fixture(scope="session", autouse=True)
def _require_and_load_env(request: pytest.FixtureRequest) -> None:
    env_args = request.config.getoption("--env")
    if not env_args:
        pytest.fail("Missing required --env argument (for example: --env tests/env-UT)")

    env_files: list[str] = []
    for arg in env_args:
        env_files.extend(_split_env_arg(arg))

    locked = set(os.environ.keys())
    merged: dict[str, str] = {}
    for env_path in env_files:
        _load_env_file(env_path, locked=locked, merged=merged)
    os.environ.update(merged)


def _split_env_arg(arg: str) -> list[str]:
    tests_dir = Path(__file__).resolve().parent
    out: list[str] = []
    for part in arg.split(","):
        token = part.strip()
        if not token:
            continue
        upper = token.upper()
        if upper in _TIER_TOKENS:
            tier_file = tests_dir / f"env-{upper}"
            if tier_file.is_file():
                out.append(str(tier_file))
        else:
            out.append(token)
    return out


def _load_env_file(path: str, *, locked: set[str], merged: dict[str, str]) -> None:
    env_file = Path(path)
    if not env_file.exists():
        pytest.fail(f"Env file not found: {path}")

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            pytest.fail(f"Invalid env file line (expected KEY=value): {raw_line!r}")
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            pytest.fail(f"Invalid env file line (empty key): {raw_line!r}")
        if key in locked:
            continue
        merged[key] = value


@pytest.fixture(scope="session")
def vault_env() -> dict[str, str]:
    required = ["VAULT_ADDR", "VAULT_TOKEN", "VAULT_MOUNT_POINT"]
    return {k: os.environ[k] for k in required if os.environ.get(k)}
