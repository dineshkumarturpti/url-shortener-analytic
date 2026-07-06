from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central application configuration.

    Values are pulled from environment variables (or a .env file) so the
    same image can run in dev / staging / prod without code changes.
    """

    app_name: str = "URL Shortener & Analytics Platform"
    environment: str = "development"

    # Postgres
    database_url: str = "postgresql://postgres:postgres@localhost:5432/url_shortener"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 3600  # how long a short-code -> long-url mapping stays cached

    # Short code generation
    base62_alphabet: str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    short_code_min_length: int = 6
    # Offset so the very first row doesn't encode to "0" / "1" (looks nicer, avoids collisions
    # with reserved single-character routes like health checks).
    id_offset: int = 100_000

    base_redirect_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
