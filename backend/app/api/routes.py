from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.url import AnalyticsResponse, ShortenRequest, ShortenResponse
from app.services import analytics, shortener

router = APIRouter()


@router.post("/api/shorten", response_model=ShortenResponse, status_code=201)
def shorten_url(payload: ShortenRequest, db: Session = Depends(get_db)):
    url_row = shortener.create_short_url(db, long_url=str(payload.long_url))
    return ShortenResponse(
        short_code=url_row.short_code,
        short_url=f"{settings.base_redirect_url}/{url_row.short_code}",
        long_url=url_row.long_url,
        created_at=url_row.created_at,
    )


@router.get("/{short_code}")
def redirect_to_long_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    long_url = shortener.resolve_short_code(db, short_code)
    if long_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    url_row = shortener.get_url_row_by_code(db, short_code)
    if url_row is not None:
        analytics.record_click(
            db,
            url_id=url_row.id,
            referrer=request.headers.get("referer"),
            user_agent=request.headers.get("user-agent"),
        )

    return RedirectResponse(url=long_url, status_code=307)


@router.get("/api/analytics/{short_code}", response_model=AnalyticsResponse)
def get_analytics(short_code: str, db: Session = Depends(get_db)):
    url_row = shortener.get_url_row_by_code(db, short_code)
    if url_row is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    total_clicks = analytics.get_total_clicks(db, url_row.id)
    recent_clicks = analytics.get_recent_clicks(db, url_row.id)

    return AnalyticsResponse(
        short_code=url_row.short_code,
        long_url=url_row.long_url,
        total_clicks=total_clicks,
        created_at=url_row.created_at,
        recent_clicks=recent_clicks,
    )
