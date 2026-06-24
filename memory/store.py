import os
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime


MEMORY_PARENT_PATH = Path("memory/conversations/")
KST = ZoneInfo("Asia/Seoul")

def get_memory_path() -> Path:
    MEMORY_PARENT_PATH.mkdir(parents=True, exist_ok=True)
    today = datetime.now(KST).strftime("%Y-%m-%d")
    return MEMORY_PARENT_PATH / f"conversation.{today}.json"


def _now() -> str:
    return datetime.now().isoformat()


def load_memory() -> dict:
    memory_path = get_memory_path()
    if not memory_path.exists():
        return {"messages": [], "last_calendar_event": None}

    with open(memory_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

def save_memory(memory: dict) -> None:
    memory_path = get_memory_path()

    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def append_memory(role: str, content: str) -> None:
    memory = load_memory()

    memory.setdefault("messages", []).append(
        {
            "role": role,
            "content": content,
            "created_at": _now()
        }
    )

    save_memory(memory)


def update_last_calendar_event(event: dict) -> None:
    memory = load_memory()

    memory["last_calendar_event"] = {
        "event_id": event['id'],
        "title": event.get("summary"),
        "start_time": event.get("start", {}).get("dateTime", None),
        "end_time": event.get("end", {}).get("dateTime", None),
        "location": event.get("location", None),
        "html_link": event.get('htmlLink'),
        "updated_at": _now()
    }

    save_memory(memory)


def get_recent_memory(limit: int = 5) -> dict:
    memory = load_memory()

    return {
        "messages": memory.get("messages", [])[-limit:],
        "last_calendar_event": memory.get("last_calendar_event")
    }

