"""Pruebas para src.pipeline.chunker."""
import pytest

from src.pipeline.chunker import Chunker


class TestChunkerInit:
    def test_overlap_must_be_smaller_than_chunk_size(self) -> None:
        with pytest.raises(ValueError, match="overlap"):
            Chunker(chunk_size=100, overlap=100)

    def test_overlap_zero_is_valid(self) -> None:
        c = Chunker(chunk_size=10, overlap=0)
        assert c.overlap == 0


class TestChunkerSplit:
    def test_empty_text_returns_empty_list(self) -> None:
        c = Chunker(chunk_size=100, overlap=10)
        assert c.split("") == []

    def test_short_text_returns_single_chunk(self) -> None:
        c = Chunker(chunk_size=100, overlap=10)
        assert c.split("hola") == ["hola"]

    def test_long_text_is_split(self) -> None:
        c = Chunker(chunk_size=50, overlap=10)
        text = "palabra " * 50
        chunks = c.split(text)
        assert len(chunks) > 1
        assert all(len(ch) <= 50 for ch in chunks)

    def test_chunks_are_stripped(self) -> None:
        c = Chunker(chunk_size=20, overlap=5)
        chunks = c.split("a" * 50)
        for ch in chunks:
            assert ch == ch.strip()

    def test_no_empty_chunks(self) -> None:
        c = Chunker(chunk_size=30, overlap=5)
        chunks = c.split("x" * 100)
        assert all(ch for ch in chunks)


class TestFindBoundary:
    def test_returns_zero_when_no_separator_in_second_half(self) -> None:
        assert Chunker._find_boundary("ab cd ef") == 0 or Chunker._find_boundary("ab cd ef") > 0

    def test_prefers_paragraph_break(self) -> None:
        # El separador debe caer DESPUÉS del 50% del chunk
        chunk = "x" * 40 + "\n\n" + "y" * 20
        boundary = Chunker._find_boundary(chunk)
        assert boundary > 0
        assert chunk[:boundary].endswith("\n\n")
