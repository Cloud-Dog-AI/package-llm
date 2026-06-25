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

"""Read model entries from Vault config using VAULT_* env variables."""

from __future__ import annotations

import json
import os
import ssl
import urllib.request
from typing import Any


def _read_vault_config() -> dict[str, Any]:
    addr = os.environ.get("VAULT_ADDR", "").strip()
    token = os.environ.get("VAULT_TOKEN", "").strip()
    mount = os.environ.get("VAULT_MOUNT_POINT", "").strip("/")
    if not addr or not token or not mount:
        return {}

    path = os.environ.get("VAULT_CONFIG_PATH", "").strip("/")
    url = f"{addr}/v1/{mount}/data/{path}" if path else f"{addr}/v1/{mount}/data"
    req = urllib.request.Request(url, headers={"X-Vault-Token": token})
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=10) as resp:
            raw = json.loads(resp.read())
    except Exception:
        return {}

    blob = raw.get("data", {}).get("data", {})
    if not isinstance(blob, dict):
        return {}
    cfg = blob.get("json", blob)
    if not isinstance(cfg, dict):
        return {}
    if "dev" in cfg and isinstance(cfg["dev"], dict):
        cfg = cfg["dev"]
    return cfg


def get_model_entry(logical_name: str) -> dict[str, Any] | None:
    cfg = _read_vault_config()
    models = cfg.get("models", {})
    if not isinstance(models, dict):
        return None
    if logical_name in models:
        val = models[logical_name]
        return val if isinstance(val, dict) else None
    for key, val in models.items():
        if logical_name in key and isinstance(val, dict):
            return val
    return None


def list_model_entries() -> dict[str, dict[str, Any]]:
    cfg = _read_vault_config()
    models = cfg.get("models", {})
    if not isinstance(models, dict):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for key, val in models.items():
        if isinstance(val, dict):
            out[str(key)] = val
    return out
