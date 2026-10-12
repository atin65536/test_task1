from __future__ import annotations

from typing import Annotated
import logging
from uuid import UUID

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from fastapi import FastAPI, Query, HTTPException, status


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WEBHOOK_")

    success: bool = True


settings = Settings.model_validate({})


class WebhookData(BaseModel):
    key: str
    status: str


logger = logging.getLogger("uvicorn.error")
app = FastAPI()


@app.get("/api/v1/webhook")
async def webhook(query: Annotated[WebhookData, Query()]) -> None:
    logger.info(f"Called webhook with: {query}")
    if not settings.success:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)