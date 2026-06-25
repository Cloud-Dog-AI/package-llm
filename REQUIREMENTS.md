# platform-llm — Requirements

**Package:** `cloud_dog_llm`  
**Version:** 0.2.0 (pre-release)  
**Standard:** PS-50 (LLM Interfaces)  
**Status:** Draft

---

## Scope / Vision

### SV1.1
The package SHALL provide a single, reusable LLM interface library for all Cloud-Dog Python services, implementing PS-50.

### SV1.2
The package SHALL support pluggable provider adapters, tool/function calling, MCP and A2A client integration, streaming, multimodal I/O, prompt management, and embeddings — all behind stable interfaces.

### SV1.3
The package SHALL work with common Python web stacks (FastAPI recommended) and agent runtimes but MUST NOT be coupled to a single framework.

---

## Business Objectives

### BO1.1
Eliminate per-project LLM client reimplementation — centralise provider logic, timeout/retry handling, and streaming.

### BO1.2
Enable consistent MCP and A2A integration across all services — same transport modes, same tool routing, same session management.

### BO1.3
Support progressive adoption: services can start with basic chat and add tool calling, MCP, and streaming incrementally.

---

## Functional Requirements

### FR1.1 — Provider Adapter Interface
The package MUST define an abstract `ProviderAdapter` interface:
- `invoke(request) -> LLMResponse`
- `invoke_stream(request) -> AsyncIterator[LLMEvent]`
- `health() -> bool`
- `capabilities() -> CapabilityDescriptor`

### FR1.2 — OpenAI-Compatible Adapter
The package MUST provide an adapter for OpenAI-compatible HTTP APIs:
- `/v1/chat/completions` endpoint.
- Bearer token auth.
- Supports local gateways (vLLM, LM Studio), Azure OpenAI, and direct OpenAI.

### FR1.3 — Ollama Adapter
The package MUST provide an Ollama adapter:
- `/api/chat` and `/api/generate` endpoints (with fallback from chat to generate).
- Thinking content extraction (`message.thinking`).
- `/api/tags` health check.

### FR1.4 — OpenRouter Adapter
The package MUST provide an OpenRouter adapter:
- Multi-model gateway with `HTTP-Referer` and `X-Title` headers.
- Reasoning model fallback (`message.reasoning`).

### FR1.5 — Custom / Extension Adapters
Any additional provider MUST be pluggable via the adapter interface without changing the domain API. The package MUST provide a registration mechanism.

### FR1.6 — Model Registry
The package MUST provide a model registry:
- `provider_id`, `model_id`, capabilities (`chat`, `tool_calling`, `vision`, `json_mode`, `embeddings`), `context_window`.
- Static config and optional dynamic discovery.
- `ModelRegistry.get(model_id) -> CapabilityDescriptor`.

### FR1.7 — Chat Interface
The package MUST provide a portable chat interface:
- `system`/`user`/`assistant`/`tool` roles.
- Message content: text, image references, file references, tool call messages/results.
- Conversation state as `Conversation` / `SessionContext`.

### FR1.8 — Completions Interface
The package MUST provide a non-chat completion interface where provider supports it, and emulate where needed.

### FR1.9 — Embeddings Interface
The package MUST provide an embedding interface:
- Single text and batch generation.
- Configurable embedding model (separate from chat model).
- Dimension reporting.
- Ollama and OpenAI-compatible providers (compatible with existing `EmbeddingManager`).

### FR1.10 — Streaming Engine
The package MUST support streaming with a unified event model:
- Events: `response_started`, `delta_text`, `delta_tool_call`, `tool_call_started`, `tool_call_result`, `response_completed`, `response_error`.
- Serialisable to: JSONL, SSE, internal async iterator.
- Backpressure (bounded buffers).
- Client cancellation.
- Continuation via conversation state.

### FR1.11 — Structured Outputs
The package MUST support:
- JSON schema / json_mode (where provider supports).
- Tool/function calling for structured extraction.
- Prompt scaffolding + JSON validation + repair loop (bounded retries) for providers without native support.

### FR1.12 — Tool Definition Model
The package MUST define a unified tool model:
- `tool_id`, `name`, `description`, `input_schema` (JSON Schema), `output_schema`, `execution_mode` (`local`/`remote`/`mcp`/`a2a`), `timeout_ms`, `retries`, `security_context`.

### FR1.13 — Tool Calling Styles
The package MUST support:
- OpenAI-style function calling (tool call objects).
- JSON tool calls embedded in text (detect + parse).
- Provider-specific formats via adapter mapping.

### FR1.14 — Tool Execution Pipeline
The package MUST support:
- Tool selection by model.
- Tool execution (sync/async).
- Result injection back into conversation.
- Parallel tool calls (bounded concurrency).
- Sequential tool calls.
- Tool call cancellation.
- Lifecycle events: `tool_call_started`, `tool_call_succeeded`, `tool_call_failed`, `tool_call_cancelled`.

### FR1.15 — MCP Client (All Transports)
The package MUST include an MCP client supporting:
- Tool discovery (`tools/list`), resource discovery (`resources/list`, `resources/read`).
- Tool invocation (`tools/call`).
- Streaming results.
- Async job mode (`wait=false` → poll `/jobs/{job_id}`).
- **All transport modes**: Streamable HTTP (Mcp-Session-Id header), HTTP JSON-RPC (/messages), Legacy SSE (/sse + /message), stdio (JSON-RPC over stdin/stdout).
- Session management (create on initialize, terminate on DELETE).
- Keep-alive for long-lived SSE streams.
- Retry with exponential backoff + jitter (configurable).

### FR1.16 — A2A Client
The package MUST include an A2A client supporting:
- Request/response (JSON).
- Streaming formats (SSE, chunked, WebSocket, chat-style).
- Envelope normalisation: consistent error model, correlation IDs, tracing headers.
- Topic subscription pattern (as per notification-agent WebSocket topics).

### FR1.17 — Unified Tool Router
The package MUST route tool calls to: local Python tools, MCP tools, A2A tools.
- Policy-driven routing (configurable).
- Auditable (all calls logged with correlation IDs).
- Capability-aware (knows available tools per source).

### FR1.18 — Prompt Registry
The package MUST provide a prompt registry:
- `name`, `version`, `template` (Jinja2), `default_parameters`, `metadata`.
- Deterministic rendering (no hidden randomness).
- System prompts, tool instruction prompts, user prompts, message history assembly.
- Prompt observability: prompt name + version, rendered hash, model/provider, redacted params.

### FR1.19 — Artefact Store
The package MUST provide a provider-agnostic artefact store:
- Local filesystem, S3-compatible (optional), in-memory (testing).
- Metadata: `artefact_id`, `filename`, `mime_type`, `size`, `hash` (SHA-256), `created_at`, `expires_at`, `owner`/`session` linkage.

### FR1.20 — Parameter Passthrough
The package MUST accept and forward:
- Common params: `temperature`, `top_p`, `top_k`, `max_tokens`, `presence_penalty`, `frequency_penalty`, stop sequences, seed, response format, tool choice.
- Provider-specific under `x_provider.*` namespace.
- Capability-aware validation (error or degrade gracefully).

### FR1.21 — Timeouts and Retries
The package MUST support configurable timeouts:
- `connect_timeout` (30s), `read_timeout` (300s), `overall_timeout` (480s).
- Bounded retries with exponential backoff + jitter.
- Provider-aware retry rules.
- Retryable codes: 502, 503, 504, connection/timeout errors.

### FR1.22 — Cancellation
- Client cancels stream.
- Server cancels tool calls.
- Cascading cancellation.

### FR1.23 — Session Context
All calls MUST carry `SessionContext`: `session_id`, `conversation_id`, `user_id`, `tenant_id`, `correlation_id`.

### FR1.24 — Unified Response Model
All calls MUST return `LLMResponse`: `request_id`, `provider_id`, `model_id`, `content`, `tool_calls`, `usage`, `timing`, `finish_reason`, optional `raw_provider_response`.

### FR1.25 — Error Taxonomy
Portable errors: `AuthError`, `RateLimitError`, `TimeoutError`, `ProviderUnavailableError`, `InvalidRequestError`, `StreamingProtocolError`, `ToolExecutionError`, `CancelledError`.
- Include: correlation_id, provider/model_id, retryable flag, redacted raw error.

### FR1.26 — Audit and Observability
- Correlation IDs on all requests.
- INFO: model, tokens, latency. DEBUG: full prompt/response.
- Secrets MUST be redacted.
- Metrics hooks: request counts, error rates, latency, token usage, tool call counts.
- OpenTelemetry integration (optional).

### FR1.27 — Security / Governance
- Allow/deny lists for models/providers per environment.
- Max prompt size and max output tokens per policy.
- Content redaction hooks.
- Restricted tools policies.
- All credential fields (API keys, bearer tokens, provider URLs) MUST arrive pre-resolved by `cloud_dog_config` (PS-80). This package MUST NOT read `os.environ` for credentials, import `hvac`, navigate Vault JSON, or implement its own secret resolution logic.

### FR1.28 — Tool Output Reduction
Configurable MCP tool output reducer: `mcp.output.{format, max_items, max_chars, max_field_chars, fields}`.

### FR1.29 — Configuration via Platform Config
All settings via `cloud_dog_config` (PS-80): `llm.*`, `mcp.*`, `a2a.*`, `embeddings.*`.

### FR1.29a — Vault Config Sections for LLM
IT and AT tests MUST obtain LLM provider credentials from Vault (PS-80 CM9). The Vault config currently contains **24 models** (14 LLM, 10 embedding).

**LLM Models (chat/completions):**

| Vault Path | Model | Provider | URL |
|------------|-------|----------|-----|
| `dev.models.ollama_qwen3_14b_llm1` | `qwen3:14b` | Ollama | `https://llm1.example.test` |
| `dev.models.ollama_qwen3_14b_llm2` | `qwen3:14b` | Ollama | `https://llm2.example.test` |
| `dev.models.ollama_gemma3_12b_llm1` | `gemma3:12b` | Ollama | `https://llm1.example.test` |
| `dev.models.ollama_gemma3_12b_llm2` | `gemma3:12b` | Ollama | `https://llm2.example.test` |
| `dev.models.ollama_gemma3_27b_llm2` | `gemma3:27b` | Ollama | `https://llm2.example.test` |
| `dev.models.ollama_granite4_tiny_h_llm1` | `granite4:tiny-h` | Ollama | `https://llm1.example.test` |
| `dev.models.ollama_ibm_granite4_tiny_h_llm2` | `ibm/granite4:tiny-h` | Ollama | `https://llm2.example.test` |
| `dev.models.ollama_ibm_granite4_small_h_llm2` | `ibm/granite4:small-h` | Ollama | `https://llm2.example.test` |
| `dev.models.openai_qwen3_14b_openrouter_expert` | `qwen/qwen3-14b` | OpenAI-compat | `https://openrouter.ai/api/v1` |
| `dev.models.openai_deepseek_v3_2_openrouter_expert` | `deepseek/deepseek-v3.2` | OpenAI-compat | `https://openrouter.ai/api/v1` |
| `dev.models.vllm_bge_reranker_v2_m3_llm3` | `bge-reranker-v2-m3` | OpenAI-compat (vLLM) | `https://llm3.example.test` |

**Embedding Models (10 total):**

Ollama (self-hosted, no API key):

| Vault Path | Model | Dimensions | URL |
|------------|-------|-----------|-----|
| `dev.models.ollama_bge_m3_567m_llm1` | `bge-m3:567m` | 1024 | `https://llm1.example.test` |
| `dev.models.ollama_bge_m3_567m_llm2` | `bge-m3:567m` | 1024 | `https://llm2.example.test` |
| `dev.models.ollama_nomic_embed_text_llm1` | `nomic-embed-text:latest` | 768 | `https://llm1.example.test` |
| `dev.models.ollama_nomic_embed_text_llm2` | `nomic-embed-text:latest` | 768 | `https://llm2.example.test` |
| `dev.models.ollama_granite_embedding_278m_llm1` | `granite-embedding:278m` | 768 | `https://llm1.example.test` |
| `dev.models.ollama_granite_embedding_278m_llm2` | `granite-embedding:278m` | 768 | `https://llm2.example.test` |

OpenAI-compatible via OpenRouter (requires API key):

| Vault Path | Model | Dimensions | URL |
|------------|-------|-----------|-----|
| `dev.models.openai_text_embedding_baai_bge_m3_openrouter` | `baai/bge-m3` | 1024 | `https://openrouter.ai/api/v1` |
| `dev.models.openai_text_embedding_3_small_openrouter` | `openai/text-embedding-3-small` | 1536 | `https://openrouter.ai/api/v1` |
| `dev.models.openai_text_embedding_3_large_openrouter` | `openai/text-embedding-3-large` | 3072 | `https://openrouter.ai/api/v1` |
| `dev.models.openai_text_embedding_ada_002_openrouter` | `openai/text-embedding-ada-002` | 1536 | `https://openrouter.ai/api/v1` |

Tests MUST be env-gated: skip gracefully if `VAULT_ADDR`/`VAULT_TOKEN` are absent.
UT/ST tests MUST use mock HTTP responses — no real provider calls.

### FR1.30 — Conformance Test Suite
The package MUST include a conformance test suite verifying: adapter interfaces, streaming events, tool calling, parameter passthrough, timeouts/cancellation, MCP/A2A interop.

### FR1.31 — FastMCP Patterns
The package SHOULD support FastMCP-compatible patterns for simplified MCP server creation.

### FR1.32 — Response-Shape Compatibility Adapter
The package MUST provide a `ResponseAdapter` for normalising legacy provider response shapes:
- Translates provider-specific response formats (Ollama, OpenRouter, OpenAI, Anthropic) to the unified `LLMResponse` model.
- Configurable per-provider mappings.
- Legacy response schemas accepted and normalised without loss.
- Use case: expert-agent has bespoke response parsing; sql-agent has mixed provider/runtime pathways.
- **Sources**: expert-agent (response-shape compatibility), sql-agent (mixed provider pathways).

### FR1.33 — Reliability Middleware Hooks
The package MUST support reliability middleware hooks in the LLM request pipeline:
- `pre_request(request) -> request` — invoked before provider call (e.g. rate limiting, circuit breaker check).
- `post_response(response) -> response` — invoked after provider response (e.g. quality scoring, fallback trigger).
- `on_error(error) -> response | raise` — invoked on provider error (e.g. fallback to alternate provider).
- Middleware is composable (list of callables, executed in order).
- **Sources**: expert-agent (reliability hook points), chat-client (bespoke runtime contracts).

### FR1.34 — MCP Transport Migration Matrix
The package MUST provide a documented transport migration matrix:
- Matrix mapping current MCP transports (stdio, SSE, streamable HTTP, HTTP JSON-RPC) to package adapters.
- Migration guide for projects transitioning from bespoke MCP clients.
- Compatibility mode for mixed transport deployments.
- **Source**: expert-agent (MCP transport migration matrix).

### FR1.35 — Queue-Aware Availability Gating
The package SHOULD support queue-aware model availability gating:
- `check_availability(model_id) -> AvailabilityStatus` — returns model availability based on queue depth / rate limits.
- Integration with `cloud_dog_jobs` for async LLM requests.
- Configurable per-model rate limits and queue thresholds.
- **Source**: notification-agent (queue-aware availability gating).

### FR1.36 — Provider Capability Matrix
The package MUST maintain a provider capability matrix:
- Runtime-queryable matrix: `get_capabilities(model_id) -> CapabilityDescriptor`.
- Capabilities: streaming, tool_calling, structured_output, vision, embeddings, max_tokens, context_window.
- Used by runtime parameter validation (FR1.12) and routing decisions.
- **Source**: notification-agent (provider capability matrix).

### FR1.37 — Domain Formatter Stack Migration
The package SHOULD provide migration guidance for domain-heavy formatter stacks:
- Reference pattern for wrapping domain-specific prompt formatters as `PromptTemplate` instances.
- Compatibility adapter for projects with custom formatter chains.
- **Source**: notification-agent (migration guide for domain-heavy formatter stacks).

---

## Non-Functional Requirements

### NF1.1
Runtime dependencies limited to: `httpx`, `pyjwt` (for JWKS), `jinja2` (prompts). Optional: `openai`, `anthropic`, `boto3` (S3 artefacts), `opentelemetry-api`.

### NF1.2
Chat/completion calls (excluding network I/O) MUST add < 5ms overhead.

### NF1.3
All public APIs MUST have async variants. Sync wrappers MAY be provided.

### NF1.4
Python 3.10+.

---

## Cyber Security

### CS1.1
Secrets MUST NEVER be logged or included in error messages.

### CS1.2
API keys transmitted only via headers (never in URLs or logs).

### CS1.3
Content redaction hooks for prompts/responses.

### CS1.4
Tool execution respects security context (restricted tools per session).

---

## Acceptance Criteria

A project is compliant when:
- All LLM calls go through `cloud_dog_llm`.
- Streaming uses the unified event model.
- Tools route via ToolRouter (local + MCP + A2A).
- MCP client supports all transport modes.
- Prompt templates are versioned and rendered via PromptRegistry.
- Calls carry SessionContext + correlation IDs.
- Timeouts/retries/cancellation follow policy.
- No direct `os.environ`, `hvac`, or Vault reads for credentials — all config via `cloud_dog_config` (PS-80).
- Conformance test suite passes in CI.
