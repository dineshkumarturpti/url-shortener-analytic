from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.url import ClickEvent, URL


def record_click(db: Session, url_id: int, referrer: str | None, user_agent: str | None) -> None:
    """
    Append-only write on every redirect. Kept intentionally minimal (no joins,
    no aggregation) so it never becomes the bottleneck on the hot redirect path
    -- aggregate queries (total clicks, recent activity) live in this module
    and run on-demand from the dashboard instead.
    """
    db.add(ClickEvent(url_id=url_id, referrer=referrer, user_agent=user_agent))
    db.commit()


def get_total_clicks(db: Session, url_id: int) -> int:
    return db.query(func.count(ClickEvent.id)).filter(ClickEvent.url_id == url_id).scalar() or 0


def get_recent_clicks(db: Session, url_id: int, limit: int = 20) -> list[ClickEvent]:
    return (
        db.query(ClickEvent)
        .filter(ClickEvent.url_id == url_id)
        .order_by(ClickEvent.clicked_at.desc())
        .limit(limit)
        .all()
    )
