"""Prompt manager — loads templates from the prompts/ directory."""

from pathlib import Path
from typing import Any

_PROMPT_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"
_cache: dict[str, str] = {}


def _load_prompt(name: str) -> str:
    if name not in _cache:
        path = _PROMPT_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")
        _cache[name] = path.read_text(encoding="utf-8")
    return _cache[name]


def get_system_prompt() -> str:
    return _load_prompt("system_prompt.txt")


def get_emotion_prompt(**kwargs: Any) -> str:
    template = _load_prompt("emotion_prompt.txt")
    return template.format(**kwargs)


def get_knowledge_prompt(**kwargs: Any) -> str:
    template = _load_prompt("knowledge_prompt.txt")
    return template.format(**kwargs)


def get_mentor_prompt(**kwargs: Any) -> str:
    template = _load_prompt("mentor_prompt.txt")
    return template.format(**kwargs)


def get_summary_prompt(**kwargs: Any) -> str:
    template = _load_prompt("summary_prompt.txt")
    return template.format(**kwargs)


def get_classify_prompt(**kwargs: Any) -> str:
    template = _load_prompt("classify_prompt.txt")
    return template.format(**kwargs)
