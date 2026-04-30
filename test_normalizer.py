"""Pruebas para src.pipeline.normalizer."""
from src.pipeline.normalizer import normalize_text


class TestNormalizeText:
    def test_empty_string_returns_empty(self) -> None:
        assert normalize_text("") == ""

    def test_none_safe_for_falsy(self) -> None:
        assert normalize_text("") == ""

    def test_collapses_repeated_spaces(self) -> None:
        assert normalize_text("hola    mundo") == "hola mundo"

    def test_collapses_tabs_and_nbsp(self) -> None:
        assert normalize_text("hola\t\u00a0mundo") == "hola mundo"

    def test_strips_lines(self) -> None:
        assert normalize_text("  hola  \n  mundo  ") == "hola\nmundo"

    def test_drops_empty_lines(self) -> None:
        assert normalize_text("a\n\n\n\nb") == "a\nb"

    def test_collapses_more_than_two_newlines(self) -> None:
        # tras "join" sin líneas vacías se generan \n simples; añadimos contenido vacío forzado
        text = "a\n   \n   \nb"
        assert normalize_text(text) == "a\nb"

    def test_strips_non_printable_chars(self) -> None:
        assert normalize_text("a\x00b\x07c") == "abc"

    def test_nfkc_normalization(self) -> None:
        # ﬁ (ligadura U+FB01) debe convertirse a "fi"
        assert normalize_text("o\ufb01cina") == "oficina"

    def test_trims_outer_whitespace(self) -> None:
        assert normalize_text("\n\n  hola  \n\n") == "hola"
