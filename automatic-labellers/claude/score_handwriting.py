#!/usr/bin/env python3
"""
Handwriting Quality Batch Scorer
---------------------------------
Scores handwriting images using Claude's vision API.
Outputs a CSV with per-dimension scores and an overall rating.

Usage:
    python score_handwriting.py --input ./images --output results.csv
    python score_handwriting.py --input ./images --output results.csv --workers 5
    python score_handwriting.py --input ./images --output results.csv --resume

Supported image formats: JPEG, PNG, GIF, WebP
"""

import io
import anthropic
import base64
import csv
import json
import mimetypes
import os
import sys
import time
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime
from PIL import Image

# ── Configuration ────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 512
MAX_WORKERS = 3          # concurrent API calls; raise cautiously to avoid rate limits
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5          # seconds between retries
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

SYSTEM_PROMPT = """You are an expert handwriting analyst. Your job is to assess the quality
of handwritten English text (which may be printed, cursive, or mixed) from images.
You must always respond with valid JSON — no prose, no markdown fences."""

SCORING_PROMPT = """Assess the handwriting quality in this image and return ONLY a JSON object
with the following fields. Use integer scores from 1 (very poor) to 10 (excellent).

{
  "overall": <1-10>,
  "legibility": <1-10>,
  "letter_consistency": <1-10>,
  "line_alignment": <1-10>,
  "spacing": <1-10>,
  "script_type": "<printed|cursive|mixed|unclear>",
  "notes": "<one sentence observation, or empty string>"
}

Scoring rubric:
- overall: holistic quality; a reader's first impression
- legibility: how easily the text can be read by an unfamiliar reader
- letter_consistency: uniformity of letter size, shape, and slant
- line_alignment: how well text follows an imaginary baseline
- spacing: consistency of space between letters and words
- script_type: dominant style observed

Score on a 1-10 scale where:
1-3 = poor (hard to read, inconsistent, sloppy)
4-6 = average (readable but unremarkable)
7-8 = good (clear, consistent, pleasing)
9-10 = exceptional (near-professional quality)
Reserve 5 for truly average handwriting. Actively use the full range.

Return ONLY the JSON object. No explanation, no markdown."""

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Core scoring function ─────────────────────────────────────────────────────

def encode_image(path: Path) -> tuple[str, str]:
    """Return (base64_data, media_type) for an image file."""
    # media_type, _ = mimetypes.guess_type(str(path))
    # if media_type not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
    #     # fallback for .jpg not caught by mimetypes on some systems
    #     ext = path.suffix.lower()
    #     media_type = "image/jpeg" if ext in (".jpg", ".jpeg") else f"image/{ext.lstrip('.')}"

    with Image.open(path) as img:
        img = img.convert("RGB")
        # Resize if either dimension exceeds 2000px (keeps well under 5MB)
        img.thumbnail((1500, 1500), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        data = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

    # with open(path, "rb") as f:
    #     data = base64.standard_b64encode(f.read()).decode("utf-8")

    return data, "image/jpeg"


def score_image(client: anthropic.Anthropic, image_path: Path) -> dict:
    """Score a single image. Returns a result dict (includes error field on failure)."""
    base_result = {"filename": image_path.name, "filepath": str(image_path)}

    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            data, media_type = encode_image(image_path)

            message = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": data,
                                },
                            },
                            {"type": "text", "text": SCORING_PROMPT},
                        ],
                    }
                ],
            )

            raw = message.content[0].text.strip()

            # Strip accidental markdown fences if model adds them
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            scores = json.loads(raw)
            return {**base_result, **scores, "error": ""}

        except json.JSONDecodeError as e:
            log.warning(f"[{image_path.name}] JSON parse error (attempt {attempt}): {e}")
            if attempt == RETRY_ATTEMPTS:
                return {**base_result, "error": f"JSON parse failed: {e}"}
            time.sleep(RETRY_DELAY)

        except anthropic.RateLimitError:
            wait = RETRY_DELAY * attempt
            log.warning(f"[{image_path.name}] Rate limited, waiting {wait}s (attempt {attempt})")
            time.sleep(wait)

        except anthropic.APIError as e:
            log.warning(f"[{image_path.name}] API error (attempt {attempt}): {e}")
            if attempt == RETRY_ATTEMPTS:
                return {**base_result, "error": str(e)}
            time.sleep(RETRY_DELAY)

        except Exception as e:
            return {**base_result, "error": str(e)}

    return {**base_result, "error": "Max retries exceeded"}


# ── CSV helpers ───────────────────────────────────────────────────────────────

FIELDNAMES = [
    "filename", "filepath",
    "overall", "legibility", "letter_consistency",
    "line_alignment", "spacing",
    "script_type", "notes", "error",
]


def load_already_scored(output_path: Path) -> set[str]:
    """Return set of filenames already present in the output CSV."""
    done = set()
    if output_path.exists():
        with open(output_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("filename"):
                    done.add(row["filename"])
    return done


def write_row(writer, row: dict):
    """Write a single result row, filling missing fields with empty strings."""
    writer.writerow({k: row.get(k, "") for k in FIELDNAMES})


# ── Main ──────────────────────────────────────────────────────────────────────

def collect_images(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    images = sorted(
        p for p in input_path.rglob("*")
        if p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return images


def run(args):
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        log.error(f"Input path does not exist: {input_path}")
        sys.exit(1)

    images = collect_images(input_path)
    if not images:
        log.error(f"No supported images found in: {input_path}")
        sys.exit(1)

    log.info(f"Found {len(images)} image(s) in {input_path}")

    # Resume support: skip already-scored files
    already_done: set[str] = set()
    if args.resume and output_path.exists():
        already_done = load_already_scored(output_path)
        log.info(f"Resuming — {len(already_done)} already scored, skipping those")

    to_process = [img for img in images if img.name not in already_done]
    log.info(f"Images to score: {len(to_process)}")

    if not to_process:
        log.info("Nothing to do.")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error("ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Open CSV (append if resuming, write fresh otherwise)
    file_mode = "a" if args.resume and output_path.exists() else "w"
    write_header = file_mode == "w" or not output_path.exists()

    completed = 0
    errors = 0
    start_time = time.time()

    with open(output_path, file_mode, newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(score_image, client, img): img for img in to_process}

            for future in as_completed(futures):
                img = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    result = {"filename": img.name, "filepath": str(img), "error": str(e)}

                write_row(writer, result)
                csvfile.flush()  # write immediately so progress survives interruption

                completed += 1
                if result.get("error"):
                    errors += 1
                    log.warning(f"[{result['filename']}] ERROR: {result['error']}")
                else:
                    log.info(
                        f"[{completed}/{len(to_process)}] {result['filename']} "
                        f"→ overall={result.get('overall','?')} "
                        f"legibility={result.get('legibility','?')} "
                        f"type={result.get('script_type','?')}"
                    )

    elapsed = time.time() - start_time
    log.info(
        f"Done. {completed} processed ({errors} errors) in {elapsed:.1f}s. "
        f"Results saved to: {output_path}"
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch handwriting quality scorer using Claude vision API."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to image file or directory of images"
    )
    parser.add_argument(
        "--output", "-o", default="handwriting_scores.csv",
        help="Output CSV file path (default: handwriting_scores.csv)"
    )
    parser.add_argument(
        "--workers", "-w", type=int, default=MAX_WORKERS,
        help=f"Concurrent API workers (default: {MAX_WORKERS}). Keep low to avoid rate limits."
    )
    parser.add_argument(
        "--resume", "-r", action="store_true",
        help="Skip images already present in the output CSV (safe to restart after interruption)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
