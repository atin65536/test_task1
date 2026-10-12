from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_dsn: str
    api_key: str
    rabbitmq_dsn: str


settings = Settings.model_validate({})
