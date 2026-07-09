"""
Management of Competition Scoring Records
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ScoreManager:
    """Responsible for saving and reading competition scoring records"""

    def __init__(self, path: Optional[str] = None):
        self.path = Path(path or "scores.json")
        self.scores: List[Dict] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self.scores = data
            except json.JSONDecodeError:
                self.scores = []

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.scores, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_record(self, record: Dict) -> None:
        record.setdefault("timestamp", datetime.utcnow().isoformat(timespec="seconds"))
        self.scores.append(record)
        self._save()

    def get_scores(self) -> List[Dict]:
        return sorted(self.scores, key=lambda item: item.get("timestamp", ""), reverse=True)

    def clear(self) -> None:
        self.scores = []
        if self.path.exists():
            self.path.unlink()

