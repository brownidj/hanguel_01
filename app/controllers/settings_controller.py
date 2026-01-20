from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QSpinBox

from app.domain.enums import DelayKey, DelaySeconds, DelaysConfig
from app.services.settings_store import SettingsStore


class SettingsController:
    """Qt wiring for delays + repeats."""

    def __init__(self, store: SettingsStore) -> None:
        self._store = store

        self._spin_pre_first: Optional[QSpinBox] = None
        self._spin_between_reps: Optional[QSpinBox] = None
        self._spin_before_hints: Optional[QSpinBox] = None
        self._spin_before_extras: Optional[QSpinBox] = None
        self._spin_auto_advance: Optional[QSpinBox] = None
        self._spin_repeats: Optional[QSpinBox] = None

    def bind_delay_spinboxes(
            self,
            *,
            spin_pre_first: Optional[QSpinBox],
            spin_between_reps: Optional[QSpinBox],
            spin_before_hints: Optional[QSpinBox],
            spin_before_extras: Optional[QSpinBox],
            spin_auto_advance: Optional[QSpinBox],
    ) -> None:
        self._spin_pre_first = spin_pre_first
        self._spin_between_reps = spin_between_reps
        self._spin_before_hints = spin_before_hints
        self._spin_before_extras = spin_before_extras
        self._spin_auto_advance = spin_auto_advance

    def bind_repeats_spinbox(self, spin_repeats: Optional[QSpinBox]) -> None:
        self._spin_repeats = spin_repeats

    def apply_delays_from_store(self) -> None:
        vals: DelaySeconds = self._store.get_delay_seconds()
        try:
            if self._spin_pre_first is not None:
                self._spin_pre_first.setValue(int(vals.pre_first))
            if self._spin_between_reps is not None:
                self._spin_between_reps.setValue(int(vals.between_reps))
            if self._spin_before_hints is not None:
                self._spin_before_hints.setValue(int(vals.before_hints))
            if self._spin_before_extras is not None:
                self._spin_before_extras.setValue(int(vals.before_extras))
            if self._spin_auto_advance is not None:
                self._spin_auto_advance.setValue(int(vals.auto_advance))
        except Exception:
            pass

    def apply_repeats_from_store(self) -> None:
        try:
            if self._spin_repeats is not None:
                self._spin_repeats.setValue(int(self._store.get_repeats()))
        except Exception:
            pass

    def wire_delay_persistence(self) -> None:
        pairs = [
            (self._spin_pre_first, DelayKey.PRE_FIRST),
            (self._spin_between_reps, DelayKey.BETWEEN_REPS),
            (self._spin_before_hints, DelayKey.BEFORE_HINTS),
            (self._spin_before_extras, DelayKey.BEFORE_EXTRAS),
            (self._spin_auto_advance, DelayKey.AUTO_ADVANCE),
        ]

        for sb, key in pairs:
            if sb is None:
                continue
            try:
                sb.valueChanged.disconnect()
            except Exception:
                pass

            def _mk_handler(k: DelayKey):
                return lambda val: self._store.set_delay_seconds(k, int(val))

            sb.valueChanged.connect(_mk_handler(key))

    def wire_repeats_persistence(self) -> None:
        if self._spin_repeats is None:
            return
        try:
            self._spin_repeats.valueChanged.disconnect()
        except Exception:
            pass
        self._spin_repeats.valueChanged.connect(lambda v: self._store.set_repeats(int(v)))

    def current_repeats(self) -> int:
        try:
            if self._spin_repeats is not None:
                return max(1, int(self._spin_repeats.value()))
        except Exception:
            pass
        return self._store.get_repeats()

    def current_delay_seconds(self) -> DelaySeconds:
        stored = self._store.get_delay_seconds()

        def _read(sb: Optional[QSpinBox], default: int) -> int:
            try:
                if sb is not None:
                    return int(sb.value())
            except Exception:
                pass
            return int(default)

        return DelaySeconds(
            pre_first=_read(self._spin_pre_first, stored.pre_first),
            between_reps=_read(self._spin_between_reps, stored.between_reps),
            before_hints=_read(self._spin_before_hints, stored.before_hints),
            before_extras=_read(self._spin_before_extras, stored.before_extras),
            auto_advance=_read(self._spin_auto_advance, stored.auto_advance),
        )

    def current_delays_ms(self) -> DelaysConfig:
        d = self.current_delay_seconds()
        return DelaysConfig(
            pre_first_ms=int(d.pre_first) * 1000,
            between_reps_ms=int(d.between_reps) * 1000,
            before_hints_ms=int(d.before_hints) * 1000,
            before_extras_ms=int(d.before_extras) * 1000,
            auto_advance_ms=int(d.auto_advance) * 1000,
        )
