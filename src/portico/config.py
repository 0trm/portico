import os


def get_anthropic_api_key() -> str | None:
    return os.environ.get("ANTHROPIC_API_KEY")


def get_default_provider() -> str:
    return os.environ.get("PORTICO_PROVIDER", "claude")


def get_default_model() -> str | None:
    return os.environ.get("PORTICO_MODEL")
