from portico.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    def generate(self, prompt: str, *, model: str) -> str:
        raise NotImplementedError("gemini provider deferred post-v0.1.0")
