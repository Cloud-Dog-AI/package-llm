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

# cloud_dog_llm — Resource-aware LLM invocation (PS-95 §6, W28D-310)
"""Submit LLM calls through cloud_dog_jobs with resource=llm-pool constraints.

Production paths use QUEUED mode (default) which enforces resource-pool limits.
Direct mode is an explicit opt-in for short unit tests only.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from cloud_dog_llm.domain.models import LLMRequest, LLMResponse, SessionContext


class JobMode(enum.Enum):
    """Invocation mode for LLM calls."""

    QUEUED = "queued"
    """Submit through cloud_dog_jobs with resource constraints (production default)."""

    DIRECT = "direct"
    """Bypass queue — explicit opt-in for short unit tests only."""


_DEFAULT_LLM_POOL_NAME = "llm-pool"
_DEFAULT_LLM_POOL_SLOTS = 1


@dataclass
class LLMJobConfig:
    """Configuration for resource-aware LLM invocation."""

    mode: JobMode = JobMode.QUEUED
    """Invocation mode. QUEUED is the production default."""

    pool_name: str = _DEFAULT_LLM_POOL_NAME
    """Resource pool name for LLM slots."""

    slots_per_request: int = _DEFAULT_LLM_POOL_SLOTS
    """Number of pool slots each LLM request consumes."""

    job_type: str = "llm_invocation"
    """Job type string used in cloud_dog_jobs submissions."""


@dataclass
class ResourceAwareLLMInvoker:
    """Wrap an LLM chat callable with cloud_dog_jobs resource-pool submission.

    In QUEUED mode, each invocation is submitted as a job with
    ``resources={config.pool_name: config.slots_per_request}``, enforcing
    concurrency limits via the jobs scheduler.

    In DIRECT mode, the LLM callable is invoked immediately with no queue
    or resource accounting.  This is for short unit tests only.
    """

    config: LLMJobConfig
    _submit_job: Callable[..., str] | None = field(default=None, repr=False)
    _get_result: Callable[[str], Awaitable[LLMResponse | None]] | None = field(default=None, repr=False)
    _direct_invoke: Callable[[LLMRequest, SessionContext], Awaitable[LLMResponse]] | None = field(
        default=None, repr=False
    )

    async def invoke(self, request: LLMRequest, session: SessionContext) -> LLMResponse:
        """Invoke an LLM call respecting the configured mode.

        Raises ValueError if DIRECT mode is used without an explicit
        direct_invoke callable (prevents accidental bypass).
        """
        if self.config.mode is JobMode.DIRECT:
            if self._direct_invoke is None:
                raise ValueError(
                    "DIRECT mode requires an explicit direct_invoke callable. "
                    "Production paths must use QUEUED mode."
                )
            return await self._direct_invoke(request, session)

        if self._submit_job is None or self._get_result is None:
            raise ValueError(
                "QUEUED mode requires submit_job and get_result callables."
            )

        job_id = self._submit_job(
            job_type=self.config.job_type,
            payload={
                "provider_id": request.provider_id,
                "model": request.model,
                "messages": [
                    {"role": m.role, "content": m.content} for m in request.messages
                ],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
            },
            resources={self.config.pool_name: self.config.slots_per_request},
        )

        result = await self._get_result(job_id)
        if result is None:
            raise RuntimeError(f"LLM job {job_id} returned no result")
        return result
