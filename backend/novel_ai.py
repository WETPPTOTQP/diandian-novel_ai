from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .ai_providers import BaseLLMProvider, OllamaProvider, OpenAICompatProvider
from .config import Config, load_config
from .prompts import PROMPT_TEMPLATES


@dataclass(frozen=True)
class AIRequest:
    mode: str
    context: dict
    stream: bool = True
    provider: str | None = None
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None


class NovelAIService:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._providers: dict[str, BaseLLMProvider] = {
            "ollama": OllamaProvider(base_url=config.ollama_base_url, model=config.ollama_model),
        }
        # Always initialize OpenAI provider if possible, or create a dummy one if needed
        # But for now, we'll just keep the logic as is. 
        # Ideally, we should have a provider factory or a generic provider.
        if config.openai_compat_api_key or config.openai_compat_base_url: 
             # Allow init even if some fields are missing, they might be provided in request
             self._providers["openai_compat"] = OpenAICompatProvider(
                api_key=config.openai_compat_api_key or "",
                base_url=config.openai_compat_base_url or "https://api.openai.com",
                model=config.openai_compat_model or "gpt-3.5-turbo",
            )
        elif "openai_compat" not in self._providers:
             # Add a default one for dynamic usage
             self._providers["openai_compat"] = OpenAICompatProvider(
                api_key="",
                base_url="https://api.openai.com",
                model="gpt-3.5-turbo"
             )

    def _select_provider(self, request: AIRequest) -> BaseLLMProvider:
        provider_key = request.provider or self._config.default_provider
        provider = self._providers.get(provider_key)
        if provider is None:
            # If requesting openai_compat but it wasn't configured in env, we might need it now
            if provider_key == "openai_compat":
                 # It should have been added in __init__ now
                 pass
            provider = self._providers.get("ollama") # Fallback
        return provider

    def stream(self, request: AIRequest) -> Iterable[str]:
        template = PROMPT_TEMPLATES.get(request.mode)
        if not template:
            return iter([f"不支持的模式：{request.mode}"])

        system_prompt = template.get("system")
        user_template = template.get("user", "{target_text}")
        ctx = request.context or {}

        keywords = ctx.get("keywords")
        if isinstance(keywords, list):
            keywords_str = "、".join(str(k) for k in keywords)
        else:
            keywords_str = str(keywords) if keywords is not None else ""

        prompt = user_template.format(
            previous_text=str(ctx.get("previous_text", "")),
            target_text=str(ctx.get("target_text", "")),
            style=str(ctx.get("style", "normal")),
            keywords=keywords_str,
            novel_title=str(ctx.get("novel_title", "")),
            novel_summary=str(ctx.get("novel_summary", "")),
            character_summary=str(ctx.get("character_summary", "")),
        )
        provider = self._select_provider(request)
        
        # Pass request-specific overrides
        kwargs = {}
        if request.model:
            kwargs["model"] = request.model
        if request.api_key:
            kwargs["api_key"] = request.api_key
        if request.base_url:
            kwargs["base_url"] = request.base_url
            
        return provider.generate_stream(prompt=prompt, system_prompt=system_prompt, **kwargs)

    def get_ollama_models(self) -> list[str]:
        provider = self._providers.get("ollama")
        if isinstance(provider, OllamaProvider):
            return provider.list_models()
        return []

    def generate(self, request: AIRequest) -> str:
        return "".join(self.stream(request))


ai_service = NovelAIService(load_config())
