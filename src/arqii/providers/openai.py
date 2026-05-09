from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)

from arqii.providers.base import (
    LLMProvider,
    ProviderAuthError,
    ProviderTransportError,
)

DEFAULT_MODEL = "gpt-4o"
DEFAULT_MAX_TOKENS = 4096


class OpenAIProvider(LLMProvider):
    def __init__(self, *, api_key: str | None = None, max_tokens: int = DEFAULT_MAX_TOKENS) -> None:
        self.client = OpenAI(api_key=api_key)
        self.max_tokens = max_tokens

    def generate(self, prompt: str, *, model: str = DEFAULT_MODEL) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
        except (AuthenticationError, PermissionDeniedError) as e:
            raise ProviderAuthError(str(e)) from e
        except (APIConnectionError, APITimeoutError, RateLimitError) as e:
            raise ProviderTransportError(str(e)) from e

        text = resp.choices[0].message.content
        if not text:
            raise ProviderTransportError("OpenAI returned empty content")
        return text
