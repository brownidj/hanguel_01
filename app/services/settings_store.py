from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from app.domain.enums import DelayKey, DelaySeconds
import logging

logger = logging.getLogger(__name__)


class SettingsStore:
    """YAML-backed settings store.

    Responsibilities:
      - Load/save settings.yaml atomically
      - Provide typed helpers for delays + repeats

    Notes:
      - Delays are stored in SECONDS (matching UI).
    """

    def __init__(self, settings_path: str | None = None) -> None:
        if settings_path is None:
            # Default to project root next to main.py.
            # This resolves to: <project_root>/settings.yaml
            project_root = Path(__file__).resolve().parents[2]
            self._path = project_root / "settings.yaml"
        else:
            self._path = Path(settings_path)

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> dict[str, Any]:
        try:
            p = self._path
            if not p.exists():
                return {}
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return data if isinstance(data, dict) else {}
        except (OSError, yaml.YAMLError, ValueError) as e:
            logger.warning("Failed to load settings from %s: %s", self._path, e)
            return {}

    def save(self, data: dict[str, Any]) -> None:
        try:
            p = self._path
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(p.suffix + ".tmp")
            with tmp.open("w", encoding="utf-8") as f:
                yaml.safe_dump(data or {}, f, allow_unicode=True, sort_keys=True)
            os.replace(str(tmp), str(p))
        except (OSError, yaml.YAMLError, ValueError) as e:
            logger.warning("Failed to save settings to %s: %s", self._path, e)
            # Best-effort persistence; callers should not crash on save failures.
            pass

    def get_delay_seconds(self) -> DelaySeconds:
        s = self.load()
        d = s.get("delays") or {}
        if not isinstance(d, dict):
            d = {}

        def _ival(key: str, default: int) -> int:
            try:
                v = d.get(key, default)
                if isinstance(v, (int, float)):
                    return int(v)
            except (TypeError, ValueError, AttributeError):
                pass
            return int(default)

        return DelaySeconds(
            pre_first=_ival(DelayKey.PRE_FIRST.value, 0),
            between_reps=_ival(DelayKey.BETWEEN_REPS.value, 2),
            before_hints=_ival(DelayKey.BEFORE_HINTS.value, 0),
            before_extras=_ival(DelayKey.BEFORE_EXTRAS.value, 1),
            auto_advance=_ival(DelayKey.AUTO_ADVANCE.value, 0),
        )

    def set_delay_seconds(self, key: DelayKey, value: int) -> None:
        try:
            s = self.load()
            d = s.get("delays") or {}
            if not isinstance(d, dict):
                d = {}
            d[key.value] = int(value)
            s["delays"] = d
            self.save(s)
        except Exception as e:
            print("[WARN] Failed to persist delay '{}':".format(key.value), e)

    def get_repeats(self) -> int:
        try:
            s = self.load()
            v = int(s.get("repeats", 1))
            return 1 if v < 1 else v
        except Exception as e:
            print("[WARN] Failed to get repeats '{}':".format(v), e)
            return 1

    def set_repeats(self, value: int) -> None:
        try:
            s = self.load()
            s["repeats"] = max(1, int(value))
            self.save(s)
        except Exception as e:
            print("[WARN] Failed to persist repeats:", e)

    def get_wpm(self) -> int:
        try:
            s = self.load()
            v = int(s.get("wpm", 120))
            return max(40, min(160, v))
        except Exception as e:
            print("[WARN] Failed to get wpm:", e)
            return 120

    def set_wpm(self, value: int) -> None:
        try:
            s = self.load()
            v = max(40, min(160, int(value)))
            s["wpm"] = v
            self.save(s)
        except Exception as e:
            print("[WARN] Failed to persist wpm:", e)

    def get_mode(self) -> str | None:
        try:
            s = self.load()
            mode = s.get("mode")
            if isinstance(mode, str) and mode.strip():
                return mode.strip()
        except Exception:
            pass
        return None

    def set_mode(self, mode: str) -> None:
        try:
            s = self.load()
            value = (mode or "").strip()
            if value:
                s["mode"] = value
                self.save(s)
        except Exception:
            pass

    def get_rr_cues(self) -> bool | None:
        try:
            s = self.load()
            val = s.get("rr_show_cues")
            if isinstance(val, bool):
                return val
        except Exception:
            pass
        return None

    def set_rr_cues(self, value: bool) -> None:
        try:
            s = self.load()
            s["rr_show_cues"] = bool(value)
            self.save(s)
        except Exception:
            pass
