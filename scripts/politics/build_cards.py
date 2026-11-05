"""Turn the extracted point cards into small, recall-friendly study cards."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public" / "politics" / "data"

YEAR_RE = re.compile(r"(?:18|19|20)\d{2}")
COLOR_TONES = {"key", "warm", "blue", "purple", "green"}


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def keywords_of(blocks: list[dict]) -> list[str]:
    seen: list[str] = []
    for block in blocks:
        for span in block.get("spans", []):
            text = span.get("text", "").strip()
            if span.get("tone") in COLOR_TONES and len(text) >= 2 and text not in seen:
                seen.append(text)
    return seen[:14]


def hint_of(point: dict, part: str = "") -> str:
    bits = [point["sectionName"], f"第 {point['page']} 页"]
    if point.get("topic"):
        bits.append(point["topic"])
    if part:
        bits.append(f"第 {part} 段")
    return " · ".join(bits)


def make_card(point: dict, *, card_id: str, title: str, prompt: str, blocks: list[dict], kind: str,
              part: str = "", figure: str | None = None, figure_alt: str = "",
              figure_caption: str = "") -> dict:
    return {
        "id": card_id,
        "pointId": point["id"],
        "title": title,
        "pointTitle": point["title"],
        "section": point["section"],
        "sectionName": point["sectionName"],
        "topic": point.get("topic") or "",
        "page": point["page"],
        "kind": kind,
        "prompt": prompt,
        "part": part,
        "hint": hint_of(point, part),
        "blocks": blocks,
        "keywords": keywords_of(blocks),
        "figure": figure,
        "figureAlt": figure_alt,
        "figureCaption": figure_caption,
    }


def is_meeting_heading(text: str) -> bool:
    text = text.strip()
    return (
        0 < len(text) <= 60
        and bool(YEAR_RE.search(text))
        and "。" not in text
        and not text.startswith(("(", "（"))
    )


def merge_heading_fragments(blocks: list[dict]) -> list[dict]:
    """A long heading can be split into two PDF blocks (e.g. 《决 / 议》）1981)."""
    merged: list[dict] = []
    for block in blocks:
        text = block["text"].strip()
        if (
            merged
            and 0 < len(text) <= 12
            and text.startswith(("议》", "》", "）"))
            and "《" in merged[-1]["text"]
            and not merged[-1]["text"].endswith(("》", "）"))
        ):
            merged[-1] = {
                "text": merged[-1]["text"] + text,
                "spans": merged[-1]["spans"] + block["spans"],
            }
        else:
            merged.append(block)
    return merged


def meeting_cards(point: dict) -> list[dict]:
    blocks = merge_heading_fragments(point.get("blocks", []))
    starts = [i for i, block in enumerate(blocks) if is_meeting_heading(block["text"])]
    if not starts:
        return []

    cards: list[dict] = []
    if starts[0] > 0:
        starts.insert(0, 0)
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(blocks)
        head = blocks[start]["text"].strip()
        detail = blocks[start + 1 : end]
        if not detail:
            continue
        # A single meeting can have 15–20 detail blocks; split it so one card
        # never becomes an unreadable wall of text.
        parts = 1 if len(detail) <= 10 else math.ceil(len(detail) / 8)
        size = math.ceil(len(detail) / parts)
        for part_index in range(parts):
            part_blocks = detail[part_index * size : (part_index + 1) * size]
            if not part_blocks:
                continue
            part = f"{part_index + 1}/{parts}" if parts > 1 else ""
            cards.append(
                make_card(
                    point,
                    card_id=(
                        f"p{point['id']}-m{index + 1}"
                        if parts == 1
                        else f"p{point['id']}-m{index + 1}-{part_index + 1}"
                    ),
                    title=head,
                    prompt=head,
                    blocks=part_blocks,
                    kind="meeting",
                    part=part,
                )
            )
    return cards


def mnemonic_cards(point: dict) -> list[dict]:
    blocks = point.get("blocks", [])
    if not blocks:
        return []
    chunk = 7
    total = math.ceil(len(blocks) / chunk)
    cards = []
    for index in range(total):
        part_blocks = blocks[index * chunk : (index + 1) * chunk]
        part = f"{index + 1}/{total}"
        cards.append(
            make_card(
                point,
                card_id=f"p{point['id']}-{index + 1}",
                title=point["title"],
                prompt=f"会议口诀 · 第 {part} 段",
                blocks=part_blocks,
                kind="mnemonic",
                part=part,
            )
        )
    return cards


def point_cards(point: dict) -> list[dict]:
    if point["id"] == "037":
        return [
            make_card(
                point,
                card_id="p037-figure",
                title=point["title"],
                prompt="史纲整体脉络：按时间顺序说出三个革命阶段，以及国情和历史时期的变化。",
                blocks=[],
                kind="figure",
                figure="figures/timeline.png",
                figure_alt="1840 到 1978 年中国革命、国情与历史时期的时间轴",
                figure_caption="1840–1978 史纲整体脉络",
            )
        ]

    if point["id"] == "091":
        return mnemonic_cards(point)

    if point["id"] in {"092", "093", "094"}:
        cards = meeting_cards(point)
        if cards:
            return cards

    blocks = point.get("blocks", [])
    if not blocks:
        return []

    count = len(blocks)
    parts = 1 if count <= 8 else math.ceil(count / 8)
    size = math.ceil(count / parts)
    cards = []
    for index in range(parts):
        part_blocks = blocks[index * size : (index + 1) * size]
        if not part_blocks:
            continue
        part = f"{index + 1}/{parts}" if parts > 1 else ""
        cards.append(
            make_card(
                point,
                card_id=f"p{point['id']}" if parts == 1 else f"p{point['id']}-{index + 1}",
                title=point["title"],
                prompt=point["title"],
                blocks=part_blocks,
                kind="point",
                part=part,
            )
        )
    return cards


def main() -> None:
    points = load_json("points.json")
    cards: list[dict] = []
    for point in points:
        cards.extend(point_cards(point))

    # Keep source order: points run 001→100 and each point's parts are
    # appended in reading order, which is exactly the study order.
    for index, card in enumerate(cards):
        card["seq"] = index

    (DATA / "cards.json").write_text(
        json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    meta = load_json("meta.json")
    meta["cardCount"] = len(cards)
    (DATA / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    counts: dict[str, int] = {}
    kinds: dict[str, int] = {}
    for card in cards:
        counts[card["sectionName"]] = counts.get(card["sectionName"], 0) + 1
        kinds[card["kind"]] = kinds.get(card["kind"], 0) + 1
    print(f"cards: {len(cards)}")
    print("by section:", counts)
    print("by kind:", kinds)
    for card in cards:
        if card["pointId"] in {"092", "093", "094"}:
            print(card["id"], card["title"], len(card["blocks"]))


if __name__ == "__main__":
    main()
