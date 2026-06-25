# cloud_dog_llm Configuration

## Typical inputs
Consumer services typically configure:
- provider identifier
- model name
- base URL
- API key
- timeout and retry limits
- prompt template locations
- extra headers for provider-specific integrations

## Guidance
- keep API keys and registry credentials in Vault-backed configuration
- avoid package-level service host defaults in source code
- make provider-specific headers overrideable through configuration
