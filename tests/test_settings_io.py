from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml

_DEBUG_MAIN = False
SETTINGS_PATH = Path(__file__).resolve().parent / "settings.yaml"


@dataclass
class DelaysConfig:
    pre_first: int = 0
    between_reps: int = 2
    before_hints: int = 0
    before_extras: int = 1
    auto_advance: int = 0


@dataclass
class SettingsStore:
    settings_path: Optional[Path] = None

    def __post_init__(self):
        if self.settings_path is None:
            self.settings_path = SETTINGS_PATH

    def load(self) -> Dict:
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data is None:
                    return {}
                return data
        except FileNotFoundError:
            return {}

    def save(self, data: Dict) -> None:
        with open(self.settings_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)

# Replace calls to removed helpers with direct calls or SettingsStore usage
# For example:
# settings = SettingsStore(settings_path=SETTINGS_PATH).load()
# SettingsStore(settings_path=SETTINGS_PATH).save(data)
# delays = DelaysConfig()
