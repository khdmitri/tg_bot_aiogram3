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
    BOT_TOKEN: str
    LOG_LEVEL: str
    USE_REDIS: bool
    REDIS_HOST: str
    REDIS_PORT: int


settings = Settings()
