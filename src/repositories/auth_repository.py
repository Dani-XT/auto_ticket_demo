from pathlib import Path

from src.app.runtime_paths import AUTH_DIR

class AuthRepository:
    def __init__(self):
        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        self.state_path = AUTH_DIR / "proactiva_storage_state.json"

    def exists(self) -> bool:
        return self.state_path.exists()

    def get_state_path(self) -> Path:
        return self.state_path

    def save_storage_state(self, context) -> None:
        context.storage_state(path=str(self.state_path))

    def delete(self) -> None:
        if self.state_path.exists():
            self.state_path.unlink()