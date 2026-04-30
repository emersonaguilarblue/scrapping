DEFAULT_HEADERS: dict[str, str] = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

REMOVABLE_SELECTORS: tuple[str, ...] = (
    "script",
    "style",
    "noscript",
    "iframe",
    "header",
    "footer",
    "nav",
    "[role=navigation]",
    "[aria-hidden=true]",
    ".cookie",
    ".cookies",
    "#onetrust-banner-sdk",
)

CONTENT_SELECTORS: tuple[str, ...] = (
    "main",
    "article",
    "[role=main]",
    ".main-content",
    "#main",
    "body",
)

PDF_CONTENT_TYPES: frozenset[str] = frozenset(
    {"application/pdf", "application/octet-stream"}
)

HTML_CONTENT_TYPES: frozenset[str] = frozenset(
    {"text/html", "application/xhtml+xml"}
)
