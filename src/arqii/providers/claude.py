from anthropic import (
    Anthropic,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
)

from arqii.providers.base import (
    LLMProvider,
    ProviderAuthError,
    ProviderTransportError,
)

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 4096


class ClaudeProvider(LLMProvider):
    def __init__(self, *, api_key: str | None = None, max_tokens: int = DEFAULT_MAX_TOKENS) -> None:
        self.client = Anthropic(api_key=api_key)
        self.max_tokens = max_tokens

    def generate(self, prompt: str, *, model: str = DEFAULT_MODEL) -> str:
        try:
            msg = self.client.messages.create(
                model=model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
        except (AuthenticationError, PermissionDeniedError) as e:
            raise ProviderAuthError(str(e)) from e
        except (APIConnectionError, APITimeoutError, RateLimitError) as e:
            raise ProviderTransportError(str(e)) from e

        for block in msg.content:
            if block.type == "text":
                return block.text
        raise ProviderTransportError("Claude returned no text content block")
