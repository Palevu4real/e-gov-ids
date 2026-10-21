from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from app.core.config import settings
from app.api import auth, alerts
from app.consumers.kafka_consumer import consume_alerts

# Set up logging
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Kafka consumer in the background
    task = asyncio.create_task(consume_alerts())
    yield
    # Cancel on shutdown
    task.cancel()

app = FastAPI(title=settings.APP_NAME, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.APP_NAME}