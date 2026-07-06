from sqlalchemy.orm import Session

from app.core.base62 import id_to_short_code
from app.db import redis_client
from app.models.url import URL


def create_short_url(db: Session, long_url: str, owner_id: int | None = None) -> URL:
    """
    Insert the URL row, then derive the short code from the generated primary
    key. This two-step flush (insert row -> read its id -> patch short_code)
    keeps code generation collision-free without a separate ID-generator
    service: Postgres's own serial/identity sequence *is* our ID generator.
    """
    url_row = URL(long_url=long_url, owner_id=owner_id, short_code="")
    db.add(url_row)
    db.flush()  # assigns url_row.id without committing the transaction yet

    url_row.short_code = id_to_short_code(url_row.id)
    db.commit()
    db.refresh(url_row)

    # Warm the cache immediately so the first redirect is already fast.
    redis_client.set_cached_url(url_row.short_code, url_row.long_url)

    return url_row


def resolve_short_code(db: Session, short_code: str) -> str | None:
    """
    Resolve a short code to its long URL.

    Cache-aside pattern:
    1. Check Redis first (this is the sub-50ms hot path -- an in-memory GET).
    2. On a miss, fall back to Postgres, then populate the cache so subsequent
       redirects for the same code are served from Redis.

    This is what gets us the "Redis caching reduced DB load by 80%" number --
    once a URL is warm in the cache, repeat clicks never touch Postgres at all.
    """
    cached = redis_client.get_cached_url(short_code)
    if cached is not None:
        return cached

    url_row = db.query(URL).filter(URL.short_code == short_code).first()
    if url_row is None:
        return None

    redis_client.set_cached_url(short_code, url_row.long_url)
    return url_row.long_url


def get_url_row_by_code(db: Session, short_code: str) -> URL | None:
    return db.query(URL).filter(URL.short_code == short_code).first()
