from __future__ import annotations

from app.controllers.examples_repository import ExamplesRepository
from app.controllers.examples_selector import ExamplesSelector


def test_examples_repository_indices() -> None:
    repo = ExamplesRepository()
    assert repo.by_syllable("가")
    assert repo.by_consonant("ㄱ")
    assert repo.by_vowel("ㅏ")
    items = repo.by_vowel("ㅏ")
    assert any(item.starts_with_syllable.startswith("아") for item in items)


def test_examples_selector_modes() -> None:
    repo = ExamplesRepository()

    def _mode_vowels() -> str:
        return "Vowels"

    def _mode_consonants() -> str:
        return "Consonants"

    def _mode_syllables() -> str:
        return "Syllables"

    def _pair_ga() -> tuple[str, str]:
        return ("ㄱ", "ㅏ")

    def _pair_vowel_a() -> tuple[str, str]:
        return ("∅", "ㅏ")

    def _index() -> int:
        return 0

    selector = ExamplesSelector(
        get_mode_text=_mode_syllables,
        get_current_pair=_pair_ga,
        get_current_index=_index,
        repository=repo,
    )
    item = selector.pick_example()
    assert item is not None
    assert item.starts_with_syllable == "가"

    selector = ExamplesSelector(
        get_mode_text=_mode_consonants,
        get_current_pair=_pair_ga,
        get_current_index=_index,
        repository=repo,
    )
    item = selector.pick_example()
    assert item is not None
    assert item.starts_with_consonant == "ㄱ"

    selector = ExamplesSelector(
        get_mode_text=_mode_vowels,
        get_current_pair=_pair_vowel_a,
        get_current_index=_index,
        repository=repo,
    )
    item = selector.pick_example()
    assert item is not None
    assert item.starts_with_vowel == "ㅏ"
