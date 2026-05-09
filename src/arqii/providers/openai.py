from arqii.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def generate(self, prompt: str, *, model: str) -> str:
        raise NotImplementedError("openai provider deferred post-v0.1.0")
