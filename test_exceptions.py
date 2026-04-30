"""Pruebas para src.core.exceptions."""
from src.core.exceptions import (
    ParserError,
    ScraperError,
    ScrapingPipelineError,
    SourceNotFoundError,
    StorageError,
)


class TestExceptionHierarchy:
    def test_all_inherit_from_pipeline_error(self) -> None:
        for exc in (ScraperError, ParserError, StorageError, SourceNotFoundError):
            assert issubclass(exc, ScrapingPipelineError)

    def test_pipeline_error_is_exception(self) -> None:
        assert issubclass(ScrapingPipelineError, Exception)

    def test_can_be_raised_with_message(self) -> None:
        try:
            raise ParserError("fail")
        except ScrapingPipelineError as e:
            assert str(e) == "fail"
