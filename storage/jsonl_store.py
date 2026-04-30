import json
from pathlib import Path
from threading import Lock

from loguru import logger

from src.core.exceptions import StorageError
from src.core.models import ScrapedDocument


class JsonlDocumentStore:
    def __init__(self, output_dir: Path, filename: str = "documents.jsonl") -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.output_dir / filename
        self._lock = Lock()

    def save(self, document: ScrapedDocument) -> None:
        try:
            line = document.model_dump_json()
            with self._lock, self.path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
            logger.debug(f"saved -> {self.path.name} ({document.source_id})")
        except OSError as exc:
            raise StorageError(f"Cannot write {self.path}: {exc}") from exc

    def load_all(self) -> list[ScrapedDocument]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            return [ScrapedDocument(**json.loads(ln)) for ln in f if ln.strip()]

    def reset(self) -> None:
        if self.path.exists():
            self.path.unlink()
