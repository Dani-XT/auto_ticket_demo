from pathlib import Path
import sys

from src.app.env import IS_PACKAGED

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent


def get_resource_base_dir() -> Path:
    if IS_PACKAGED:
        return Path(getattr(sys, "_MEIPASS"))
    return PROJECT_DIR

RESOURCE_BASE_DIR = get_resource_base_dir()

SRC_DIR = PROJECT_DIR / "src"
ASSETS_DIR = RESOURCE_BASE_DIR / "assets"
ICON_DIR = ASSETS_DIR / "icons"
IMG_DIR = ASSETS_DIR / "images"
TEMPLATES_DIR = ASSETS_DIR / "templates"