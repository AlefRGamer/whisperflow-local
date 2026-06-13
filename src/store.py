"""Histórico de transcrições, persistido em JSON."""
import json
import os
import time
import uuid

from paths import history_path


class History:
    def __init__(self, path: str | None = None):
        self.path = path or history_path()
        self._entries: list[dict] = self._load()

    def _load(self) -> list[dict]:
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._entries, f, ensure_ascii=False, indent=2)

    def all(self) -> list[dict]:
        """Mais recentes primeiro."""
        return list(reversed(self._entries))

    def add(self, text: str) -> dict:
        entry = {
            "id": uuid.uuid4().hex,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "text": text,
        }
        self._entries.append(entry)
        self._save()
        return entry

    def update(self, entry_id: str, text: str) -> None:
        for e in self._entries:
            if e["id"] == entry_id:
                e["text"] = text
                self._save()
                return

    def delete(self, entry_id: str) -> None:
        self._entries = [e for e in self._entries if e["id"] != entry_id]
        self._save()
