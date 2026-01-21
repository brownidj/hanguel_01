

from __future__ import annotations

from dataclasses import replace
from typing import Callable, List, Optional, Tuple

from app.domain.enums import PairStatus, ProgressionDirection, ProgressionState, ProgressionStep


SyllableLookup = Callable[[str, str], Tuple[str, str, str, str, PairStatus]]


class ProgressionController:
    """
    Domain-level progression engine (UI-agnostic).

    Traverses a consonant-vowel (CV) space according to a direction, anchor(s), and inclusion rules.

    Notes:
    - Skipping rules are based on PairStatus names where available:
        - Always skip status == "IMPOSSIBLE"
        - Skip status == "RARE" unless include_rare is True
      If your PairStatus enum does not define these names, no skipping occurs.
    """

    def __init__(
        self,
        consonant_order: List[str],
        vowel_order_basic: List[str],
        vowel_order_adv: List[str],
        syllable_lookup: SyllableLookup,
        state: Optional[ProgressionState] = None,
    ) -> None:
        self._consonant_order = list(consonant_order)
        self._vowel_basic = list(vowel_order_basic)
        self._vowel_adv = list(vowel_order_adv)
        self._lookup = syllable_lookup

        # Default state if none is provided
        if state is None:
            state = ProgressionState()  # type: ignore[call-arg]

        self._state: ProgressionState = state

        # Internal indices. If the provided state already carries indices, respect them.
        self._ci: int = int(getattr(state, "consonant_index", getattr(state, "ci", 0)) or 0)
        self._vi: int = int(getattr(state, "vowel_index", getattr(state, "vi", 0)) or 0)

        # If anchors are set, align indices to anchors immediately.
        self._align_to_anchors()

        # Ensure indices are within bounds.
        self._clamp_indices()

    # ---------------------------
    # Public state setters
    # ---------------------------

    def set_direction(self, direction: ProgressionDirection) -> None:
        self._state = self._state_replace(direction=direction)
        self._align_to_anchors()
        self._clamp_indices()

    def set_anchor_consonant(self, c: str) -> None:
        self._state = self._state_replace(anchor_consonant=c)
        self._align_to_anchors()
        self._clamp_indices()

    def set_anchor_vowel(self, v: str) -> None:
        self._state = self._state_replace(anchor_vowel=v)
        self._align_to_anchors()
        self._clamp_indices()

    def set_include_rare(self, include: bool) -> None:
        self._state = self._state_replace(include_rare=include)

    def set_use_advanced_vowels(self, use_adv: bool) -> None:
        self._state = self._state_replace(use_advanced_vowels=use_adv)
        self._align_to_anchors()
        self._clamp_indices()

    def reset(self) -> None:
        self._ci = 0
        self._vi = 0
        self._align_to_anchors()
        self._clamp_indices()

    # ---------------------------
    # Core navigation API
    # ---------------------------

    def current(self) -> ProgressionStep:
        return self._step_at(self._ci, self._vi)

    def next(self) -> ProgressionStep:
        return self._advance(delta=1)

    def prev(self) -> ProgressionStep:
        return self._advance(delta=-1)

    def progress_summary(self) -> str:
        """
        Human-readable summary based on the current direction.
        Example: "3/10 vowels" (if vowel-major) or "5/19 consonants" (if consonant-major).
        """
        if self._is_vowel_major():
            total = max(len(self._active_vowels()), 1)
            current = min(max(self._vi + 1, 1), total)
            return "{0}/{1} vowels".format(current, total)

        total = max(len(self._consonant_order), 1)
        current = min(max(self._ci + 1, 1), total)
        return "{0}/{1} consonants".format(current, total)

    # ---------------------------
    # Internal helpers
    # ---------------------------

    def _state_replace(self, **kwargs):
        """
        Replace fields on ProgressionState if it is a dataclass; otherwise, fall back to setattr.
        """
        try:
            return replace(self._state, **kwargs)  # type: ignore[arg-type]
        except Exception:
            # Mutable fallback: set attributes in-place when replace() is not available.
            for k, v in kwargs.items():
                try:
                    setattr(self._state, k, v)
                except Exception:
                    pass
            return self._state

    def _active_vowels(self) -> List[str]:
        use_adv = bool(getattr(self._state, "use_advanced_vowels", False))
        return self._vowel_adv if use_adv else self._vowel_basic

    def _is_vowel_major(self) -> bool:
        """
        Determine traversal mode based on ProgressionDirection naming.
        This keeps the engine resilient if enum member names evolve.
        """
        d = getattr(self._state, "direction", None)
        if d is None:
            return True
        name = getattr(d, "name", "")
        name_upper = (name or "").upper()
        if "CONSONANT" in name_upper:
            return False
        if "VOWEL" in name_upper:
            return True
        # Default to vowel-major if unclear
        return True

    def _align_to_anchors(self) -> None:
        anchor_c = getattr(self._state, "anchor_consonant", None)
        anchor_v = getattr(self._state, "anchor_vowel", None)

        if anchor_c:
            try:
                self._ci = self._consonant_order.index(anchor_c)
            except ValueError:
                pass

        if anchor_v:
            vowels = self._active_vowels()
            try:
                self._vi = vowels.index(anchor_v)
            except ValueError:
                pass

    def _clamp_indices(self) -> None:
        if not self._consonant_order:
            self._ci = 0
        else:
            self._ci = max(0, min(self._ci, len(self._consonant_order) - 1))

        vowels = self._active_vowels()
        if not vowels:
            self._vi = 0
        else:
            self._vi = max(0, min(self._vi, len(vowels) - 1))

    def _advance(self, delta: int) -> ProgressionStep:
        """
        Move forward/backward in the CV space according to direction,
        returning the next valid step after applying skipping rules.
        """
        if not self._consonant_order or not self._active_vowels():
            # Degenerate case: orders not configured
            return self.current()

        max_guard = len(self._consonant_order) * len(self._active_vowels()) + 5
        guard = 0

        ci = self._ci
        vi = self._vi

        while guard < max_guard:
            guard += 1

            ci, vi = self._advance_indices(ci, vi, delta)
            step = self._step_at(ci, vi)

            if self._is_step_allowed(step):
                self._ci = ci
                self._vi = vi
                return step

        # If we can't find anything allowed, fall back to current.
        return self.current()

    def _advance_indices(self, ci: int, vi: int, delta: int) -> Tuple[int, int]:
        vowels = self._active_vowels()
        c_count = len(self._consonant_order)
        v_count = len(vowels)

        if c_count <= 0 or v_count <= 0:
            return ci, vi

        if self._is_vowel_major():
            vi += delta
            if vi >= v_count:
                vi = 0
                ci += 1
            elif vi < 0:
                vi = v_count - 1
                ci -= 1

            if ci >= c_count:
                ci = 0
            elif ci < 0:
                ci = c_count - 1

            return ci, vi

        # consonant-major
        ci += delta
        if ci >= c_count:
            ci = 0
            vi += 1
        elif ci < 0:
            ci = c_count - 1
            vi -= 1

        if vi >= v_count:
            vi = 0
        elif vi < 0:
            vi = v_count - 1

        return ci, vi

    def _is_step_allowed(self, step: ProgressionStep) -> bool:
        include_rare = bool(getattr(self._state, "include_rare", False))
        status = getattr(step, "status", None)

        # If status isn't an enum with a name, allow it.
        status_name = getattr(status, "name", None)
        if not status_name:
            return True

        status_name_upper = str(status_name).upper()

        if status_name_upper == "IMPOSSIBLE":
            return False
        if status_name_upper == "RARE" and not include_rare:
            return False

        return True

    def _step_at(self, ci: int, vi: int) -> ProgressionStep:
        vowels = self._active_vowels()
        c = self._consonant_order[ci] if self._consonant_order else ""
        v = vowels[vi] if vowels else ""

        cons, vow, glyph, block_type, status = self._lookup(c, v)

        # Construct ProgressionStep in a resilient way: prefer keywords, fall back to positional.
        try:
            return ProgressionStep(
                consonant=cons,
                vowel=vow,
                glyph=glyph,
                block_type=block_type,
                status=status,
            )
        except Exception:
            try:
                return ProgressionStep(cons, vow, glyph, block_type, status)  # type: ignore[misc]
            except Exception:
                # Last resort: return whatever is possible
                return ProgressionStep()  # type: ignore[call-arg]