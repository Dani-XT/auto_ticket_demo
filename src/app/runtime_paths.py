# Ruta de datos que no seran empaquetadas
from src.app.env import IS_DEV, IS_PROD, APP_NAME
from src.app.paths import PROJECT_DIR

from pathlib import Path
import os

def _get_appdata_dir() -> Path:
    local_appdata = os.environ.get("LOCALAPPDATA")

    if local_appdata:
        return Path(local_appdata)
    
    return Path.home() / "AppData" / "Local"


if IS_DEV:
    DATA_DIR = PROJECT_DIR / "storages"

if IS_PROD:
    DATA_DIR = _get_appdata_dir() / APP_NAME

AUTH_DIR = DATA_DIR / "auth"
LOGS_DIR = DATA_DIR / "logs"

TEMPLATE_DIR = DATA_DIR / "templates"
UPLOAD_README_FILE = TEMPLATE_DIR / "upload_readme.html"

SETTINGS_DIR = DATA_DIR / "settings"
USER_SETTINGS_FILE = SETTINGS_DIR / "user_settings.json"


EXCEL_SETTINGS_FILE = SETTINGS_DIR / "excel_settings.json"
