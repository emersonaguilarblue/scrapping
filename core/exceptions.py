class ScrapingPipelineError(Exception):
    pass


class ScraperError(ScrapingPipelineError):
    pass


class ParserError(ScrapingPipelineError):
    pass


class StorageError(ScrapingPipelineError):
    pass


class SourceNotFoundError(ScrapingPipelineError):
    pass
