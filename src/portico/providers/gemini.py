from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from portico.providers.base import (
    LLMProvider,
    ProviderAuthError,
    ProviderTransportError,
)

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_MAX_TOKENS = 4096


class GeminiProvider(LLMProvider):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> None:
        # api_key=None lets the SDK read GOOGLE_API_KEY / GEMINI_API_KEY from env,
        # mirroring the OpenAIProvider pattern.
        self.client = genai.Client(api_key=api_key)
        self.max_tokens = max_tokens

    def generate(self, prompt: str, *, model: str = DEFAULT_MODEL) -> str:
        config = genai_types.GenerateContentConfig(max_output_tokens=self.max_tokens)
        try:
            resp = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
        except genai_errors.ClientError as e:
            if e.code in (401, 403):
                raise ProviderAuthError(str(e)) from e
            raise ProviderTransportError(str(e)) from e
        except genai_errors.ServerError as e:
            raise ProviderTransportError(str(e)) from e
        except genai_errors.APIError as e:
            raise ProviderTransportError(str(e)) from e

        text = resp.text
        if not text:
            raise ProviderTransportError("Gemini returned empty content")
        return text
