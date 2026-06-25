# cloud_dog_llm Architecture

## Purpose
`cloud_dog_llm` provides shared LLM client abstractions, provider adapters, tool routing, prompt handling, and streaming support for Cloud-Dog Python services.

## Main responsibilities
- wrap multiple LLM providers behind a common interface
- support chat, completion, embedding, and streaming workflows
- route tool calls to local, MCP, or A2A backends
- standardise request and response models for consumer services

## Main components
- provider adapters and factories
- domain request and response models
- prompt and templating helpers
- MCP and A2A client integrations
- tool routing and response normalisation helpers
