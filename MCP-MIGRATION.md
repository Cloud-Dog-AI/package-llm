# cloud_dog_llm — MCP Transport Migration Matrix

This matrix maps legacy and current MCP transport modes to `cloud_dog_llm` adapters.

| Legacy / external transport | `cloud_dog_llm` transport module | Notes |
|---|---|---|
| stdio | `cloud_dog_llm/mcp/transports/stdio.py` | Best for local sidecar MCP servers and CLI-hosted tools. |
| SSE (legacy) | `cloud_dog_llm/mcp/transports/legacy_sse.py` | Maintained for backward compatibility with event-stream MCP servers. |
| Streamable HTTP | `cloud_dog_llm/mcp/transports/streamable_http.py` | Preferred for modern HTTP MCP deployments supporting server push and async jobs. |
| HTTP JSON-RPC | `cloud_dog_llm/mcp/transports/http_jsonrpc.py` | Preferred for request/response style MCP service integration. |

## Mixed Deployment Notes

- Mixed transport fleets are supported by selecting a transport per MCP endpoint at client construction.
- For phased migrations, keep legacy SSE endpoints on `legacy_sse.py` while new endpoints move to `streamable_http.py`.
- `stdio` and HTTP transports can coexist in one process if each server is isolated by session/channel.
- Prefer streamable HTTP for long-running tool calls where polling and incremental updates are needed.
