from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Generator, Iterable

import requests


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs,
    ) -> Iterable[str]:
        raise NotImplementedError

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        return "".join(self.generate_stream(prompt=prompt, system_prompt=system_prompt, **kwargs))


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str, model: str, timeout_seconds: int = 120) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    def list_models(self) -> list[str]:
        try:
            url = f"{self._base_url}/api/tags"
            with requests.get(url, timeout=5) as response:
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    return [m["name"] for m in models]
        except Exception as e:
            print(f"Failed to list Ollama models: {e}")
        return []

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs,
    ) -> Generator[str, None, None]:
        url = f"{self._base_url}/api/generate"
        
        # Allow model override
        model = kwargs.get("model") or self._model

        payload: dict[str, object] = {
            "model": model,
            "prompt": prompt,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt
        options = kwargs.get("options")
        if isinstance(options, dict):
            payload["options"] = options

        with requests.post(url, json=payload, stream=True, timeout=self._timeout_seconds) as response:
            response.raise_for_status()
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                try:
                    data = json.loads(raw_line)
                except json.JSONDecodeError:
                    continue
                if data.get("done") is True:
                    break
                chunk = data.get("response")
                if isinstance(chunk, str) and chunk:
                    yield chunk


class OpenAICompatProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: int = 120,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs,
    ) -> Generator[str, None, None]:
        # Allow overrides from kwargs
        api_key = kwargs.get("api_key") or self._api_key
        base_url = kwargs.get("base_url")
        if base_url:
             base_url = base_url.rstrip("/")
        else:
             base_url = self._base_url
        
        model = kwargs.get("model") or self._model

        url = f"{base_url}/v1/chat/completions"
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, object] = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        temperature = kwargs.get("temperature")
        if isinstance(temperature, (int, float)):
            payload["temperature"] = float(temperature)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        with requests.post(url, headers=headers, json=payload, stream=True, timeout=self._timeout_seconds) as response:
            response.raise_for_status()
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = raw_line.strip()
                if not line.startswith("data:"):
                    continue
                data_part = line[5:].strip()
                if data_part == "[DONE]":
                    break
                try:
                    data = json.loads(data_part)
                except json.JSONDecodeError:
                    continue
                choices = data.get("choices")
                if not isinstance(choices, list) or not choices:
                    continue
                delta = choices[0].get("delta") if isinstance(choices[0], dict) else None
                if not isinstance(delta, dict):
                    continue
                content = delta.get("content")
                if isinstance(content, str) and content:
                    yield content

