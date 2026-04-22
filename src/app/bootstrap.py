from pathlib import Path
import logging
import shutil

from src.core.logger import setup_logging
from src.core.app_context import AppContext, build_app_context

logger = logging.getLogger(__name__)

REQUIRED_TEMPLATE_FILES = [
    "Planilla de Actividades - Nombre Tecnico.xlsx",
    "upload_readme.html",
    "process_readme.html",
    "config_readme.html",
    "favicon.ico",
]

def ensure_runtime_directories(app_context: AppContext) -> None:
    runtime_dirs = [
        app_context.runtime.data_dir,
        app_context.runtime.auth_dir,
        app_context.runtime.logs_dir,
        app_context.runtime.settings_dir,
        app_context.runtime.templates_dir,
    ]

    for directory in runtime_dirs:
        directory.mkdir(parents=True, exist_ok=True)


def validate_asset_template_files(app_context: AppContext) -> None:
    source_dir = app_context.paths.templates_dir

    missing = []
    for file_name in REQUIRED_TEMPLATE_FILES:
        source_file = source_dir / file_name
        if not source_file.exists():
            missing.append(str(source_file))

    if missing:
        raise FileNotFoundError(
            "Faltan archivos base en assets/templates:\n- " + "\n- ".join(missing)
        )

def copy_template_files_if_missing(app_context: AppContext) -> None:
    source_dir = app_context.paths.templates_dir
    target_dir = app_context.runtime.templates_dir

    for file_name in REQUIRED_TEMPLATE_FILES:
        source_file = source_dir / file_name
        target_file = target_dir / file_name

        if target_file.exists():
            continue

        shutil.copyfile(source_file, target_file)
        logger.info("Archivo base copiado a runtime: %s", target_file.name)


def validate_runtime_environment(app_context: AppContext) -> None:
    required_files = [
        app_context.runtime.templates_dir / "Planilla de Actividades - Nombre Tecnico.xlsx",
        app_context.runtime.templates_dir / "upload_readme.html",
        app_context.runtime.templates_dir / "process_readme.html",
        app_context.runtime.templates_dir / "config_readme.html",
        app_context.runtime.templates_dir / ""
    ]

    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Faltan archivos requeridos en runtime:\n- " + "\n- ".join(missing)
        )


def bootstrap_app() -> AppContext:
    app_context = build_app_context()

    ensure_runtime_directories(app_context)
    setup_logging(app_context)

    validate_asset_template_files(app_context)
    copy_template_files_if_missing(app_context)
    validate_runtime_environment(app_context)

    return app_context