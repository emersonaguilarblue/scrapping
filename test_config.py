"""Pruebas para src.config.settings y src.config.constants."""
from pathlib import Path

from src.config.constants import (
    CONTENT_SELECTORS,
    DEFAULT_HEADERS,
    HTML_CONTENT_TYPES,
    PDF_CONTENT_TYPES,
    REMOVABLE_SELECTORS,
)
from src.config.settings import Settings


class TestConstants:
    def test_default_headers_has_user_agent_friendly_keys(self) -> None:
        assert "Accept" in DEFAULT_HEADERS
        assert "Accept-Language" in DEFAULT_HEADERS

    def test_content_selectors_are_tuple(self) -> None:
        assert isinstance(CONTENT_SELECTORS, tuple)
        assert "main" in CONTENT_SELECTORS

    def test_removable_selectors_includes_script(self) -> None:
        assert "script" in REMOVABLE_SELECTORS

    def test_pdf_content_types(self) -> None:
        assert "application/pdf" in PDF_CONTENT_TYPES

    def test_html_content_types(self) -> None:
        assert "text/html" in HTML_CONTENT_TYPES


class TestSettings:
    def test_defaults_are_sensible(self) -> None:
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.max_concurrency >= 1
        assert s.chunk_size > s.chunk_overlap
        assert s.timeout_ms > 0

    def test_ensure_dirs_creates_directories(self, tmp_path: Path) -> None:
        s = Settings(
            raw_dir=tmp_path / "r",
            processed_dir=tmp_path / "p",
            cache_dir=tmp_path / "c",
        )
        s.ensure_dirs()
        assert (tmp_path / "r").is_dir()
        assert (tmp_path / "p").is_dir()
        assert (tmp_path / "c").is_dir()
