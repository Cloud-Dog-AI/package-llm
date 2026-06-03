# Copyright 2026 Cloud-Dog, Viewdeck Engineering Limited
# W28D-310 / PS-95 §6 — LLM resource-aware invocation tests

from __future__ import annotations

import asyncio
from collections import Counter
from unittest.mock import AsyncMock

import pytest

from cloud_dog_llm.domain.models import LLMRequest, LLMResponse, Message, SessionContext, Usage
from cloud_dog_llm.runtime.job_invoker import (
    JobMode,
    LLMJobConfig,
    ResourceAwareLLMInvoker,
)


def _session() -> SessionContext:
    return SessionContext(session_id="s1", correlation_id="c1")


def _request() -> LLMRequest:
    return LLMRequest(
        provider_id="ollama",
        model="test-model",
        messages=[Message(role="user", content="hello")],
    )


def _response() -> LLMResponse:
    return LLMResponse(
        request_id="r1",
        provider_id="ollama",
        model_id="test-model",
        content="world",
        usage=Usage(prompt_tokens=5, completion_tokens=3, total_tokens=8),
    )


# ── UT-B6-01: Default mode is QUEUED ──


def test_default_mode_is_queued():
    """UT-B6-01: LLMJobConfig defaults to QUEUED mode."""
    config = LLMJobConfig()
    assert config.mode is JobMode.QUEUED


# ── UT-B6-02: DIRECT mode requires explicit callable ──


@pytest.mark.asyncio
async def test_direct_mode_without_callable_raises():
    """UT-B6-02: DIRECT mode without explicit direct_invoke raises ValueError."""
    config = LLMJobConfig(mode=JobMode.DIRECT)
    invoker = ResourceAwareLLMInvoker(config=config)
    with pytest.raises(ValueError, match="DIRECT mode requires an explicit"):
        await invoker.invoke(_request(), _session())


# ── UT-B6-03: DIRECT mode with callable works ──


@pytest.mark.asyncio
async def test_direct_mode_with_callable_invokes():
    """UT-B6-03: DIRECT mode with explicit callable invokes immediately."""
    config = LLMJobConfig(mode=JobMode.DIRECT)
    mock_invoke = AsyncMock(return_value=_response())
    invoker = ResourceAwareLLMInvoker(
        config=config,
        _direct_invoke=mock_invoke,
    )
    result = await invoker.invoke(_request(), _session())
    assert result.content == "world"
    mock_invoke.assert_called_once()


# ── UT-B6-04: QUEUED mode submits job with resources ──


@pytest.mark.asyncio
async def test_queued_mode_submits_with_resources():
    """UT-B6-04: QUEUED mode submits through job queue with llm-pool resource."""
    submitted = {}

    def fake_submit(*, job_type, payload, resources):
        submitted["job_type"] = job_type
        submitted["resources"] = resources
        submitted["payload"] = payload
        return "job-123"

    async def fake_get_result(job_id):
        assert job_id == "job-123"
        return _response()

    config = LLMJobConfig(mode=JobMode.QUEUED)
    invoker = ResourceAwareLLMInvoker(
        config=config,
        _submit_job=fake_submit,
        _get_result=fake_get_result,
    )
    result = await invoker.invoke(_request(), _session())
    assert result.content == "world"
    assert submitted["resources"] == {"llm-pool": 1}
    assert submitted["job_type"] == "llm_invocation"


# ── UT-B6-05: Max 2 concurrent LLM-resource jobs enforced ──


@pytest.mark.asyncio
async def test_max_two_concurrent_llm_jobs():
    """UT-B6-05: Resource pool with llm-pool=2 allows exactly 2 concurrent jobs, blocks 3rd.

    Uses cloud_dog_jobs ResourcePool + Dispatcher to prove concurrency enforcement.
    """
    from cloud_dog_jobs.backends.memory_backend import MemoryQueueBackend
    from cloud_dog_jobs.domain.models import JobRequest, Job
    from cloud_dog_jobs.domain.enums import JobStatus
    from cloud_dog_jobs.scheduler.resource_pool import ResourcePool, ResourcePoolConfig
    from cloud_dog_jobs.scheduler.concurrency import ConcurrencyLimits, ConcurrencyManager
    from cloud_dog_jobs.scheduler.dispatcher import Dispatcher

    # Resource pool: llm-pool max 2 slots
    pool_config = ResourcePoolConfig(limits={"llm-pool": 2})
    pool = ResourcePool(pool_config)
    concurrency = ConcurrencyManager(ConcurrencyLimits(global_max=10))
    backend = MemoryQueueBackend()

    dispatcher = Dispatcher(
        backend=backend,
        concurrency=concurrency,
        resource_pool=pool,
    )

    # Submit 3 LLM jobs
    jobs = []
    for i in range(3):
        req = JobRequest(job_type="llm_invocation", resources={"llm-pool": 1})
        job = Job.from_request(req)
        backend.enqueue(job)
        jobs.append(job)

    # Select eligible — should return at most 2
    eligible = dispatcher.select_eligible(limit=10)
    assert len(eligible) == 2, f"Expected 2 eligible, got {len(eligible)}"

    # The 3rd job must be blocked (pool exhausted)
    remaining = dispatcher.select_eligible(limit=10)
    assert len(remaining) == 0, "3rd job should be blocked by pool limit"

    # Release one slot — 3rd job becomes eligible
    dispatcher.release_job(eligible[0])
    freed = dispatcher.select_eligible(limit=10)
    assert len(freed) == 1, "After release, 3rd job should be eligible"


# ── UT-B6-06: Production path cannot accidentally reach DIRECT ──


def test_production_config_cannot_reach_direct():
    """UT-B6-06: Default LLMJobConfig + ResourceAwareLLMInvoker cannot invoke in DIRECT mode."""
    config = LLMJobConfig()  # defaults to QUEUED
    invoker = ResourceAwareLLMInvoker(config=config)
    # Mode is QUEUED — cannot call direct
    assert invoker.config.mode is JobMode.QUEUED
    # Even if someone tries to hack mode after construction:
    invoker.config.mode = JobMode.DIRECT
    # Still fails because _direct_invoke is None
    import asyncio
    with pytest.raises(ValueError, match="DIRECT mode requires"):
        asyncio.get_event_loop().run_until_complete(
            invoker.invoke(_request(), _session())
        )
