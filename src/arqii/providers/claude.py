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

# Thinking budgets keyed by effort level. xhigh = the eval default; spends real
# money but produces meaningfully better porticos on hard inputs.
THINKING_EFFORT: dict[str, int] = {
    "low": 2048,
    "medium": 4096,
    "high": 8192,
    "xhigh": 32000,
}


class ClaudeProvider(LLMProvider):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        thinking_budget: int | None = None,
    ) -> None:
        self.client = Anthropic(api_key=api_key)
        self.max_tokens = max_tokens
        self.thinking_budget = thinking_budget

    def generate(self, prompt: str, *, model: str = DEFAULT_MODEL) -> str:
        kwargs: dict = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.thinking_budget is not None:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": self.thinking_budget}
            kwargs["max_tokens"] = self.thinking_budget + self.max_tokens
        else:
            kwargs["max_tokens"] = self.max_tokens

        try:
            if self.thinking_budget is not None:
                # Large thinking budgets exceed the SDK's 10-min non-streaming cap.
                with self.client.messages.stream(**kwargs) as stream:
                    msg = stream.get_final_message()
            else:
                msg = self.client.messages.create(**kwargs)
        except (AuthenticationError, PermissionDeniedError) as e:
            raise ProviderAuthError(str(e)) from e
        except (APIConnectionError, APITimeoutError, RateLimitError) as e:
            raise ProviderTransportError(str(e)) from e

        for block in msg.content:
            if block.type == "text":
                return block.text
        raise ProviderTransportError("Claude returned no text content block")
