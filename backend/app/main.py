import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.db.session import Base, engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creates tables on startup if they don't exist yet. In a real production
    # deploy this would ideally be replaced by Alembic migrations, but this
    # keeps local/dev setup to one command. Wrapped so the app (and the test
    # suite, which overrides the DB dependency per-test) can still
    # import/start even if Postgres isn't up.
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:  # pragma: no cover - depends on local environment
        logger.warning("Could not create tables on startup: %s", exc)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}


app.include_router(router)
