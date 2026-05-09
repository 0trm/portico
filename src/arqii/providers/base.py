from abc import ABC, abstractmethod


class ProviderError(Exception):
    """Base for provider-side failures (network, auth, quota)."""


class ProviderAuthError(ProviderError):
    """Auth or quota -- do not retry."""


class ProviderTransportError(ProviderError):
    """Network / timeout -- retryable at the analyzer's discretion."""


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, *, model: str) -> str:
        """Send the prompt, return the model's text response."""
