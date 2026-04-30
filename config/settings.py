from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SCRAPER_",
        case_sensitive=False,
        extra="ignore",
    )

    headless: bool = True
    timeout_ms: int = 60_000
    nav_wait: str = "domcontentloaded"
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    )
    locale: str = "es-CO"
    timezone: str = "America/Bogota"

    max_concurrency: int = 3
    retry_attempts: int = 3
    retry_backoff: float = 2.0
    cache_ttl_hours: int = 24

    raw_dir: Path = Field(default=Path("data/raw"))
    processed_dir: Path = Field(default=Path("data/processed"))
    cache_dir: Path = Field(default=Path("data/cache"))

    log_level: str = "INFO"
    respect_robots: bool = True

    chunk_size: int = 1500
    chunk_overlap: int = 150

    def ensure_dirs(self) -> None:
        for d in (self.raw_dir, self.processed_dir, self.cache_dir):
            d.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.ensure_dirs()
    return s
