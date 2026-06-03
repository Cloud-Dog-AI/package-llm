# platform-llm

**Package:** `cloud_dog_llm`  
**Standard:** PS-50 (LLM Interfaces)  
**Status:** Pre-release (implemented + tested)

## Purpose

Drop-in Python library implementing the PS-50 LLM interfaces standard. Provides pluggable provider adapters, tool/function calling, MCP and A2A client integration, streaming, multimodal I/O, prompt management, and embeddings.

## Key Features

- **Provider adapters**: Ollama, OpenRouter, OpenAI-compatible, OpenAI, Anthropic — all behind `ProviderAdapter` interface
- **Model registry**: Capability descriptors, static config + dynamic discovery
- **Chat + completions + embeddings**: Unified interface with session context
- **Streaming**: Unified event model (SSE + JSONL + async iterator), backpressure, cancellation
- **Tool/function calling**: OpenAI-style + JSON-in-text detection, parallel/sequential execution pipeline
- **MCP client**: All transports (streamable HTTP, HTTP JSON-RPC, legacy SSE, stdio), session management, async jobs
- **A2A client**: Request/response + streaming, envelope normalisation, topic subscription
- **Unified tool router**: Local + MCP + A2A routing, policy-driven, auditable
- **Prompt registry**: Versioned templates, Jinja2 rendering, observability
- **Artefact store**: Local FS + S3 + in-memory for multimodal I/O
- **Structured outputs**: JSON extraction + repair loop
- **Compatibility adapters**: Response-shape normalisation and domain formatter wrapping
- **Reliability middleware**: `pre_request` / `post_response` / `on_error` hooks
- **Availability gating**: Queue-aware model availability status
- **Error taxonomy**: Portable normalised errors with retryable flags
- **Observability**: Audit events, metrics hooks, OpenTelemetry integration

## Dependencies

- **Required:** `httpx`, `jinja2`
- **Optional:** `pyjwt`, `openai`, `anthropic`, `boto3`, `opentelemetry-api`

## Documents

- [REQUIREMENTS.md](REQUIREMENTS.md) — 31 functional requirements
- [ARCHITECTURE.md](ARCHITECTURE.md) — Module layout, component design, integration pattern
- [MCP-MIGRATION.md](MCP-MIGRATION.md) — MCP transport migration matrix and mixed deployment notes
- [TESTS.md](TESTS.md) — Test plan, directory structure, and v0.2.0 feature coverage

## Quick Start

```python
from cloud_dog_llm import get_llm_client
from cloud_dog_llm.domain.models import LLMRequest, Message, SessionContext

client = get_llm_client(config)
session = SessionContext(session_id="s1", correlation_id="r1")

# Chat
response = await client.chat(
    LLMRequest(messages=[Message(role="user", content="Hello")]),
    session,
)

# Streaming
async for event in client.chat_stream(
    LLMRequest(messages=[Message(role="user", content="Stream this")]),
    session,
):
    print(event.text, end="")
```

## Installation

```bash
pip install cloud-dog-llm
```

## API Overview

- factory helpers build provider-backed LLM clients
- domain models standardise messages, requests, and responses
- tool-routing helpers connect local, MCP, and A2A integrations

## Examples

- Build a provider-backed chat client for service runtimes.
- Stream model output through the unified event interface.
- Route tool calls through local, MCP, or A2A integrations.

---

## Licence

Apache-2.0 — Copyright (c) 2026 Cloud-Dog, Viewdeck Engineering Limited
