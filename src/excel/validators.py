from pathlib import Path

from src.utils.exceptions import (
    ExcelFileNotFoundError,
    ExcelFileOpenError,
    ExcelRequiredColumnsError,
)

import logging


logger = logging.getLogger(__name__)


def validate_excel(path: Path) -> None:
    _validate_exists(path)
    _validate_open(path)


def _validate_exists(path: Path) -> None:
    if not path.exists():
        logger.error("El archivo excel no existe")
        raise ExcelFileNotFoundError("El archivo Excel no existe.")
    
def _validate_open(path: Path) -> None:
    try:
        with open(path, "rb+"):
            pass
    except PermissionError:
        logger.error("El archivo excel esta abierto")
        raise ExcelFileOpenError("El archivo Excel está abierto. Ciérralo antes de continuar.")


def validate_format() -> str:
    pass