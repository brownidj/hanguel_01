from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
import ssl


DEFAULT_MODEL = "gpt-4o-mini"
ALLOWED_POS = {
    "noun",
    "verb",
    "adjective",
    "adverb",
    "particle",
    "pronoun",
    "numeral",
    "interjection",
    "determiner",
    "other",
}


def _load_cache(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(path: Path, cache: dict[str, str]) -> None:
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _call_chatgpt(surface: str, gloss: str, *, api_key: str, model: str) -> str:
    system = (
        "You are labeling Korean lexemes with a single part-of-speech tag. "
        "Return only one token from this list: "
        "noun, verb, adjective, adverb, particle, pronoun, numeral, interjection, determiner, other."
    )
    user = f"Hangul: {surface}\nGloss: {gloss}\nPOS:"
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        import certifi  # type: ignore
        context = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        context = ssl.create_default_context()
    with urlopen(req, timeout=60, context=context) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"].strip().lower()
    return content


def _normalize_pos(raw: str) -> str:
    token = raw.strip().lower()
    token = token.replace(".", "")
    if token in ALLOWED_POS:
        return token
    if token in {"n", "nn", "noun"}:
        return "noun"
    if token in {"v", "verb"}:
        return "verb"
    if token in {"adj", "adjective"}:
        return "adjective"
    if token in {"adv", "adverb"}:
        return "adverb"
    if token in {"pron", "pronoun"}:
        return "pronoun"
    if token in {"num", "numeral"}:
        return "numeral"
    if token in {"det", "determiner"}:
        return "determiner"
    if token in {"part", "particle"}:
        return "particle"
    if token in {"int", "interjection"}:
        return "interjection"
    return "other"


def main() -> int:
    parser = argparse.ArgumentParser(description="Assign POS tags to kengdic.tsv entries using ChatGPT.")
    parser.add_argument("--input", default="flutter_app/assets/data/kengdic.tsv")
    parser.add_argument("--output", default="", help="Output TSV path (default: <input>.pos.tsv).")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--cache", default="utils/pos_cache.json")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY is required.", file=sys.stderr)
        return 1

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_suffix(".pos.tsv")
    cache_path = Path(args.cache)

    cache = _load_cache(cache_path)

    with input_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames or []
        if "pos" not in fieldnames:
            fieldnames.append("pos")

        rows = list(reader)

    end = len(rows) if args.limit == 0 else min(len(rows), args.start + args.limit)
    updated = 0
    for idx in range(args.start, end):
        row = rows[idx]
        surface = (row.get("surface") or "").strip()
        gloss = (row.get("gloss") or "").strip()
        key = f"{surface}|{gloss}"
        if not surface:
            continue
        if row.get("pos") and not args.overwrite:
            continue
        if key in cache:
            row["pos"] = cache[key]
            updated += 1
            continue

        raw_pos = _call_chatgpt(surface, gloss, api_key=api_key, model=args.model)
        pos = _normalize_pos(raw_pos)
        row["pos"] = pos
        cache[key] = pos
        updated += 1
        print(f"[{idx+1}/{end}] {surface} -> {pos}")
        time.sleep(max(0.0, args.sleep))

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    _save_cache(cache_path, cache)
    print(f"Wrote {output_path} ({updated} updated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
