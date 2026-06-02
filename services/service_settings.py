import json
from dataclasses import asdict

from core.config import SETTINGS_FILE
from models.settings import Settings


class SettingsService:

    @staticmethod
    def load() -> Settings:
        if not SETTINGS_FILE.exists():
            return Settings()


        with open(SETTINGS_FILE, encoding="utf-8") as f:
            data = json.load(f)

        return Settings(**data)

    @staticmethod
    def save(settings: Settings):
        data = asdict(settings)


        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )