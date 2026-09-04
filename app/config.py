import os
from functools import lru_cache
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "mysql+mysqlconnector://root:password@localhost:3306/franchiseops"
    db_password: Optional[str] = None
    app_name: str = "FranchiseOps AI Backend"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    @field_validator("database_url", mode="before")
    @classmethod
    def inject_db_password(cls, value: str, info) -> str:
        password = info.data.get("db_password")
        if password and isinstance(value, str) and "${DB_PASSWORD}" in value:
            return value.replace("${DB_PASSWORD}", password)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
