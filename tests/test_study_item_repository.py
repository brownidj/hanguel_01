from pathlib import Path

from app.controllers.main_window_controller import StudyItemRepository


def test_repo_fallback_when_no_data_dir(tmp_path: Path) -> None:
    repo = StudyItemRepository(project_root=tmp_path)
    pairs = repo.pairs_for_mode("Syllables")
    assert pairs, "Expected non-empty fallback pairs"
    assert pairs[0] == ("ㄱ", "ㅏ")


def test_repo_consonants_mode_returns_pairs_with_empty_vowel(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "consonants.yaml").write_text(
        "- glyph: ㄱ\n- glyph: ㄴ\n", encoding="utf-8"
    )

    repo = StudyItemRepository(project_root=tmp_path)
    pairs = repo.pairs_for_mode("Consonants")

    assert pairs == [("ㄱ", "∅"), ("ㄴ", "∅")]


def test_repo_vowels_mode_returns_pairs_with_empty_consonant(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "vowels.yaml").write_text(
        "- glyph: ㅏ\n- glyph: ㅑ\n", encoding="utf-8"
    )

    repo = StudyItemRepository(project_root=tmp_path)
    pairs = repo.pairs_for_mode("Vowels")

    assert pairs == [("∅", "ㅏ"), ("∅", "ㅑ")]


def test_repo_syllables_mode_extracts_cv_pairs_from_compact_strings(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "syllables.yaml").write_text(
        "- \"ㄱㅏ\"\n- \"ㄴㅏ\"\n", encoding="utf-8"
    )

    repo = StudyItemRepository(project_root=tmp_path)
    pairs = repo.pairs_for_mode("Syllables")

    assert pairs == [("ㄱ", "ㅏ"), ("ㄴ", "ㅏ")]