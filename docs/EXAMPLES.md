# cloud_dog_llm Examples

## Create a client and send a request
```python
from cloud_dog_llm import get_llm_client
from cloud_dog_llm.domain.models import LLMRequest, Message

client = get_llm_client(config)
response = await client.chat(LLMRequest(messages=[Message(role="user", content="Hello")]))
```
