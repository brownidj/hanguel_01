from __future__ import annotations

"""Domain mapping and helpers for Hangul block layout templates.

This module is the single source of truth for:
  - The vowel -> BlockType mapping
  - block_type_for_pair() classification

It contains *no* Qt dependencies.
"""

from typing import Final

from app.domain.enums import BlockType


# -----------------------------------------------------------------------------
# Vowel -> BlockType mapping
# -----------------------------------------------------------------------------
#
# IMPORTANT:
# - This is DOMAIN DATA, not UI/pedagogy ordering.
# - It is intentionally explicit so tests and future YAML loading are stable.
# - If a vowel is not present, we default to D_Horizontal (conservative).
#
# Notes on the four templates:
#   A_RightBranch  : vertical vowels like ㅏ/ㅓ family
#   B_TopBranch    : top-anchored vowels like ㅗ family
#   C_BottomBranch : bottom-anchored vowels like ㅜ family
#   D_Horizontal   : horizontal/central vowels like ㅡ/ㅣ/ㅢ etc.

VOWEL_TO_BLOCK: Final[dict[str, BlockType]] = {
    # --- A: right-branch (vertical stems to the right) ---
    "ㅏ": BlockType.A_RightBranch,
    "ㅐ": BlockType.A_RightBranch,
    "ㅑ": BlockType.A_RightBranch,
    "ㅒ": BlockType.A_RightBranch,
    "ㅓ": BlockType.A_RightBranch,
    "ㅔ": BlockType.A_RightBranch,
    "ㅕ": BlockType.A_RightBranch,
    "ㅖ": BlockType.A_RightBranch,

    # --- B: top-branch (ㅗ family) ---
    "ㅗ": BlockType.B_TopBranch,
    "ㅘ": BlockType.B_TopBranch,
    "ㅙ": BlockType.B_TopBranch,
    "ㅚ": BlockType.B_TopBranch,
    "ㅛ": BlockType.B_TopBranch,

    # --- C: bottom-branch (ㅜ family) ---
    "ㅜ": BlockType.C_BottomBranch,
    "ㅝ": BlockType.C_BottomBranch,
    "ㅞ": BlockType.C_BottomBranch,
    "ㅠ": BlockType.C_BottomBranch,

    # --- D: horizontal / central ---
    "ㅡ": BlockType.D_Horizontal,
    "ㅣ": BlockType.D_Horizontal,
    "ㅢ": BlockType.D_Horizontal,
    "ㅟ": BlockType.D_Horizontal,

}


def block_type_for_pair(lead: str, vowel: str) -> BlockType:
    """Return a BlockType for a (leading consonant, vowel) jamo pair.

    This is pure domain logic. `lead` is currently unused (kept for future rules).
    """
    v = str(vowel)
    return VOWEL_TO_BLOCK.get(v, BlockType.D_Horizontal)
