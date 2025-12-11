# tests/test_classification.py
import pytest

@pytest.mark.classification
def test_block_type_function_exposed(main_module):
    fn = getattr(main_module, "block_type_for_pair", None)
    assert callable(fn), "block_type_for_pair() must be exposed"

@pytest.mark.classification
@pytest.mark.parametrize("lead,vowel,starts_with", [
    ("ㄱ", "ㅏ", "A"), ("ㄴ", "ㅑ", "A"), ("ㅁ", "ㅐ", "A"),
    ("ㄱ", "ㅗ", "B"), ("ㄴ", "ㅛ", "B"), ("ㅁ", "ㅚ", "B"),  # ㅚ often top-branch in many layouts
    ("ㄱ", "ㅜ", "C"), ("ㄴ", "ㅠ", "C"), ("ㅁ", "ㅝ", "C"),
    ("ㄱ", "ㅣ", "D"), ("ㄴ", "ㅐ", "A"), ("ㅁ", "ㅟ", "D"),  # ㅟ typically vertical-ish
])
def test_block_type_basic_mapping(main_module, lead, vowel, starts_with):
    fn = getattr(main_module, "block_type_for_pair")
    result = fn(lead, vowel)
    name = getattr(result, "name", str(result))
    assert name.startswith(starts_with), f"{lead}+{vowel} expected {starts_with}*, got {name}"