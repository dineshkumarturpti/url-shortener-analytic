from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class ShortenRequest(BaseModel):
    long_url: HttpUrl = Field(..., description="The original URL to shorten")


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class ClickStat(BaseModel):
    clicked_at: datetime
    referrer: str | None = None
    user_agent: str | None = None

    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    short_code: str
    long_url: str
    total_clicks: int
    created_at: datetime
    recent_clicks: list[ClickStat]
