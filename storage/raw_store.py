from datetime import datetime
from pathlib import Path

from loguru import logger
from slugify import slugify

from src.config.constants import HTML_CONTENT_TYPES, PDF_CONTENT_TYPES
from src.core.exceptions import StorageError
from src.core.models import RawPayload


class RawFileStore:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(self, payload: RawPayload) -> Path:
        ext = self._extension_for(payload.content_type)
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        name = f"{slugify(payload.source_id)}_{ts}{ext}"
        path = self.output_dir / name
        try:
            path.write_bytes(payload.body)
            logger.debug(f"raw -> {path.name}")
            return path
        except OSError as exc:
            raise StorageError(f"Cannot write {path}: {exc}") from exc

    @staticmethod
    def _extension_for(content_type: str) -> str:
        ct = content_type.split(";")[0].strip().lower()
        if ct in PDF_CONTENT_TYPES:
            return ".pdf"
        if ct in HTML_CONTENT_TYPES:
            return ".html"
        return ".bin"
