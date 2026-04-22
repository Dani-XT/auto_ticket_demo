# Decide el entorno
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
ENV_PROD_FILE = BASE_DIR / ".env.prod"

def _load_environment_files() -> None:
    if load_dotenv is None:
        return
    
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE, override=False)

    if getattr(sys, "frozen", False) and ENV_PROD_FILE.exists():
        load_dotenv(ENV_PROD_FILE, override=True)

def _normalize_app_env(value: str | None) -> str:
    if not value:
        return "prod" if getattr(sys, "frozen", False) else "dev"
    
    normalized = value.strip().lower()

    if normalized in {"dev", "development"}:
        return "dev"
    
    if normalized in {"prod", "production"}:
        return "prod"
    
    return "prod" if getattr(sys, "frozen", False) else "dev"

def _to_bool(value: str | bool | None, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on", "si", "sí"}


_load_environment_files()

IS_PACKAGED = getattr(sys, "frozen", False)

APP_ENV = _normalize_app_env(os.getenv("APP_ENVIRONMENT"))
APP_NAME = os.getenv("APP_NAME", "AutomatizarTicket")
APP_DEBUG = _to_bool(os.getenv("APP_DEBUG"), default=(APP_ENV == "dev"))

IS_DEV = APP_ENV == "dev"
IS_PROD = APP_ENV == "prod"