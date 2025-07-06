from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class OrderSessionStore:
    _store: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def start_session(self, line_id: str):
        self._store[line_id] = {"step": "waiting_recipient"}

    def get_session(self, line_id: str) -> Optional[Dict]:
        return self._store.get(line_id)

    def set_field(self, line_id: str, key: str, value: Any):
        if line_id in self._store:
            self._store[line_id][key] = value

    def clear_session(self, line_id: str):
        self._store.pop(line_id, None)

    def is_active(self, line_id: str) -> bool:
        return line_id in self._store
