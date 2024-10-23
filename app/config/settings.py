import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):

    # App
    APP_NAME: str = os.environ.get("APP_NAME", "FastAPI")
    DEBUG: bool = bool(os.environ.get("DEBUG", False))

    # PostgreSQL Database Config
    DB_HOST: str = os.environ.get("DB_HOST", 'localhost')
    DB_USER: str = os.environ.get("DB_USERNAME", 'root')
    DB_PASS: str = os.environ.get("DB_PASSWORD", 'secret')
    DB_PORT: int = int(os.environ.get("DB_PORT", 5432))
    DB_DATABASE: str = os.environ.get("DB_DATABASE", 'fastapi')

    # Create the DATABASE_URI with the updated variables
    DATABASE_URI: str = f"postgresql://{DB_USER}:%s@{DB_HOST}:{DB_PORT}/{DB_DATABASE}" % quote_plus(DB_PASS)
    # JWT Configuration
    JWT_SECRET: str = os.environ.get("JWT_SECRET")
    JWT_PUBLIC: str = os.environ.get("JWT_PUBLIC")

    # M2M Authentication Config
    M2M_AIA_CLIENT_ID: str = os.environ.get("M2M_AIA_CLIENT_ID")
    M2M_AIA_CLIENT_SECRET: str = os.environ.get("M2M_AIA_CLIENT_SECRET")
    M2M_AIA_APP_ID: str = os.environ.get("M2M_AIA_APP_ID")
    AUTH_URL: str = os.environ.get("AUTH_URL")

    # IAM Service Host and Port
    INV_IAM_SERVICE_HOST: str = os.environ.get("INV_IAM_SERVICE_HOST")
    INV_IAM_SERVICE_PORT: str = os.environ.get("INV_IAM_SERVICE_PORT")

    # Dynamic URLs for SSO and organisation Login
    @property
    def SSO_URL(self) -> str:
        """
        Dynamically generate the SSO URL based on the host and port.
        """
        return f"http://{self.INV_IAM_SERVICE_HOST}:{self.INV_IAM_SERVICE_PORT}/iam/sso/token"

    @property
    def ORG_LOGIN_URL(self) -> str:
        """
        Dynamically generate the organisation login URL based on the host and port.
        """
        return f"http://{self.INV_IAM_SERVICE_HOST}:{self.INV_IAM_SERVICE_PORT}/iam/organisation/login"

# Load settings using LRU cache
@lru_cache()
def get_settings() -> Settings:
    return Settings()
