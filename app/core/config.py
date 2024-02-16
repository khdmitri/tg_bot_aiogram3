import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import field_validator, AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn
import logging
from dotenv import load_dotenv
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DATABASE: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode='before')
    def assemble_db_connection(cls, v: Optional[str], values: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        url = PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            port=int(values.data.get("POSTGRES_PORT")),
            path=f"/{values.data.get('POSTGRES_DATABASE') or ''}",
        )
        logger.info(f"PostgresURL: {url}")
        return url

    SQLALCHEMY_DATABASE_URI_ASYNC: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI_ASYNC", mode='before')
    def assemble_db_connection_async(cls, v: Optional[str], values: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            port=int(values.data.get("POSTGRES_PORT")),
            path=f"{values.data.get('POSTGRES_DATABASE') or ''}",
        )

    APP_VERSION: str


settings = Settings()