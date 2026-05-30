from __future__ import annotations

from abc import ABC, abstractmethod


class ModelAdapter(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Send prompt and return the model's response text."""
        ...


class OpenAIAdapter(ModelAdapter):
    def __init__(self, model: str, api_key: str | None = None) -> None:
        import openai

        self.model = model
        self._client = openai.OpenAI(api_key=api_key)

    def complete(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content or ""


class AnthropicAdapter(ModelAdapter):
    def __init__(self, model: str, api_key: str | None = None) -> None:
        import anthropic

        self.model = model
        self._client = anthropic.Anthropic(api_key=api_key)

    def complete(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text if message.content else ""


def get_adapter(model: str) -> ModelAdapter:
    """Return the appropriate adapter based on model name prefix."""
    lower = model.lower()
    if lower.startswith(("gpt-", "o1-", "o3-")):
        return OpenAIAdapter(model)
    if lower.startswith("claude-"):
        return AnthropicAdapter(model)
    raise ValueError(
        f"Unknown model prefix for '{model}'. "
        "Expected 'gpt-*', 'o1-*', 'o3-*' (OpenAI) or 'claude-*' (Anthropic)."
    )
