from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Chapter, Character, Novel


def build_context_for_novel(db: Session, novel_id: int, max_chars: int = 6000) -> dict[str, str]:
    novel = db.scalar(select(Novel).where(Novel.id == novel_id))
    if not novel:
        return {}
    chapters = db.scalars(
        select(Chapter).where(Chapter.novel_id == novel_id).order_by(Chapter.order_index.asc())
    ).all()
    text = "\n\n".join((c.content or "") for c in chapters)
    if len(text) > max_chars:
        text = text[-max_chars:]
    characters = db.scalars(select(Character).where(Character.novel_id == novel_id)).all()
    character_summary = "\n".join(f"{c.name}：{(c.profile or '').strip()}" for c in characters if c.name)
    return {
        "novel_title": novel.title,
        "novel_summary": (novel.summary or "").strip(),
        "previous_text": text,
        "character_summary": character_summary,
    }
