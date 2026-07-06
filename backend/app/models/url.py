from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(16), unique=True, index=True, nullable=False)
    long_url = Column(String(2048), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    # Owner is optional -- lets the same platform support anonymous "quick shorten"
    # links as well as ones tied to a signed-in user for the dashboard view.
    owner_id = Column(Integer, nullable=True, index=True)

    clicks = relationship("ClickEvent", back_populates="url", cascade="all, delete-orphan")


class ClickEvent(Base):
    """
    One row per redirect. Deliberately kept append-only and narrow so writes are
    cheap even under high redirect volume -- aggregation/analytics happen in a
    separate read path (see services/analytics.py) rather than on every click.
    """

    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False, index=True)
    clicked_at = Column(DateTime, server_default=func.now(), index=True)
    referrer = Column(String(512), nullable=True)
    user_agent = Column(String(512), nullable=True)

    url = relationship("URL", back_populates="clicks")
