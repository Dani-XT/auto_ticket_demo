import json
from pathlib import Path

from src.app.runtime_paths import USER_SETTINGS_FILE

class SettingsRepository:
    def __init__(self, settings_file: Path = USER_SETTINGS_FILE):
        self.settings_file = settings_file

    def exists(self) -> bool:
        return self.settings_file.exists()

    def load(self) -> dict:
        if not self.settings_file.exists():
            return {}

        with self.settings_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save(self, data: dict) -> None:
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)

        with self.settings_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def delete(self) -> None:
        if self.settings_file.exists():
            self.settings_file.unlink()