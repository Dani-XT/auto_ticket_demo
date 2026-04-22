from dataclasses import dataclass
from pathlib import Path

from src.app import config as cfg
from src.app import paths as p
from src.app import runtime_paths as rp


@dataclass(frozen=True)
class AppConfig:
    app_size: str
    app_title: str
    app_id: str
    default_report_user: str
    default_job_group: str
    url_proactiva: str
    months_es: dict[int, str]
    months_es_inv: dict[str, int]
    creator_name: str
    creator_url: str


@dataclass(frozen=True)
class AppPaths:
    project_dir: Path
    src_dir: Path
    assets_dir: Path
    icon_dir: Path
    img_dir: Path
    templates_dir: Path


@dataclass(frozen=True)
class AppRuntimePaths:
    data_dir: Path
    auth_dir: Path
    logs_dir: Path
    settings_dir: Path
    templates_dir: Path
    user_settings_file: Path
    upload_readme_file: Path

@dataclass(frozen=True)
class AppContext:
    config: AppConfig
    paths: AppPaths
    runtime: AppRuntimePaths


def build_app_context() -> AppContext:
    return AppContext(
        config = AppConfig(
            app_size=cfg.APP_SIZE,
            app_title=cfg.APP_TITLE,
            app_id=cfg.APP_ID,
            default_report_user=cfg.DEFAULT_REPORT_USER,
            default_job_group=cfg.DEFAULT_JOB_GROUP,
            url_proactiva=cfg.URL_PROACTIVA,
            months_es=cfg.MONTHS_ES,
            months_es_inv=cfg.MONTHS_ES_INV,
            creator_name=cfg.CREATOR_NAME,
            creator_url=cfg.CREATOR_URL,
        ),
        paths = AppPaths(
            project_dir=p.PROJECT_DIR,
            src_dir=p.SRC_DIR,
            assets_dir=p.ASSETS_DIR,
            icon_dir=p.ICON_DIR,
            img_dir=p.IMG_DIR,
            templates_dir=p.TEMPLATES_DIR,
        ),
        runtime = AppRuntimePaths(
            data_dir=rp.DATA_DIR,
            auth_dir=rp.AUTH_DIR,
            logs_dir=rp.LOGS_DIR,
            settings_dir=rp.SETTINGS_DIR,
            templates_dir=rp.TEMPLATE_DIR,
            user_settings_file=rp.USER_SETTINGS_FILE,
            upload_readme_file=rp.UPLOAD_README_FILE,
        ),
    )