from src.app.config import (DEFAULT_REPORT_USER, DEFAULT_JOB_GROUP)

from src.repositories.settings_repository import SettingsRepository

class SettingsManager:
    def __init__(self, repository: SettingsRepository | None = None):
        self.repository = repository or SettingsRepository()

    def get_defaults(self) -> dict:
        return {
            "report_user": DEFAULT_REPORT_USER,
            "job_group": DEFAULT_JOB_GROUP
        }
    
    def get_settings(self) -> dict:
        defaults = self.get_defaults()

        if not self.repository.exists():
            return defaults
        
        saved = self.repository.load()

        return {
            "report_user": saved.get("report_user", defaults["report_user"]),
            "job_group": saved.get("job_group", defaults["job_group"]),
        }
    
    def save_settings(self, report_user: str, job_group: str) -> None:
        data = {
            "report_user": report_user,
            "job_group": job_group,
        }
        self.repository.save(data)

    def restore_defaults(self) -> None:
        self.repository.delete()