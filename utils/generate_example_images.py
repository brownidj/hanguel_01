from __future__ import annotations

import argparse
import base64
import json
import os
import re
import time
import select
import sys
from pathlib import Path
from typing import Any
import ssl
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import yaml


DEFAULT_MODEL = "gpt-image-1"
DEFAULT_STYLE = (
    "Flat, clean illustration, centered object, consistent style, soft lighting, "
    "no text or labels, simple composition."
)
PASTEL_BACKGROUNDS = {
    "syllable": "very light pastel peach",
    "vowel": "very light pastel mint",
    "consonant": "very light pastel lavender",
}


def _slugify(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "example"


def _load_examples(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items = data.get("examples", [])
    if not isinstance(items, list):
        return []
    return items


def _save_examples(path: Path, items: list[dict[str, Any]]) -> None:
    data = {"examples": items}
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _build_prompt(image_prompt: str, *, background: str) -> str:
    base = image_prompt.strip().rstrip(".")
    return "{}. {} Pastel background color: {}.".format(base, DEFAULT_STYLE, background)


def _call_openai_image(prompt: str, *, api_key: str, model: str) -> bytes:
    print("[image] Requesting image...")
    payload = {
        "model": model,
        "prompt": prompt,
        "size": "1024x1024",
    }
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(api_key),
        },
        method="POST",
    )
    try:
        import certifi  # type: ignore
        context = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        context = ssl.create_default_context()
    try:
        with urlopen(req, timeout=480, context=context) as resp:
            raw = resp.read()
    except HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        raise RuntimeError(
            "OpenAI image request failed: {} {} payload={}".format(e.code, body, payload)
        )
    data = json.loads(raw.decode("utf-8"))
    first = data["data"][0]
    if "b64_json" in first:
        return base64.b64decode(first["b64_json"])
    if "url" in first:
        img_req = Request(first["url"], method="GET")
        with urlopen(img_req, timeout=480, context=context) as resp:
            return resp.read()
    raise RuntimeError("OpenAI image response missing image data")

def _maybe_abort() -> bool:
    try:
        if not sys.stdin.isatty():
            return False
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if rlist:
            line = sys.stdin.readline().strip().lower()
            return line == "q"
    except Exception:
        return False
    return False

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate example images via DALL-E.")
    parser.add_argument("--examples", default="flutter_app/assets/data/examples.yaml")
    parser.add_argument("--syllables", default="flutter_app/assets/data/syllables.yaml")
    parser.add_argument("--output-dir", default="flutter_app/assets/images/examples")
    parser.add_argument("--context", choices=["syllable", "vowel", "consonant"], default="syllable")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Max images to generate (0 = no limit).")
    parser.add_argument("--all", action="store_true", help="Ignore --limit and process all items.")
    parser.add_argument("--batch-size", type=int, default=10, help="Images per batch (0 = all).")
    parser.add_argument("--batch-index", type=int, default=1, help="1-based batch index to process.")
    parser.add_argument("--auto-batches", action="store_true", help="Run batches sequentially with pauses.")
    parser.add_argument("--batch-pause", type=int, default=10, help="Seconds to pause between batches.")
    args = parser.parse_args()

    examples_path = Path(args.examples)
    syllables_path = Path(args.syllables)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for image generation.")

    items = _load_examples(examples_path)
    if not items:
        print("No examples found in {}".format(examples_path))
        return 1
    syllables = yaml.safe_load(syllables_path.read_text(encoding="utf-8")) or {}
    syllable_glyphs = {
        s.get("glyph") for s in syllables.get("syllables", []) if isinstance(s, dict) and s.get("glyph")
    }

    background = PASTEL_BACKGROUNDS.get(args.context, PASTEL_BACKGROUNDS["syllable"])
    candidates: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        syllable = item.get("starts_with_syllable", "")
        if isinstance(syllable, str) and syllable_glyphs and syllable not in syllable_glyphs:
            continue
        filename = item.get("image_filename", "")
        if not isinstance(filename, str) or not filename.strip():
            continue
        out_path = output_dir / filename
        if out_path.exists() and not args.overwrite:
            continue
        candidates.append(item)

    total_missing = len(candidates)
    if total_missing == 0:
        print("All example images already exist in {}".format(output_dir))
        return 0

    if args.batch_size and args.batch_size > 0:
        batches = (total_missing + args.batch_size - 1) // args.batch_size
        batch_index = max(1, args.batch_index)
        if batch_index > batches:
            print("Batch index {} is out of range (1-{}).".format(batch_index, batches))
            return 1
        if args.auto_batches:
            start_batch = batch_index
        else:
            start_batch = batch_index
            batch_list = [(batch_index, batches)]
        if args.auto_batches:
            batch_list = [(idx, batches) for idx in range(start_batch, batches + 1)]
    else:
        batches = 1
        batch_index = 1
        batch_list = [(1, 1)]

    total_generated = 0
    for batch_index, batches in batch_list:
        if args.batch_size and args.batch_size > 0:
            start = (batch_index - 1) * args.batch_size
            end = min(start + args.batch_size, total_missing)
            batch_candidates = candidates[start:end]
        else:
            batch_candidates = candidates
        batch_total = len(batch_candidates)
        print("Processing batch {} of {} ({} items).".format(batch_index, batches, batch_total))
        generated = 0
        for item in batch_candidates:
            gloss = item.get("gloss_en", "")
            prompt = item.get("image_prompt", "")
            filename = item.get("image_filename", "")
            if not isinstance(gloss, str) or not gloss.strip():
                continue
            if not isinstance(prompt, str) or not prompt.strip():
                continue
            if not isinstance(filename, str) or not filename.strip():
                continue

            out_path = output_dir / filename
            full_prompt = _build_prompt(prompt, background=background)
            if args.dry_run:
                print("[dry-run] Would generate {} -> {}".format(gloss, out_path))
            else:
                if _maybe_abort():
                    print("[abort] Received 'q' - exiting.")
                    return 1
                print("[image] Generating '{}' -> {}".format(gloss, out_path))
                image_bytes = _call_openai_image(full_prompt, api_key=api_key, model=args.model)
                out_path.write_bytes(image_bytes)

            if not args.dry_run:
                generated += 1
                total_generated += 1
                print(
                    "Saved {} ({} of {}, batch {} of {})".format(
                        out_path, generated, batch_total, batch_index, batches
                    )
                )
            else:
                generated += 1
                total_generated += 1
            if not args.all and args.limit > 0 and total_generated >= args.limit:
                break
        if not args.all and args.limit > 0 and total_generated >= args.limit:
            break
        if args.auto_batches and batch_index < batches:
            print("Pausing {}s before next batch...".format(args.batch_pause))
            time.sleep(max(0, args.batch_pause))

    if args.dry_run:
        print("[dry-run] Skipping examples.yaml write")
    else:
        _save_examples(examples_path, items)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
