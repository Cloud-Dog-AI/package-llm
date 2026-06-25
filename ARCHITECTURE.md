# platform-llm — Architecture

**Package:** `cloud_dog_llm`  
**Version:** 0.2.0 (pre-release)  
**Standard:** PS-50 (LLM Interfaces)  
**Status:** Draft

---

## OV1 — Overview

`cloud_dog_llm` is a drop-in Python library that implements the PS-50 LLM interfaces standard. It provides pluggable provider adapters, tool/function calling, MCP and A2A client integration, streaming, multimodal I/O, prompt management, embeddings, and a unified tool router — all behind stable, framework-agnostic interfaces.

### Design Goals

- **Hexagonal / ports-and-adapters**: domain logic is provider-agnostic; providers are pluggable adapters.
- **Single implementation** of LLM client, MCP client, A2A client, tool router — no per-project reimplementation.
- **Progressive adoption**: services can start with basic `LLMClient.chat()` and add tool calling, MCP, streaming incrementally.
- **Async-first**: all public APIs have async variants; sync wrappers optional.
- **Framework-optional**: core has no web framework dependency.

---

## SA1 — Module Layout

```
cloud_dog_llm/
  __init__.py                          # Public API: LLMClient, get_llm_client
  config/
    models.py                          # Pydantic settings for LLM, MCP, A2A config
  domain/
    models.py                          # Message, ContentPart, ToolDef, LLMRequest, LLMResponse, LLMEvent
    errors.py                          # Portable error taxonomy
    enums.py                           # FinishReason, EventType, ExecutionMode enums
  registry/
    registry.py                        # Model registry + capability descriptors
    capabilities.py                    # CapabilityDescriptor model
  providers/
    base.py                            # ProviderAdapter interface (ABC)
    openai_compat.py                   # OpenAI-compatible REST adapter
    openai.py                          # First-party OpenAI (optional, extends compat)
    openrouter.py                      # OpenRouter adapter
    ollama.py                          # Ollama adapter (chat + generate fallback)
    anthropic.py                       # Anthropic adapter (planned)
    registry.py                        # Provider registry (configure active adapters)
  embeddings/
    base.py                            # EmbeddingProvider interface
    ollama.py                          # Ollama embedding provider
    openai_compat.py                   # OpenAI-compatible embedding provider
    manager.py                         # EmbeddingManager (batch, dimension, retries)
  prompts/
    registry.py                        # PromptRegistry (name, version, templates)
    render.py                          # Jinja2 deterministic renderer
  tools/
    models.py                          # ToolDef, ToolCall, ToolResult
    router.py                          # Unified ToolRouter (local + MCP + A2A)
    local.py                           # Local tool executor
    schemas.py                         # Tool JSON Schema helpers
    parser.py                          # JSON-in-text tool call detector/parser
    pipeline.py                        # Tool execution pipeline (parallel/sequential)
  mcp/
    client.py                          # MCPClient (all transports)
    transports/
      streamable_http.py               # Streamable HTTP (Mcp-Session-Id header)
      http_jsonrpc.py                  # HTTP JSON-RPC (/messages)
      legacy_sse.py                    # Legacy SSE (/sse + /message)
      stdio.py                         # stdio (JSON-RPC over stdin/stdout)
    session.py                         # MCP session management
    fastmcp.py                         # FastMCP compatibility patterns
  a2a/
    client.py                          # A2AClient (JSON + SSE + WebSocket)
    envelope.py                        # Envelope normalisation
  artefacts/
    base.py                            # ArtefactStore interface
    local.py                           # Local filesystem store
    s3.py                              # S3-compatible store (optional)
    memory.py                          # In-memory store (testing)
  runtime/
    client.py                          # LLMClient (main entry point)
    session.py                         # SessionContext
    streaming.py                       # Streaming engine, event serialisation
    retries.py                         # Retry policy (exponential backoff + jitter)
    timeouts.py                        # Timeout management
    cancellation.py                    # Cancellation propagation
  structured/
    extractor.py                       # Structured output extraction
    repair.py                          # JSON repair loop (bounded retries)
    reducer.py                         # Tool output reducer
  multimodal/
    models.py                          # Typed multimodal content parts
    handler.py                         # Multimodal normalisation / provider flattening
  compat/
    response_adapter.py                # Response-shape compatibility adapter (FR1.32)
    formatter_compat.py                # Domain formatter stack migration (FR1.37)
  middleware/
    base.py                            # Middleware protocol (FR1.33)
    reliability.py                     # Reliability middleware (pre_request, post_response, on_error)
  availability/
    gating.py                          # Queue-aware availability gating (FR1.35)
  observability/
    audit.py                           # Audit event helpers
    metrics.py                         # Metrics hooks
    otel.py                            # OpenTelemetry integration (optional)
    redaction.py                       # Content redaction
  security/
    governance.py                      # Allow/deny lists, max prompt/output size
    tools_policy.py                    # Restricted tools per session
  testing/
    conformance.py                     # Conformance test suite
    mock_providers.py                  # Mock adapters for testing
    fixtures.py                        # Shared test fixtures
    vcr.py                             # Lightweight cassette recorder/replayer
```

---

## SA2 — Component Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                     Service (FastAPI / Agent / CLI)                   │
│                                                                      │
│  LLMClient.chat() / .chat_stream() / .complete() / .embed()         │
│         │                                                            │
│         ▼                                                            │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                  runtime/client.py                        │       │
│  │  SessionContext ──→ correlation_id propagation             │       │
│  │  timeouts.py ──→ connect/read/overall                     │       │
│  │  retries.py ──→ backoff + jitter                          │       │
│  │         │                                                 │       │
│  │         ▼                                                 │       │
│  │  ┌─────────────────────────────────────────────────┐     │       │
│  │  │           providers/registry.py                  │     │       │
│  │  │  Active adapters: [ollama, openrouter, openai]   │     │       │
│  │  │         │                                        │     │       │
│  │  │         ├──→ ollama.py ──→ /api/chat             │     │       │
│  │  │         ├──→ openrouter.py ──→ /api/v1/chat      │     │       │
│  │  │         └──→ openai_compat.py ──→ /v1/chat       │     │       │
│  │  └─────────────────────────────────────────────────┘     │       │
│  │         │                                                 │       │
│  │         ▼ (if tool_calls in response)                     │       │
│  │  ┌─────────────────────────────────────────────────┐     │       │
│  │  │           tools/router.py                        │     │       │
│  │  │  Policy-driven routing to:                       │     │       │
│  │  │         ├──→ tools/local.py (in-process)         │     │       │
│  │  │         ├──→ mcp/client.py (MCP servers)         │     │       │
│  │  │         └──→ a2a/client.py (A2A agents)          │     │       │
│  │  └─────────────────────────────────────────────────┘     │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │ prompts/    │  │ embeddings/ │  │ artefacts/  │                 │
│  │ registry.py │  │ manager.py  │  │ local.py    │                 │
│  │ render.py   │  │ ollama.py   │  │ s3.py       │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
│                                                                      │
│  ┌─────────────────────────────────────────────────┐                │
│  │            observability/                        │                │
│  │  audit.py ← metrics.py ← otel.py ← redaction.py│                │
│  └─────────────────────────────────────────────────┘                │
└──────────────────────────────────────────────────────────────────────┘

MCP Client Transport Detail:
┌─────────────────────────────────────────────────┐
│              mcp/client.py                       │
│                     │                            │
│  ┌─────────────────┼─────────────────────┐      │
│  │ transports/     │                     │      │
│  │  streamable_http.py  ──→ POST /mcp    │      │
│  │  http_jsonrpc.py     ──→ POST /messages│     │
│  │  legacy_sse.py       ──→ GET /sse      │     │
│  │  stdio.py            ──→ stdin/stdout  │     │
│  └────────────────────────────────────────┘     │
│                     │                            │
│  mcp/session.py ──→ Mcp-Session-Id tracking      │
└─────────────────────────────────────────────────┘
```

## MCP Transport Migration Matrix

See `MCP-MIGRATION.md` for the canonical mapping from legacy transport labels to runtime adapters:
- `stdio` → `mcp/transports/stdio.py`
- `SSE` (legacy) → `mcp/transports/legacy_sse.py`
- `streamable HTTP` → `mcp/transports/streamable_http.py`
- `HTTP JSON-RPC` → `mcp/transports/http_jsonrpc.py`

---

## CC1 — Core Components

### CC1.1 LLMClient (`runtime/client.py`)

Central entry point:

```python
class LLMClient:
    def __init__(self, config, provider_registry, tool_router=None): ...
    
    async def chat(self, request: LLMRequest, session: SessionContext) -> LLMResponse: ...
    async def chat_stream(self, request: LLMRequest, session: SessionContext) -> AsyncIterator[LLMEvent]: ...
    async def complete(self, prompt: str, **kwargs) -> LLMResponse: ...
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
    async def health(self) -> bool: ...
```

Orchestrates: provider selection → invoke → tool execution loop → result assembly.

### CC1.2 Provider Adapter Interface (`providers/base.py`)

```python
class ProviderAdapter(ABC):
    @abstractmethod
    async def invoke(self, request: LLMRequest) -> LLMResponse: ...
    @abstractmethod
    async def invoke_stream(self, request: LLMRequest) -> AsyncIterator[LLMEvent]: ...
    @abstractmethod
    async def health(self) -> bool: ...
    def capabilities(self) -> CapabilityDescriptor: ...
```

### CC1.3 Ollama Adapter (`providers/ollama.py`)

- Chat via `/api/chat` with fallback to `/api/generate`.
- Thinking content extraction.
- Separate timeout for connect vs read.
- Health via `/api/tags`.
- Compatible with existing `LLMClient._ollama_chat()` pattern.

### CC1.4 Tool Router (`tools/router.py`)

```python
class ToolRouter:
    def register(self, tool_def: ToolDef, handler: Callable | str): ...
    async def route(self, tool_call: ToolCall, session: SessionContext) -> ToolResult: ...
    def available_tools(self, session: SessionContext) -> list[ToolDef]: ...
```

Routes to: `local.py` (in-process), `mcp/client.py` (MCP servers), `a2a/client.py` (A2A agents).
Policy from config determines routing rules.

### CC1.5 MCP Client (`mcp/client.py`)

```python
class MCPClient:
    @classmethod
    def from_config(cls, config, server_index=0) -> MCPClient: ...
    
    async def initialize(self) -> dict: ...
    async def tools_list(self) -> dict: ...
    async def tools_call(self, name: str, arguments: dict) -> dict: ...
    async def resources_list(self) -> dict: ...
    async def resources_read(self, uri: str) -> dict: ...
    async def health(self) -> dict: ...
    async def aclose(self) -> None: ...
```

Transport selection based on config: `streamable_http`, `http_jsonrpc`, `legacy_sse`, `stdio`.
Session tracking via `Mcp-Session-Id`. Retry with backoff + jitter. Async job polling.

### CC1.6 A2A Client (`a2a/client.py`)

```python
class A2AClient:
    async def call(self, request: A2ARequest) -> A2AResponse: ...
    async def call_stream(self, request: A2ARequest) -> AsyncIterator[A2AEvent]: ...
    async def subscribe(self, topic: str) -> AsyncIterator[A2AEvent]: ...
```

### CC1.7 Streaming Engine (`runtime/streaming.py`)

```python
class StreamingEngine:
    async def stream(self, provider_stream: AsyncIterator) -> AsyncIterator[LLMEvent]: ...
    def to_sse(self, event: LLMEvent) -> str: ...
    def to_jsonl(self, event: LLMEvent) -> str: ...
```

Unified event model with backpressure and cancellation.

### CC1.8 Prompt Registry (`prompts/registry.py`)

```python
class PromptRegistry:
    def register(self, name: str, version: str, template: str, **metadata): ...
    def render(self, name: str, version: str, variables: dict) -> RenderedPrompt: ...
    def get(self, name: str, version: str = "latest") -> PromptTemplate: ...
```

### CC1.9 Embedding Manager (`embeddings/manager.py`)

```python
class EmbeddingManager:
    async def generate_embedding(self, text: str) -> list[float]: ...
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]: ...
    @property
    def dimension(self) -> int: ...
```

Compatible with existing expert-agent `EmbeddingManager`.

### CC1.10 Structured Output Extractor (`structured/extractor.py`)

```python
class StructuredExtractor:
    async def extract_json(self, response: LLMResponse, schema: dict) -> dict: ...
    async def extract_with_repair(self, client: LLMClient, request: LLMRequest, schema: dict, max_retries: int = 3) -> dict: ...
```

---

## DM1 — Data Model

No persistent database. All state is ephemeral (request-scoped or session-scoped).

### Key Domain Objects

| Object | Purpose |
|--------|---------|
| `LLMRequest` | Chat/completion request with messages, params, tools |
| `LLMResponse` | Unified response with content, tool_calls, usage, timing |
| `LLMEvent` | Streaming event (delta_text, tool_call_started, etc.) |
| `ToolDef` | Tool definition with schema, execution mode |
| `ToolCall` | Tool invocation from model |
| `ToolResult` | Tool execution result |
| `SessionContext` | Session/correlation/user/tenant context |
| `CapabilityDescriptor` | Model capabilities |
| `RenderedPrompt` | Rendered prompt with hash and metadata |

---

## DP1 — Dependency Policy

| Dependency | Status | Notes |
|-----------|--------|-------|
| `httpx` | Required | HTTP client for all providers |
| `jinja2` | Required | Prompt template rendering |
| `pyjwt` | Optional | JWKS verification for MCP auth |
| `openai` | Optional | First-party OpenAI SDK |
| `anthropic` | Optional | Anthropic SDK |
| `boto3` | Optional | S3 artefact store |
| `opentelemetry-api` | Optional | Tracing integration |

---

## SE1 — Security Architecture

- API keys transmitted only in headers (never in URLs or logs).
- Content redaction hooks for prompts and responses.
- Tool execution respects security context per session.
- Allow/deny lists for models/providers per environment.
- Max prompt/output size enforcement per policy.
- Secrets via Cloud-Dog config/vault standards (PS-80).

---

## Integration Pattern

```python
from cloud_dog_llm import LLMClient, get_llm_client
from cloud_dog_llm.mcp import MCPClient
from cloud_dog_llm.tools import ToolRouter
from cloud_dog_llm.domain.models import SessionContext

# At startup
client = get_llm_client(config)
mcp = MCPClient.from_config(config)
router = ToolRouter(local_tools=[...], mcp_clients=[mcp])

# Chat with tool calling
session = SessionContext(session_id="s1", correlation_id="r1")
response = await client.chat(request, session)

# Streaming
async for event in client.chat_stream(request, session):
    if event.type == "delta_text":
        print(event.text, end="")

# Embeddings
vectors = await client.embed(["text1", "text2"])

# MCP tool call
tools = await mcp.tools_list()
result = await mcp.tools_call("search", {"query": "example"})
```

## Auto-Declared Source Modules (Traceability Scanner)
<!-- TRACEABILITY-MODULE-LIST:START -->
The list below is generated from the current source tree and kept in sync for architecture-traceability audits.
- `cloud_dog_llm/__init__.py`
- `cloud_dog_llm/a2a/__init__.py`
- `cloud_dog_llm/a2a/client.py`
- `cloud_dog_llm/a2a/envelope.py`
- `cloud_dog_llm/artefacts/__init__.py`
- `cloud_dog_llm/artefacts/base.py`
- `cloud_dog_llm/artefacts/local.py`
- `cloud_dog_llm/artefacts/memory.py`
- `cloud_dog_llm/artefacts/models.py`
- `cloud_dog_llm/artefacts/s3.py`
- `cloud_dog_llm/artefacts/store.py`
- `cloud_dog_llm/availability/__init__.py`
- `cloud_dog_llm/availability/gating.py`
- `cloud_dog_llm/compat/__init__.py`
- `cloud_dog_llm/compat/formatter_compat.py`
- `cloud_dog_llm/compat/response_adapter.py`
- `cloud_dog_llm/config/__init__.py`
- `cloud_dog_llm/config/models.py`
- `cloud_dog_llm/config/registry.py`
- `cloud_dog_llm/config/settings.py`
- `cloud_dog_llm/domain/__init__.py`
- `cloud_dog_llm/domain/enums.py`
- `cloud_dog_llm/domain/errors.py`
- `cloud_dog_llm/domain/models.py`
- `cloud_dog_llm/embeddings/__init__.py`
- `cloud_dog_llm/embeddings/base.py`
- `cloud_dog_llm/embeddings/manager.py`
- `cloud_dog_llm/embeddings/ollama.py`
- `cloud_dog_llm/embeddings/openai_compat.py`
- `cloud_dog_llm/embeddings/providers.py`
- `cloud_dog_llm/factory.py`
- `cloud_dog_llm/mcp/__init__.py`
- `cloud_dog_llm/mcp/client.py`
- `cloud_dog_llm/mcp/fastmcp.py`
- `cloud_dog_llm/mcp/session.py`
- `cloud_dog_llm/mcp/transport.py`
- `cloud_dog_llm/mcp/transports/http_jsonrpc.py`
- `cloud_dog_llm/mcp/transports/legacy_sse.py`
- `cloud_dog_llm/mcp/transports/stdio.py`
- `cloud_dog_llm/mcp/transports/streamable_http.py`
- `cloud_dog_llm/middleware/__init__.py`
- `cloud_dog_llm/middleware/base.py`
- `cloud_dog_llm/middleware/reliability.py`
- `cloud_dog_llm/multimodal/__init__.py`
- `cloud_dog_llm/multimodal/handler.py`
- `cloud_dog_llm/multimodal/models.py`
- `cloud_dog_llm/observability/__init__.py`
- `cloud_dog_llm/observability/audit.py`
- `cloud_dog_llm/observability/logging.py`
- `cloud_dog_llm/observability/metrics.py`
- `cloud_dog_llm/observability/otel.py`
- `cloud_dog_llm/observability/redaction.py`
- `cloud_dog_llm/prompts/__init__.py`
- `cloud_dog_llm/prompts/registry.py`
- `cloud_dog_llm/prompts/render.py`
- `cloud_dog_llm/prompts/template.py`
- `cloud_dog_llm/providers/__init__.py`
- `cloud_dog_llm/providers/anthropic.py`
- `cloud_dog_llm/providers/base.py`
- `cloud_dog_llm/providers/factory.py`
- `cloud_dog_llm/providers/ollama.py`
- `cloud_dog_llm/providers/openai.py`
- `cloud_dog_llm/providers/openai_compat.py`
- `cloud_dog_llm/providers/openrouter.py`
- `cloud_dog_llm/providers/registry.py`
- `cloud_dog_llm/registry/__init__.py`
- `cloud_dog_llm/registry/capabilities.py`
- `cloud_dog_llm/registry/registry.py`
- `cloud_dog_llm/routing/__init__.py`
- `cloud_dog_llm/routing/engine.py`
- `cloud_dog_llm/routing/policies.py`
- `cloud_dog_llm/runtime/__init__.py`
- `cloud_dog_llm/runtime/cancel.py`
- `cloud_dog_llm/runtime/cancellation.py`
- `cloud_dog_llm/runtime/client.py`
- `cloud_dog_llm/runtime/params.py`
- `cloud_dog_llm/runtime/response.py`
- `cloud_dog_llm/runtime/retries.py`
- `cloud_dog_llm/runtime/retry.py`
- `cloud_dog_llm/runtime/session.py`
- `cloud_dog_llm/runtime/streaming.py`
- `cloud_dog_llm/runtime/timeout.py`
- `cloud_dog_llm/runtime/timeouts.py`
- `cloud_dog_llm/security/__init__.py`
- `cloud_dog_llm/security/governance.py`
- `cloud_dog_llm/security/policies.py`
- `cloud_dog_llm/security/rbac.py`
- `cloud_dog_llm/security/redaction.py`
- `cloud_dog_llm/security/secrets.py`
- `cloud_dog_llm/security/tools_policy.py`
- `cloud_dog_llm/structured/__init__.py`
- `cloud_dog_llm/structured/extractor.py`
- `cloud_dog_llm/structured/parser.py`
- `cloud_dog_llm/structured/reducer.py`
- `cloud_dog_llm/structured/repair.py`
- `cloud_dog_llm/structured/schema.py`
- `cloud_dog_llm/structured/validator.py`
- `cloud_dog_llm/testing/__init__.py`
- `cloud_dog_llm/testing/conformance.py`
- `cloud_dog_llm/testing/fixtures.py`
- `cloud_dog_llm/testing/mock_providers.py`
- `cloud_dog_llm/testing/vcr.py`
- `cloud_dog_llm/tools/__init__.py`
- `cloud_dog_llm/tools/calling.py`
- `cloud_dog_llm/tools/executor.py`
- `cloud_dog_llm/tools/local.py`
- `cloud_dog_llm/tools/models.py`
- `cloud_dog_llm/tools/parser.py`
- `cloud_dog_llm/tools/pipeline.py`
- `cloud_dog_llm/tools/reducer.py`
- `cloud_dog_llm/tools/router.py`
- `cloud_dog_llm/tools/schema.py`
- `cloud_dog_llm/tools/schemas.py`
- `cloud_dog_llm/traceability_ids.py`
<!-- TRACEABILITY-MODULE-LIST:END -->
