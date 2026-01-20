from enum import Enum


class BlockType(Enum):
    A_RightBranch = 1
    B_TopBranch = 2
    C_BottomBranch = 3
    D_Horizontal = 4


VOWEL_TO_BLOCK = {
    "ㅏ": BlockType.A_RightBranch,
    "ㅐ": BlockType.A_RightBranch,
    "ㅑ": BlockType.A_RightBranch,
    "ㅒ": BlockType.A_RightBranch,
    "ㅓ": BlockType.B_TopBranch,
    "ㅔ": BlockType.B_TopBranch,
    "ㅕ": BlockType.B_TopBranch,
    "ㅖ": BlockType.B_TopBranch,
    "ㅗ": BlockType.B_TopBranch,
    "ㅛ": BlockType.B_TopBranch,
    "ㅜ": BlockType.C_BottomBranch,
    "ㅠ": BlockType.C_BottomBranch,
    "ㅡ": BlockType.C_BottomBranch,
    "ㅣ": BlockType.D_Horizontal,
    "ㅟ": BlockType.D_Horizontal,
}
