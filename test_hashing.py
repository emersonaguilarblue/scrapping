"""Pruebas para src.pipeline.hashing."""
from src.pipeline.hashing import compute_hash


class TestComputeHash:
    def test_is_deterministic(self) -> None:
        assert compute_hash("abc") == compute_hash("abc")

    def test_differs_for_different_inputs(self) -> None:
        assert compute_hash("abc") != compute_hash("abd")

    def test_returns_hex_string_64_chars(self) -> None:
        # SHA-256 = 64 caracteres hex
        h = compute_hash("anything")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_handles_empty_string(self) -> None:
        # SHA-256 del string vacío conocido
        assert compute_hash("") == (
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

    def test_handles_unicode(self) -> None:
        h = compute_hash("héllo ñ 日本")
        assert len(h) == 64
