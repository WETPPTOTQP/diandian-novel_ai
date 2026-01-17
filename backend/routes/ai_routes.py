from __future__ import annotations

import json
from typing import Iterable

from flask import Blueprint, Response, jsonify, request

from ..novel_ai import AIRequest, ai_service
from ..utils.rate_limiter import InMemoryFixedWindowLimiter


from ..context_builder import build_context_for_novel
from ..database import SessionLocal

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")
limiter = InMemoryFixedWindowLimiter(limit=60, window_seconds=60)


def _sse_stream(chunks: Iterable[str]) -> Iterable[str]:
    try:
        for chunk in chunks:
            data = json.dumps({"content": chunk}, ensure_ascii=False)
            yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        err = json.dumps({"error": str(e)}, ensure_ascii=False)
        yield f"data: {err}\n\n"


@ai_bp.get("/models")
def list_models():
    """获取本地 Ollama 模型列表"""
    try:
        models = ai_service.get_ollama_models()
        return jsonify({"code": "OK", "data": models})
    except Exception as e:
        return jsonify({"code": "ERROR", "message": str(e)}), 500


@ai_bp.post("/generate")
def generate():
    data = request.get_json(silent=True) or {}
    key = request.remote_addr or "anonymous"
    result = limiter.check(key)
    if not result.allowed:
        return (
            jsonify(
                {
                    "code": "RATE_LIMITED",
                    "message": "请求过于频繁",
                    "data": {"reset_in_seconds": result.reset_in_seconds},
                }
            ),
            429,
        )

    mode = str(data.get("mode", "continue"))
    context = data.get("context") if isinstance(data.get("context"), dict) else {}
    stream = bool(data.get("stream", True))
    provider = data.get("provider")
    model = data.get("model")
    api_key = data.get("api_key")
    base_url = data.get("base_url")
    novel_id = data.get("novel_id")

    # 如果提供了 novel_id，自动构建上下文
    if novel_id:
        try:
            with SessionLocal() as db:
                novel_context = build_context_for_novel(db, int(novel_id))
                # 合并上下文，前端传来的优先级更高（如果有）
                for k, v in novel_context.items():
                    if k not in context:
                        context[k] = v
        except Exception as e:
            print(f"Error building context: {e}")

    req = AIRequest(
        mode=mode, 
        context=context, 
        stream=stream, 
        provider=provider, 
        model=model,
        api_key=api_key,
        base_url=base_url
    )
    if stream:
        return Response(_sse_stream(ai_service.stream(req)), mimetype="text/event-stream")

    content = ai_service.generate(req)
    return jsonify({"code": "OK", "data": {"content": content}})


@ai_bp.post("/brainstorm")
def brainstorm():
    data = request.get_json(silent=True) or {}
    brainstorm_type = str(data.get("type", "outline"))
    keywords = data.get("keywords")
    provider = data.get("provider")
    model = data.get("model")
    api_key = data.get("api_key")
    base_url = data.get("base_url")

    if not isinstance(keywords, list):
        keywords = []
    
    req = AIRequest(
        mode=brainstorm_type, 
        context={"keywords": keywords}, 
        stream=False,
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url
    )
    content = ai_service.generate(req)
    return jsonify({"code": "OK", "data": {"content": content}})
