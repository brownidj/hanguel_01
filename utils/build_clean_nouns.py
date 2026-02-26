#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import yaml
import re


# -----------------------------
# Paths (explicit and stable)
# -----------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
        PROJECT_ROOT
        / "flutter_app"
        / "assets"
        / "data"
        / "nouns.txt"
)

OUTPUT_PATH = (
        PROJECT_ROOT
        / "flutter_app"
        / "assets"
        / "data"
        / "clean_nouns.yaml"
)


# -----------------------------
# Helpers
# -----------------------------

# Hangul syllables only (가–힣)
HANGUL_RE = re.compile(r"^[가-힣]+$")


def load_nouns(path: Path) -> list[str]:
    nouns: set[str] = set()

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            word = line.strip()

            if not word:
                continue

            # Keep only pure Hangul nouns
            if not HANGUL_RE.match(word):
                continue

            nouns.add(word)

    return sorted(nouns)


def write_yaml(words: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            words,
            f,
            allow_unicode=True,
            sort_keys=False,
        )


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    nouns = load_nouns(INPUT_PATH)
    write_yaml(nouns, OUTPUT_PATH)

    print(f"✓ Wrote {len(nouns)} nouns to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()