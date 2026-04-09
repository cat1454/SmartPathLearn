from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


DEFAULT_STORAGE_PATH = Path(__file__).resolve().parents[1] / ".handoff_api_store.json"


class RecordAlreadyExistsError(RuntimeError):
    pass


class JsonStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_STORAGE_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        if not self.path.exists():
            self._write_unlocked(self._empty_db())

    @staticmethod
    def _empty_db() -> dict[str, Any]:
        return {
            "source_packs": {},
            "activities": {},
            "submissions": {},
            "feedbacks": {},
        }

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _read_unlocked(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write_unlocked(self, data: dict[str, Any]) -> None:
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        temp_path.replace(self.path)

    def has_source_pack(self, source_pack_id: str) -> bool:
        with self._lock:
            data = self._read_unlocked()
            return source_pack_id in data["source_packs"]

    def get_source_pack(self, source_pack_id: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._read_unlocked()
            return data["source_packs"].get(source_pack_id)

    def create_source_pack(self, source_pack_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            data = self._read_unlocked()
            if source_pack_id in data["source_packs"]:
                raise RecordAlreadyExistsError(f"Source pack already exists: {source_pack_id}")
            timestamp = self._timestamp()
            record = {
                "id": source_pack_id,
                "created_at": timestamp,
                "updated_at": timestamp,
                "payload": payload,
            }
            data["source_packs"][source_pack_id] = record
            self._write_unlocked(data)
            return record

    def has_activity(self, activity_id: str) -> bool:
        with self._lock:
            data = self._read_unlocked()
            return activity_id in data["activities"]

    def get_activity(self, activity_id: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._read_unlocked()
            return data["activities"].get(activity_id)

    def create_activity(self, activity_id: str, source_pack_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            data = self._read_unlocked()
            if activity_id in data["activities"]:
                raise RecordAlreadyExistsError(f"Activity already exists: {activity_id}")
            timestamp = self._timestamp()
            record = {
                "id": activity_id,
                "created_at": timestamp,
                "updated_at": timestamp,
                "source_pack_id": source_pack_id,
                "payload": payload,
            }
            data["activities"][activity_id] = record
            self._write_unlocked(data)
            return record

    def get_submission(self, activity_id: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._read_unlocked()
            return data["submissions"].get(activity_id)

    def upsert_submission(self, activity_id: str, submission: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            data = self._read_unlocked()
            existing = data["submissions"].get(activity_id)
            timestamp = self._timestamp()
            created_at = existing["created_at"] if existing else timestamp
            record = {
                "activity_id": activity_id,
                "created_at": created_at,
                "updated_at": timestamp,
                "submission": submission,
            }
            data["submissions"][activity_id] = record
            self._write_unlocked(data)
            return record

    def get_feedback(self, activity_id: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._read_unlocked()
            return data["feedbacks"].get(activity_id)

    def upsert_feedback(self, activity_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            data = self._read_unlocked()
            existing = data["feedbacks"].get(activity_id)
            timestamp = self._timestamp()
            created_at = existing["created_at"] if existing else timestamp
            record = {
                "id": f"fb_{activity_id}",
                "activity_id": activity_id,
                "created_at": created_at,
                "updated_at": timestamp,
                "payload": payload,
            }
            data["feedbacks"][activity_id] = record
            self._write_unlocked(data)
            return record
