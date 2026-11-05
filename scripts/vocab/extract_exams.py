#!/usr/bin/env python3
"""Extract clean English prose sentences from 2010-2026 NETEM exam PDFs.

Usage:
  python scripts/vocab/extract_exams.py \
      --pdf-dir .cache/vocab/pdfs \
      --out .cache/vocab/exams.json

Requires pypdf. The generated exams.json is a build-time input for
scripts/vocab/build-data.mjs and is not shipped as-is.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - helpful message for local runs
    sys.exit(
        "pypdf is required. Install it with:\n"
        "  python -m pip install pypdf\n"
        "or point PYTHONPATH at a local pypdf install."
    )

# ---------------------------------------------------------------------------
# Text cleanup
# ---------------------------------------------------------------------------

REPLACEMENT = "\ufffd"


def clean_page(text: str) -> str:
    """Drop page furniture and lines that are mostly CJK / broken glyphs."""
    kept: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.fullmatch(r"[-–—]?\s*\d{1,3}\s*[-–—]?", line):
            continue
        non_ascii = sum(1 for ch in line if ord(ch) > 127)
        if non_ascii / max(len(line), 1) > 0.28:
            continue
        kept.append(line)
    return "\n".join(kept)


def normalize(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = (
        text.replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .replace("–", "-")
        .replace("—", "-")
        .replace("…", "...")
    )
    # pypdf renders smart quotes as U+FFFD pairs. Decide by context.
    text = re.sub(rf"(?<=[A-Za-z]){REPLACEMENT}+(?=[A-Za-z])", "'", text)
    text = re.sub(rf"{REPLACEMENT}+", '"', text)
    # De-hyphenate words broken across lines.
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def strip_directions(body: str) -> str:
    """Remove the instruction block that always ends with (N points)."""
    body = re.sub(
        r"^.*?\(\s*\d+\s*points?\s*\)\s*",
        "",
        body,
        count=1,
        flags=re.S | re.I,
    )
    body = re.sub(r"^.*?ANSWER\s+SHEET[^.]*\.\s*", "", body, count=1, flags=re.I)
    return body


# ---------------------------------------------------------------------------
# Sentence splitting
# ---------------------------------------------------------------------------

ABBREVIATIONS = {
    "mr",
    "mrs",
    "ms",
    "dr",
    "prof",
    "st",
    "vs",
    "etc",
    "e.g",
    "i.e",
    "u.s",
    "u.k",
    "no",
    "fig",
    "al",
    "inc",
    "ltd",
    "co",
    "jr",
    "sr",
}


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    merged: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if merged:
            prev = merged[-1]
            prev_tail = re.sub(r"[\"')\]]+$", "", prev).split(" ")[-1].lower()
            next_head = part.lstrip("\"'([")
            if (
                next_head[:1].islower()
                or prev_tail.rstrip(".") in ABBREVIATIONS
                or re.fullmatch(r"[A-Z]", prev_tail.rstrip("."))
            ):
                merged[-1] = f"{prev} {part}"
                continue
        merged.append(part)
    return merged


BAD_SENTENCE = re.compile(
    r"^(?:"
    r"[A-D]\.\s|"
    r"\d{1,2}\.\s|"
    r"Directions?\s*[:;]|"
    r"Part\s+[A-C]\b|"
    r"Section\s+[IVX]+|"
    r"Text\s+\d|"
    r"Which of the following|"
    r"It can be (?:learned|inferred|concluded)|"
    r"The author(?:'s)? (?:attitude|purpose|view)|"
    r"According to (?:Paragraph|the author|the text)|"
    r"In Paragraph \d|"
    r"The word .{1,30} (?:refers to|is closest in meaning)|"
    r"The phrase .{1,40} (?:refers to|is closest in meaning)|"
    r"Write (?:your|an) (?:answer|essay)|"
    r"You should (?:write|not)|"
    r"Do not (?:sign|use|write)|"
    r"ANSWER SHEET|"
    r"\(\s*\d+\s*points?\s*\)"
    r")",
    re.I,
)


def is_useful(sentence: str) -> bool:
    s = sentence.strip().strip('"').strip()
    if len(s) < 45 or len(s) > 420:
        return False
    if "____" in s or "___" in s:
        return False
    if BAD_SENTENCE.search(s):
        return False
    # Drop option runs such as "A. foo B. bar C. baz D. qux".
    if len(re.findall(r"(?:^|\s)[A-D]\.\s", s)) >= 2:
        return False
    letters = sum(ch.isalpha() for ch in s)
    if letters / max(len(s), 1) < 0.55:
        return False
    if not re.search(r"[A-Za-z]{3}", s):
        return False
    return True


# ---------------------------------------------------------------------------
# Section extraction
# ---------------------------------------------------------------------------


def find(text: str, pattern: str, start: int = 0) -> int:
    match = re.search(pattern, text[start:], re.I)
    return start + match.start() if match else -1


def add_section(
    out: list[dict],
    body: str,
    *,
    year: int,
    paper: int,
    section: str,
    source: str,
) -> None:
    body = normalize(strip_directions(body))
    for sentence in split_sentences(body):
        if is_useful(sentence):
            out.append(
                {
                    "y": year,
                    "p": paper,
                    "sec": section,
                    "src": source,
                    "text": sentence.strip().strip('"').strip(),
                }
            )


def extract_paper(path: Path, year: int, paper: int) -> list[dict]:
    reader = PdfReader(str(path))
    pages = [clean_page(page.extract_text() or "") for page in reader.pages]
    text = normalize("\n".join(pages))

    out: list[dict] = []

    # Headings are unreliable across PDFs: "Section II" sometimes loses its
    # numeral or the words "Reading Comprehension", and OCR turns III into "ill".
    # Anchor on the features that survive: Use of English, Part A/B/C, Text N,
    # and the Writing heading.
    s1 = find(text, r"Use\s+of\s+English")
    if s1 < 0:
        s1 = find(text, r"Section\s*I\b")
    if s1 < 0:
        s1 = 0

    text1 = find(text, r"Text\s*1\b", s1 + 1)
    part_a = find(text, r"Part\s*A\b", s1 + 1)
    # In 2021 English II the "Part A" heading is missing, so the first match is
    # the writing task. Text 1 is the reliable anchor there.
    if part_a < 0 or (text1 > 0 and part_a > text1):
        part_a = text1 if text1 > 0 else s1

    s2 = find(text, r"Section\s*II\b", s1 + 1)
    cloze_end_candidates = [
        p for p in (s2, part_a if part_a > s1 else -1, text1) if p > s1
    ]
    cloze_end = min(cloze_end_candidates) if cloze_end_candidates else len(text)
    body = text[s1:cloze_end]
    body = re.split(r"\b1\.\s*A\.\s", body, maxsplit=1, flags=re.I)[0]
    add_section(
        out, body, year=year, paper=paper, section="完形", source="Use of English"
    )

    part_b = find(text, r"Part\s*B\b", part_a + 1) if part_a > 0 else -1
    part_c = find(text, r"Part\s*C\b", part_a + 1) if part_a > 0 else -1
    section3 = find(text, r"Section\s*(?:III|Ill|IIl|111)\b", part_a + 1)
    # English II's translation heading sometimes loses its numeral entirely.
    if paper == 2 and section3 < 0:
        section3 = find(text, r"\bTranslation\b", part_a + 1)

    # The writing section is the hard stop for all reading sections. Search
    # after the last reading/translation anchor, never from the top of the paper.
    anchors = [p for p in (part_a, part_b, part_c, section3, text1) if p > 0]
    anchor = max(anchors) if anchors else s1
    writing = find(text, r"\bWriting\b", anchor)
    writing = writing if writing > 0 else len(text)
    if section3 > writing:
        section3 = -1

    reading_end_candidates = [p for p in (part_b, part_c, section3, writing) if p > 0]
    reading_end = min(reading_end_candidates) if reading_end_candidates else len(text)

    # --- Reading Part A ----------------------------------------------------------
    text_starts: list[tuple[int, str]] = []
    for idx in range(1, 5):
        pos = find(text, rf"Text\s*{idx}\b", part_a)
        if pos >= 0 and pos < reading_end:
            text_starts.append((pos, f"Text {idx}"))
    text_starts.sort()

    for i, (pos, label) in enumerate(text_starts):
        next_text = text_starts[i + 1][0] if i + 1 < len(text_starts) else reading_end
        body = text[pos + len(label) : next_text]
        # Questions begin at 21/26/31/36. Cut before the first matching question.
        numbers = [21, 26, 31, 36]
        if i < len(numbers):
            q = find(body, rf"\b{numbers[i]}\.\s+[A-Z]")
            if 0 <= q < len(body):
                body = body[:q]
        add_section(
            out,
            body,
            year=year,
            paper=paper,
            section="阅读",
            source=label,
        )

    # --- Part B / new type -------------------------------------------------------
    if part_b > 0:
        end_candidates = [p for p in (part_c, section3, writing) if p > part_b]
        end = min(end_candidates) if end_candidates else len(text)
        add_section(
            out,
            text[part_b:end],
            year=year,
            paper=paper,
            section="新题型",
            source="Part B",
        )

    # --- Part C / translation ----------------------------------------------------
    if paper == 1 and part_c > 0:
        end_candidates = [p for p in (section3, writing) if p > part_c]
        end = min(end_candidates) if end_candidates else len(text)
        add_section(
            out,
            text[part_c:end],
            year=year,
            paper=paper,
            section="翻译",
            source="Part C",
        )

    if paper == 2 and section3 > 0:
        section4 = find(text, r"Section\s*(?:IV|1V|IY)\b", section3 + 1)
        end = section4 if section3 < section4 < writing else writing
        add_section(
            out,
            text[section3:end],
            year=year,
            paper=paper,
            section="翻译",
            source="Section III",
        )

    # --- Deduplicate -------------------------------------------------------------
    seen: set[str] = set()
    unique: list[dict] = []
    for item in out:
        key = re.sub(r"\W+", "", item["text"].lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-dir", default=".cache/vocab/pdfs")
    parser.add_argument("--out", default=".cache/vocab/exams.json")
    args = parser.parse_args()

    pdf_dir = Path(args.pdf_dir)
    files = sorted(pdf_dir.glob("*.pdf"))
    if not files:
        sys.exit(f"No PDFs found in {pdf_dir}")

    all_sentences: list[dict] = []
    for path in files:
        match = re.fullmatch(r"(\d{4})-([12])", path.stem)
        if not match:
            continue
        year, paper = int(match.group(1)), int(match.group(2))
        try:
            sentences = extract_paper(path, year, paper)
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"WARN {path.name}: {exc}", file=sys.stderr)
            continue
        all_sentences.extend(sentences)
        by_sec: dict[str, int] = {}
        for item in sentences:
            by_sec[item["sec"]] = by_sec.get(item["sec"], 0) + 1
        print(f"{year}-{paper}: {len(sentences):4d}  {by_sec}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(all_sentences, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"\nWrote {len(all_sentences)} sentences to {out_path}")


if __name__ == "__main__":
    main()
