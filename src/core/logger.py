import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.core.app_context import AppContext

from src.app.env import APP_DEBUG, APP_NAME


def setup_logging(app_context: AppContext) -> None:

    runtime = app_context.runtime



    log_level = logging.DEBUG if APP_DEBUG else logging.INFO
    log_file: Path = runtime.logs_dir / f"{APP_NAME.lower()}.log"

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8"
    )

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Silenciar librerías muy verbosas
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)