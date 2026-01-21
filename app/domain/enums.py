from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DelayKey(str, Enum):
    """Keys used in settings.yaml under the `delays:` mapping."""
    PRE_FIRST = "pre_first"
    BETWEEN_REPS = "between_reps"
    BEFORE_HINTS = "before_hints"
    BEFORE_EXTRAS = "before_extras"
    AUTO_ADVANCE = "auto_advance"


@dataclass(frozen=True)
class DelaySeconds:
    """Delay values as stored/shown in the UI (seconds)."""
    pre_first: int = 0
    between_reps: int = 2
    before_hints: int = 0
    before_extras: int = 1
    auto_advance: int = 0


@dataclass(frozen=True)
class DelaysConfig:
    """Delays used by the playback orchestrator (milliseconds)."""
    pre_first_ms: int = 0
    between_reps_ms: int = 2000
    before_hints_ms: int = 0
    before_extras_ms: int = 1000
    auto_advance_ms: int = 0


class BlockType(str, Enum):
    """The four vowel-driven Hangul block layout templates.

    IMPORTANT:
    - `main.py` and tests currently reference the legacy CamelCase member names
      (e.g., `A_RightBranch`).
    - We keep those names as the canonical API and provide uppercase aliases
      for robustness.
    """

    # Names used throughout the app
    A_RightBranch = "A"
    B_TopBranch = "B"
    C_BottomBranch = "C"
    D_Horizontal = "D"


class SegmentRole(str, Enum):
    """Logical role of a horizontal segment within a Hangul block.

    Keep legacy CamelCase names (`Top`, `Middle`, `Bottom`) as the canonical API
    because the UI wiring in `main.py` references them. Provide uppercase aliases
    for robustness.
    """

    # Names used throughout the app
    Top = "top"
    Middle = "middle"
    Bottom = "bottom"


# --- Additional domain enums ---

class ConsonantPosition(str, Enum):
    """Domain concept: whether a consonant is in initial (leading) or final position."""

    Initial = "initial"
    Final = "final"


class ProgressionDirection(str, Enum):
    """Direction of progression through CV space."""

    CONSONANT_TO_VOWEL = "C→V"
    VOWEL_TO_CONSONANT = "V→C"


class PairStatus(str, Enum):
    """Status tags for CV pairs loaded from YAML (syllables/overrides)."""

    ALLOWED = "allowed"
    RARE = "rare"
    NOT_USED = "not_used"
    IMPOSSIBLE = "impossible"


class StudyMode(Enum):
    """High-level study mode selection."""

    SYLLABLES = 1
    VOWELS = 2
    CONSONANTS = 3

# ----------------------------------------------------------------------------
# Progression model (domain dataclasses)
# ----------------------------------------------------------------------------


@dataclass
class ProgressionState:
    direction: ProgressionDirection = ProgressionDirection.CONSONANT_TO_VOWEL
    index_c: int = 0
    index_v: int = 0
    anchor_c: Optional[str] = None  # fixed consonant when direction is C→V
    anchor_v: Optional[str] = None  # fixed vowel when direction is V→C
    include_rare: bool = False
    use_advanced_vowels: bool = False  # toggle to include complex vowels


@dataclass(frozen=True)
class ProgressionStep:
    consonant: str  # e.g., "ㄱ"
    vowel: str  # e.g., "ㅏ"
    glyph: str  # e.g., "가"
    block_type: str  # "A_RightBranch" | "B_TopBranch" | "C_BottomBranch" | "D_Horizontal"
    status: PairStatus  # from YAML
    index_c: int  # consonant index in current order
    index_v: int  # vowel index in current order

# -----------------------------------------------------------------------------
# Block-type classification (domain logic)
# -----------------------------------------------------------------------------

# Minimal vowel sets for block classification (expand later as needed)
# _VOWELS_A = {"ㅏ", "ㅐ", "ㅑ", "ㅔ"}
# _VOWELS_B = {"ㅗ", "ㅛ", "ㅘ", "ㅙ", "ㅚ"}
# _VOWELS_C = {"ㅜ", "ㅠ", "ㅝ", "ㅞ"}
# _VOWELS_D = {"ㅣ", "ㅟ", "ㅢ", "ㅖ"}


# def block_type_for_pair(lead: str, vowel: str) -> "BlockType":
#     """Return a BlockType for a (leading, vowel) jamo pair.
#
#     Pure domain logic: no Qt dependencies.
#
#     Notes:
#       - `lead` is currently unused, but kept for API symmetry and future rules.
#       - Uses minimal vowel families for now; will later be data-driven from YAML.
#     """
#     v = str(vowel)
#     if v in _VOWELS_A:
#         return BlockType.A_RightBranch
#     if v in _VOWELS_B:
#         return BlockType.B_TopBranch
#     if v in _VOWELS_C:
#         return BlockType.C_BottomBranch
#     return BlockType.D_Horizontal
