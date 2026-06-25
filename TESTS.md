# platform-llm — TESTS.md

**Package:** `cloud_dog_llm`  
**Version:** 0.2.0 (pre-release)  
**Standard:** PS-50, PS-95  
**Status:** Draft

---

## Test Strategy

### Overview

Tests organised per PS-95 hierarchy:

- **UT** — Unit tests for individual components (adapters, tool router, MCP client, streaming, prompts, embeddings)
- **ST** — System tests for end-to-end flows with mock providers
- **IT** — Integration tests with real LLM providers and MCP servers (env-gated)
- **AT** — Application tests simulating real service patterns
- **QT** — Security tests for redaction, governance, tool policies

### Test Principles

- `--env` mandatory for all test runs.
- Zero hardcoded values.
- UT tests use mock HTTP responses and mock providers.
- IT tests require real LLM provider (Ollama at minimum) — env-gated.
- Preflight LLM availability before LLM-dependent tests.
- Stop on failure.

---

## Test Directory Structure

```
tests/
  conftest.py
  env-UT
  env-ST
  env-IT
  env-AT
  unit/
    UT1.1_OllamaAdapter/
      test_ollama.py
    UT1.2_OpenAICompatAdapter/
      test_openai_compat.py
    UT1.3_OpenRouterAdapter/
      test_openrouter.py
    UT1.4_ProviderRegistry/
      test_provider_registry.py
    UT1.5_ModelRegistry/
      test_model_registry.py
    UT1.6_StreamingEngine/
      test_streaming.py
    UT1.7_StreamingSerialization/
      test_sse_jsonl.py
    UT1.8_ToolDefinitionModel/
      test_tool_def.py
    UT1.9_ToolCallingStyles/
      test_tool_calling.py
    UT1.10_JSONInTextParser/
      test_json_text_parser.py
    UT1.11_ToolExecutionPipeline/
      test_tool_pipeline.py
    UT1.12_MCPClientStreamableHTTP/
      test_mcp_streamable.py
    UT1.13_MCPClientHTTPJsonRPC/
      test_mcp_http.py
    UT1.14_MCPClientLegacySSE/
      test_mcp_sse.py
    UT1.15_MCPClientStdio/
      test_mcp_stdio.py
    UT1.16_MCPSessionManagement/
      test_mcp_session.py
    UT1.17_A2AClient/
      test_a2a_client.py
    UT1.18_ToolRouter/
      test_tool_router.py
    UT1.19_PromptRegistry/
      test_prompt_registry.py
    UT1.20_PromptRendering/
      test_prompt_render.py
    UT1.21_EmbeddingManager/
      test_embeddings.py
    UT1.22_ArtefactStore/
      test_artefact_store.py
    UT1.23_StructuredExtractor/
      test_structured.py
    UT1.24_RepairLoop/
      test_repair_loop.py
    UT1.25_ErrorTaxonomy/
      test_errors.py
    UT1.26_RetryPolicy/
      test_retries.py
    UT1.27_TimeoutManagement/
      test_timeouts.py
    UT1.28_Cancellation/
      test_cancellation.py
    UT1.29_SessionContext/
      test_session_context.py
    UT1.30_UnifiedResponse/
      test_response_model.py
    UT1.31_ToolOutputReducer/
      test_output_reducer.py
    UT1.32_ParameterPassthrough/
      test_param_passthrough.py
    UT1.33_ResponseShapeCompatibilityAdapter/
      test_response_adapter.py
    UT1.34_ReliabilityMiddlewareHooks/
      test_reliability_hooks.py
    UT1.35_ProviderCapabilityMatrix/
      test_capability_matrix.py
    UT1.36_QueueAwareAvailabilityGating/
      test_availability_gating.py
    UT1.37_DomainFormatterCompatibility/
      test_formatter_compat.py
  system/
    ST1.1_ChatEndToEnd/
      test_chat_e2e.py
    ST1.2_StreamEndToEnd/
      test_stream_e2e.py
    ST1.3_ToolCallEndToEnd/
      test_tool_call_e2e.py
    ST1.4_MCPToolCallEndToEnd/
      test_mcp_tool_e2e.py
    ST1.5_PromptRenderToChat/
      test_prompt_to_chat.py
    ST1.6_MultiProviderSwitch/
      test_multi_provider.py
    ST1.7_ReliabilityMiddlewareEndToEnd/
      test_reliability_e2e.py
  integration/
    IT1.1_OllamaChat/
      test_ollama_chat.py
    IT1.2_OllamaStream/
      test_ollama_stream.py
    IT1.3_OllamaEmbeddings/
      test_ollama_embed.py
    IT1.4_OpenRouterChat/
      test_openrouter_chat.py
    IT1.5_MCPServerIntegration/
      test_mcp_server.py
    IT1.6_ToolCallingRealLLM/
      test_tool_calling_real.py
    IT1.7_MultiProviderBackend/
      test_multi_backend.py
  application/
    AT1.1_ServiceStartupPattern/
      test_service_startup.py
    AT1.2_ChatWithToolCalling/
      test_chat_tools.py
    AT1.3_MCPAllTransports/
      test_mcp_transports.py
    AT1.4_ConformanceSuite/
      test_conformance.py
    AT1.5_ResponseAdapterIntegration/
      test_response_adapter_integration.py
  security/
    QT1.1_SecretRedaction/
      test_secret_redaction.py
    QT1.2_GovernancePolicies/
      test_governance.py
    QT1.3_ToolAccessPolicies/
      test_tool_policies.py
```

---

## Coverage Map (Requirements → Tests)

### Functional Requirements
- **FR1.1** → UT1.4 (provider adapter interface)
- **FR1.2** → UT1.2 (OpenAI-compat adapter)
- **FR1.3** → UT1.1 (Ollama adapter), IT1.1, IT1.2
- **FR1.4** → UT1.3 (OpenRouter adapter), IT1.4
- **FR1.5** → UT1.4 (custom adapter registration)
- **FR1.6** → UT1.5 (model registry)
- **FR1.7** → ST1.1 (chat interface), IT1.1
- **FR1.8** → ST1.1 (completions)
- **FR1.9** → UT1.21 (embeddings), IT1.3
- **FR1.10** → UT1.6, UT1.7 (streaming), ST1.2
- **FR1.11** → UT1.23, UT1.24 (structured outputs + repair)
- **FR1.12** → UT1.8 (tool definition model)
- **FR1.13** → UT1.9, UT1.10 (tool calling styles + JSON-in-text)
- **FR1.14** → UT1.11 (tool execution pipeline), ST1.3
- **FR1.15** → UT1.12-UT1.16 (MCP client all transports + sessions), ST1.4, AT1.3
- **FR1.16** → UT1.17 (A2A client)
- **FR1.17** → UT1.18 (tool router), ST1.3
- **FR1.18** → UT1.19, UT1.20 (prompt registry + rendering), ST1.5
- **FR1.19** → UT1.22 (artefact store)
- **FR1.20** → UT1.32 (parameter passthrough)
- **FR1.21** → UT1.26 (retries), UT1.27 (timeouts)
- **FR1.22** → UT1.28 (cancellation)
- **FR1.23** → UT1.29 (session context)
- **FR1.24** → UT1.30 (unified response)
- **FR1.25** → UT1.25 (error taxonomy)
- **FR1.26** → QT1.1 (secret redaction)
- **FR1.27** → QT1.2 (governance), QT1.3 (tool policies)
- **FR1.28** → UT1.31 (tool output reducer)
- **FR1.29** → AT1.1 (config via platform-config)
- **FR1.30** → AT1.4 (conformance suite)

### Cyber Security
- **CS1.1** → QT1.1 (no secrets in logs)
- **CS1.2** → QT1.1 (API keys only in headers)
- **CS1.3** → QT1.1 (content redaction)
- **CS1.4** → QT1.3 (tool security context)

---

## Unit Tests (UT) — Selected Detail

### UT1.1: Ollama Adapter
- **Scope**: Ollama provider adapter
- **What is being tested**: Chat via /api/chat; fallback to /api/generate; thinking content extraction; health check; timeout handling; retry on 502/503/504
- **Related Requirements**: FR1.3
- **Related Architecture**: CC1.3

### UT1.12: MCP Client Streamable HTTP
- **Scope**: MCP client streamable HTTP transport
- **What is being tested**: JSON-RPC request/response; Mcp-Session-Id header tracking; initialize → tools/list → tools/call; session creation and termination; async job mode (wait=false → poll)
- **Related Requirements**: FR1.15

### UT1.18: Tool Router
- **Scope**: Unified tool routing (local + MCP + A2A)
- **What is being tested**: Local tool registration and execution; MCP tool routing; A2A tool routing; policy enforcement (allowed/denied tools per session); capability-aware routing; audit logging of all calls
- **Related Requirements**: FR1.17

### UT1.6: Streaming Engine
- **Scope**: Unified streaming event model
- **What is being tested**: Event sequence (started→delta→completed); SSE serialisation; JSONL serialisation; async iterator; backpressure (bounded buffer); client cancellation; error event on failure
- **Related Requirements**: FR1.10

---

## New Tests (v0.2.0 — FR1.32–FR1.37)

### UT1.33: Response-Shape Compatibility Adapter
- **Type**: UT
- **Scope**: Legacy response normalisation
- **What is being tested**: Ollama response normalised to LLMResponse; OpenRouter response normalised; OpenAI response normalised; Anthropic response normalised; unknown provider response raises error; configurable per-provider mappings; no data loss in normalisation
- **Related Requirements**: FR1.32
- **Related Architecture**: compat/response_adapter.py

### UT1.34: Reliability Middleware Hooks
- **Type**: UT
- **Scope**: Request pipeline middleware
- **What is being tested**: `pre_request` modifies request before provider call; `post_response` inspects/modifies response; `on_error` catches provider error and returns fallback; middleware chain executed in order; middleware can short-circuit; disabled middleware skipped
- **Related Requirements**: FR1.33
- **Related Architecture**: middleware/reliability.py

### UT1.35: Provider Capability Matrix
- **Type**: UT
- **Scope**: Runtime capability querying
- **What is being tested**: `get_capabilities(model_id)` returns CapabilityDescriptor; capabilities include streaming, tool_calling, structured_output, vision, embeddings, max_tokens, context_window; unknown model returns default capabilities; capabilities used by parameter validation
- **Related Requirements**: FR1.36
- **Related Architecture**: registry/capabilities.py

### UT1.36: Queue-Aware Availability Gating
- **Type**: UT
- **Scope**: Model availability based on queue depth
- **What is being tested**: `check_availability(model_id)` returns available when queue empty; returns degraded when queue at threshold; returns unavailable when queue full; configurable per-model thresholds; rate limit integration
- **Related Requirements**: FR1.35
- **Related Architecture**: availability/gating.py

### UT1.37: Domain Formatter Compatibility
- **Type**: UT
- **Scope**: Wrapping domain formatters as PromptTemplate
- **What is being tested**: Domain formatter wrapped as PromptTemplate; render produces same output; compatibility adapter preserves chain order; missing formatter raises error
- **Related Requirements**: FR1.37
- **Related Architecture**: compat/formatter_compat.py

### ST1.7: Reliability Middleware End-to-End
- **Type**: ST
- **Scope**: Full request pipeline with reliability middleware
- **What is being tested**: Request through middleware chain → provider → response through middleware; provider error triggers on_error middleware; fallback provider selected; rate limiter blocks when threshold reached
- **Related Requirements**: FR1.33

### AT1.5: Response Adapter Integration
- **Type**: AT
- **Scope**: Simulate multi-provider service with response adapter
- **What is being tested**: Service uses multiple providers; ResponseAdapter normalises all to LLMResponse; downstream code works uniformly regardless of provider; provider switch requires no downstream changes
- **Related Requirements**: FR1.32

---

## Test Run History

| Date (UTC) | Scope | Command | Status | Notes |
|------------|-------|---------|--------|-------|
| 2026-02-20 | Full matrix (UT env) | `.venv/bin/pytest tests/ --env tests/env-UT -v --tb=short` | PASS | `86 passed, 0 failed, 0 skipped` |
| 2026-02-18 | Full matrix (Vault-backed) | `pytest tests --env /opt/iac/Development/cloud-dog-ai/env-vault-admin --env tests/env-UT --env tests/env-ST --env tests/env-IT --env tests/env-AT -q` | PASS | `86 passed, 0 failed, 0 skipped` |
| 2026-02-18 | Full matrix | `pytest tests --env tests/env-UT --env tests/env-ST --env tests/env-IT --env tests/env-AT -q` | PASS | `79 passed, 0 failed, 7 skipped` |
| 2026-02-18 | Lint + format check | `ruff check cloud_dog_llm tests && ruff format --check cloud_dog_llm tests` | PASS | `All checks passed`, `176 files already formatted` |
| 2026-02-18 | Build artefacts | `python -m build` | PASS | `cloud_dog_llm-0.2.0.tar.gz` + `.whl` produced |

---

## Latest Verified Run

| Date (UTC) | Scope | Command | Status | Notes |
|------------|-------|---------|--------|-------|
| 2026-02-20 | Full matrix (UT env) | `.venv/bin/pytest tests/ --env tests/env-UT -v --tb=short` | PASS | `86 passed, 0 failed, 0 skipped` |
