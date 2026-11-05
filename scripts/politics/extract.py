"""Extract the 100 knowledge points from the 一页纸 PDF.

The PDF is a two-column card layout.  We use PyMuPDF's card rectangles to keep
each card together, then preserve the coloured spans so the study UI can show
the same "look at the coloured words" cue as the paper booklet.

Usage:
    python scripts/politics/extract.py [path-to-pdf]
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import pymupdf


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public" / "politics" / "data"
FIGURES = OUT / "figures"

DEFAULT_PDF = Path.home() / "Desktop" / "27考研政治一页纸-知识点手册.pdf"
CONTENT_PAGES = range(11, 36)

SECTIONS = [
    ("mayuan", "马原", 11, 17, "#b07a2a"),
    ("shigang", "史纲", 18, 27, "#c25b5b"),
    ("maozhongte", "毛中特", 28, 30, "#8a5bb5"),
    ("meetings", "会议大观", 31, 34, "#5b7fb5"),
    ("other", "其他", 35, 35, "#3f8f6b"),
]

TOPIC_WORDS = {
    "基本知识",
    "早期",
    "中特",
    "新时代",
    "法治",
    "会议大观",
}

# Colours as stored in the PDF (sRGB integers).
TONE_BY_COLOR = {
    0: "plain",
    9982492: "muted",       # brown page/section label
    5592405: "muted",
    6118749: "muted",
    11184810: "muted",
    16711680: "key",        # red
    13721686: "key",
    12402495: "key",
    2579409: "key",
    16736256: "warm",       # orange
    40959: "blue",
    8388863: "purple",
    9849417: "purple",
    1540932: "green",
    16639: "green",
}

CARD_MIN_W = 150
CARD_MIN_H = 40
BULLET_RE = re.compile(r"^(?:\(?\d+\)?[.、]|[（(][一二三四五六七八九十]+[）)]|[一二三四五六七八九十]+、|[✅❌⚠️]|【|\[|[-•])")
MEETING_RE = re.compile(
    r"^(?:中共|国民党|八七|古田|遵义|瓦窑堡|洛川|六届|七大|七届|人民政协|八大|十一|十二|十三|十四|十五|十六|十七|十八|《|关于真理)"
)

# The booklet is a list of short A→B facts.  Lines beginning with one of these
# subjects are new facts unless the previous line is an unfinished prompt.
SUBJECT_PREFIXES = (
    "马克思主义",
    "马克思",
    "政治上层建筑",
    "观念上层建筑",
    "实践",
    "物质",
    "意识",
    "人的本质",
    "社会",
    "资本",
    "剩余价值",
    "科学",
    "发展",
    "推动",
    "构建",
    "全面",
    "法律",
    "宪法",
    "立法",
    "行政",
    "司法",
    "普遍",
    "优先",
    "不可",
    "高质量",
    "中共",
    "国民党",
    "八七",
    "古田",
    "遵义",
    "瓦窑堡",
    "洛川",
    "六届",
    "七大",
    "七届",
    "人民政协",
    "八大",
    "十一",
    "十二",
    "十三",
    "十四",
    "十五",
    "十六",
    "十七",
    "十八",
    "《",
    "关于真理",
)


def section_for(page_no: int):
    for key, name, start, end, color in SECTIONS:
        if start <= page_no <= end:
            return key, name, color
    return "other", "其他", "#3f8f6b"


def tone_of(color: int) -> str:
    return TONE_BY_COLOR.get(color, "plain")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\u00a0", " ")).strip()


def is_page_furniture(line: dict) -> bool:
    text = line["text"]
    y = line["y"]
    if y < 50 or y > 800:
        return True
    if text in {"澄潇宇一页纸", "知识点手册"}:
        return True
    if re.fullmatch(r"\d{2}", text) and line["x"] > 500:
        return True
    return False


def read_lines(page) -> list[dict]:
    """Return visual lines, preserving span colours and positions."""
    lines = []
    raw = page.get_text("dict")
    for block in raw["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            spans = []
            for span in line["spans"]:
                text = span["text"].replace("\u00a0", " ")
                if not text:
                    continue
                spans.append(
                    {
                        "text": text,
                        "tone": tone_of(int(span["color"])),
                        "color": int(span["color"]),
                        "size": round(float(span["size"]), 2),
                    }
                )
            if not spans:
                continue
            text = clean_text("".join(span["text"] for span in spans))
            if not text:
                continue
            bbox = line["bbox"]
            lines.append(
                {
                    "text": text,
                    "spans": spans,
                    "x": float(bbox[0]),
                    "y": float(bbox[1]),
                    "x1": float(bbox[2]),
                    "y1": float(bbox[3]),
                    "size": max(float(span["size"]) for span in spans),
                }
            )
    return lines


def inside_card(line: dict, rect) -> bool:
    cx = (line["x"] + line["x1"]) / 2
    cy = (line["y"] + line["y1"]) / 2
    return rect.x0 - 2 <= cx <= rect.x1 + 2 and rect.y0 - 2 <= cy <= rect.y1 + 2


def merge_rows(lines: list[dict]) -> list[dict]:
    """Group text fragments that sit on the same visual row (e.g. an emoji)."""
    rows: list[dict] = []
    for line in sorted(lines, key=lambda item: (item["y"], item["x"])):
        target = None
        for row in rows:
            if abs(row["y"] - line["y"]) <= 2.5:
                target = row
                break
        if target is None:
            rows.append(
                {
                    "y": line["y"],
                    "x": line["x"],
                    "x1": line["x1"],
                    "y1": line["y1"],
                    "size": line["size"],
                    "spans": list(line["spans"]),
                }
            )
        else:
            target["spans"].extend(line["spans"])
            target["x"] = min(target["x"], line["x"])
            target["x1"] = max(target["x1"], line["x1"])
            target["y1"] = max(target["y1"], line["y1"])
            target["size"] = max(target["size"], line["size"])

    for row in rows:
        # Deduplicate identical adjacent fragments, then rebuild text.
        merged = []
        for span in row["spans"]:
            text = span["text"].replace("\u00a0", " ")
            if not text:
                continue
            if merged and merged[-1]["tone"] == span["tone"]:
                merged[-1]["text"] += text
            else:
                merged.append({"text": text, "tone": span["tone"], "size": span["size"]})
        row["spans"] = [
            {"text": clean_text(span["text"]), "tone": span["tone"], "size": span["size"]}
            for span in merged
            if clean_text(span["text"])
        ]
        row["text"] = clean_text("".join(span["text"] for span in row["spans"]))
    return [row for row in rows if row["text"]]


def has_colour(row: dict) -> bool:
    return any(span["tone"] in {"key", "warm", "blue", "purple", "green"} for span in row["spans"])


def should_start_block(previous: dict | None, current: dict, gap: float) -> bool:
    text = current["text"]
    if previous is None:
        return True
    if BULLET_RE.match(text):
        return True
    if gap > 22:
        return True

    # A one- or two-character row is almost always the tail of a wrapped line.
    if len(text) <= 2:
        return False

    previous_text = previous["text"].rstrip()
    # A quoted definition usually answers the line above it.
    if text.startswith(("“", "‘", "《")) and any(
        marker in previous_text for marker in ("：", ":", "指导思想", "主张", "在于", "是指", "即")
    ):
        return False

    # Wrapped lines often continue after a comma, colon, or a connector.
    if previous_text.endswith(("：", ":", "—", "–", "，", ",", "、", "；", ";", "（", "(", "和", "与", "及", "的", "为", "是", "在", "对", "把", "使", "于")):
        return False

    # A new coloured line is a new fact; a plain line is usually the wrap of
    # the previous fact.
    if has_colour(current) and len(previous_text) >= 3:
        return True

    # Many facts have no coloured word on their first line.  A new subject
    # after a complete line still starts a new fact.
    if text.startswith(SUBJECT_PREFIXES) and len(previous_text) >= 1:
        return True

    # Meeting/event headings are short and carry a year or an event suffix.
    if len(text) <= 24 and (
        re.search(r"(?:19|20)\d{2}", text)
        or text.endswith(("会议", "全会", "运动", "战争", "革命", "主张", "政策", "讨论", "整风", "大", "中", "下"))
    ):
        return True
    return False


def merge_blocks(rows: list[dict]) -> list[dict]:
    blocks: list[dict] = []
    previous_row = None
    for row in rows:
        gap = row["y"] - (previous_row["y"] if previous_row else 0)
        if should_start_block(previous_row, row, gap):
            blocks.append(
                {
                    "text": row["text"],
                    "spans": [dict(span) for span in row["spans"]],
                }
            )
        else:
            block = blocks[-1]
            prev_text = block["text"]
            next_text = row["text"]
            # Chinese wrapped lines join directly; Latin words need a space.
            if re.search(r"[A-Za-z0-9]$", prev_text) and re.match(r"[A-Za-z0-9]", next_text):
                block["text"] = f"{prev_text} {next_text}"
                block["spans"].append({"text": " ", "tone": "plain", "size": 9.2})
            else:
                block["text"] = f"{prev_text}{next_text}"
            block["spans"].extend(dict(span) for span in row["spans"])
        previous_row = row
    return [block for block in blocks if block["text"].strip()]


def find_marker(rows: list[dict]):
    for index, row in enumerate(rows):
        match = re.search(r"知识点\s*0*(\d{1,3})", row["text"])
        if match:
            return index, int(match.group(1))
    return None, None


def extract_card(card, page_no: int):
    lines = [line for line in card["lines"] if inside_card(line, card["rect"])]
    rows = merge_rows(lines)
    marker_index, number = find_marker(rows)
    if marker_index is None:
        return None

    # Title: the first larger black line after the marker.
    title = ""
    title_index = None
    for index in range(marker_index + 1, len(rows)):
        row = rows[index]
        if len(row["text"]) <= 32 and row["size"] >= 9.8 and row["text"] not in {"知识点"}:
            title = row["text"]
            title_index = index
            break
    if title_index is None:
        title_index = marker_index

    content = [
        row
        for index, row in enumerate(rows)
        if index > title_index and not row["text"].startswith("知识点")
    ]
    return {
        "number": number,
        "title": title,
        "page": page_no,
        "rows": content,
        "has_image": card.get("has_image", False),
        "rect": card["rect"],
    }


def build_points(doc):
    points: dict[int, dict] = {}
    page_map: dict[int, list[int]] = {}

    for page_no in CONTENT_PAGES:
        page = doc[page_no - 1]
        page_key, page_section, page_color = section_for(page_no)
        lines = [line for line in read_lines(page) if not is_page_furniture(line)]

        # Subsection headers such as 基本知识 / 早期 sit outside the cards.
        topics = [
            line
            for line in lines
            if 50 <= line["x"] <= 55 and 10.2 <= line["size"] <= 11.2 and len(line["text"]) <= 12
        ]
        # The big section bar is not a subtopic.
        topic_lines = [line for line in topics if line["text"] != page_section]

        drawings = page.get_drawings()
        cards = []
        for drawing in drawings:
            rect = drawing["rect"]
            if drawing["type"] != "fs" or rect.width < CARD_MIN_W or rect.height < CARD_MIN_H:
                continue
            cards.append({"rect": rect, "lines": lines, "has_image": False})
        for image in page.get_images(full=True):
            # get_images doesn't provide bbox; use image blocks instead.
            pass
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 1:
                rect = pymupdf.Rect(block["bbox"])
                for card in cards:
                    if card["rect"].contains(rect):
                        card["has_image"] = True

        # Reading order: left column top-to-bottom, then right column.
        cards.sort(key=lambda card: (round(card["rect"].x0 / 100), card["rect"].y0))

        for card in cards:
            marker_index, number = find_marker(merge_rows([line for line in card["lines"] if inside_card(line, card["rect"])]))
            if number is None:
                continue
            point = points.get(number)
            if point is None:
                point = {
                    "id": f"{number:03d}",
                    "n": number,
                    "title": "",
                    "section": page_key,
                    "sectionName": page_section,
                    "color": page_color,
                    "topic": "",
                    "page": page_no,
                    "pages": [page_no],
                    "blocks": [],
                    "figure": None,
                }
                points[number] = point
            else:
                if page_no not in point["pages"]:
                    point["pages"].append(page_no)

            # Assign the latest subsection header above this card.
            card_y = card["rect"].y0
            topic = ""
            for topic_line in topic_lines:
                if topic_line["y"] < card_y:
                    topic = topic_line["text"]
            if topic:
                point["topic"] = topic

            card_data = extract_card(card, page_no)
            if not card_data:
                continue
            if not point["title"]:
                point["title"] = card_data["title"]
            # Deduplicate repeated title rows, e.g. a card continuing on the next page.
            blocks = merge_blocks(card_data["rows"])
            if point["title"]:
                blocks = [block for block in blocks if block["text"] != point["title"]]
            for block in blocks:
                # A few OCR/font artefacts in the source PDF.
                block["text"] = block["text"].replace("彳亍", "行")
                for span in block["spans"]:
                    span["text"] = span["text"].replace("彳亍", "行")
                # Sentences that start with 是/指 often lost their subject in
                # the card's heading; put the point title back for readability.
                if (
                    point["title"]
                    and block["text"].startswith(("是", "指", "即"))
                    and not block["text"].startswith(point["title"])
                ):
                    block["text"] = f"{point['title']}{block['text']}"
                    block["spans"].insert(0, {"text": point["title"], "tone": "plain", "size": 9.2})
            point["blocks"].extend(blocks)

            if card_data["has_image"] and page_no == 18 and number == 37:
                point["figure"] = {
                    "src": "figures/timeline.png",
                    "alt": "史纲整体脉络时间轴：1840—1978 的历史时期、革命性质与国情变化",
                }

    # Make sure every id is present, and record page -> point mapping.
    for number in range(1, 101):
        if number not in points:
            page_for = next(
                (page for page in CONTENT_PAGES if any(entry[2] <= page <= entry[3] for entry in SECTIONS)),
                35,
            )
            points[number] = {
                "id": f"{number:03d}",
                "n": number,
                "title": f"知识点 {number:03d}",
                "section": "other",
                "sectionName": "其他",
                "color": "#3f8f6b",
                "topic": "",
                "page": page_for,
                "pages": [page_for],
                "blocks": [],
                "figure": None,
            }
    for number, point in sorted(points.items()):
        for page_no in point["pages"]:
            page_map.setdefault(page_no, []).append(point["id"])
        # Keep only display fields.
        point["pages"] = sorted(set(point["pages"]))
    return [points[number] for number in sorted(points)], page_map


def keywords_of(point: dict) -> list[str]:
    out: list[str] = []
    for block in point["blocks"]:
        for span in block["spans"]:
            if span["tone"] in {"key", "warm", "blue", "purple", "green"}:
                text = span["text"].strip(" ：:，,。.；;、")
                if 1 < len(text) <= 24 and text not in out:
                    out.append(text)
    return out[:12]


def preview_of(point: dict) -> str:
    for block in point["blocks"]:
        if len(block["text"]) >= 8:
            return block["text"][:48]
    return point["title"]


def build_plan(points: list[dict]) -> list[dict]:
    by_page: dict[int, list[str]] = {}
    for point in points:
        by_page.setdefault(point["page"], []).append(point["id"])

    start = date(2026, 11, 6)
    plan = []
    day = 0
    # First pass: one booklet page per day, 11–35 -> 2026-11-06..11-30.
    for page_no in range(11, 36):
        day += 1
        current = start + timedelta(days=day - 1)
        plan.append(
            {
                "date": current.isoformat(),
                "day": day,
                "phase": "第一轮",
                "pages": [page_no],
                "pointIds": by_page.get(page_no, []),
                "focus": f"第 {page_no - 10}/25 页 · 新考点",
                "minutes": 40,
            }
        )

    # Second pass through early December: two pages a day, 11–22.
    second_pages = [(11, 12), (13, 14), (15, 16), (17, 18), (19, 20), (21, 22)]
    for index, pages in enumerate(second_pages):
        day += 1
        current = start + timedelta(days=day - 1)
        ids = []
        for page_no in pages:
            ids.extend(by_page.get(page_no, []))
        plan.append(
            {
                "date": current.isoformat(),
                "day": day,
                "phase": "第二轮",
                "pages": list(pages),
                "pointIds": ids,
                "focus": f"回炉第 {pages[0] - 10}–{pages[1] - 10} 页 · 只做回忆",
                "minutes": 45,
            }
        )
    return plan


def main() -> None:
    pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF
    doc = pymupdf.open(pdf_path)
    OUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    points, page_map = build_points(doc)

    # Crop the timeline figure from p18.
    page = doc[17]
    pix = page.get_pixmap(
        clip=pymupdf.Rect(49, 158, 546.3, 395.6),
        matrix=pymupdf.Matrix(2, 2),
        alpha=False,
    )
    pix.save(FIGURES / "timeline.png")

    index = []
    for point in points:
        point["keywords"] = keywords_of(point)
        point["preview"] = preview_of(point)
        index.append(
            {
                "id": point["id"],
                "n": point["n"],
                "title": point["title"],
                "section": point["section"],
                "sectionName": point["sectionName"],
                "topic": point["topic"],
                "page": point["page"],
                "pages": point["pages"],
                "keywords": point["keywords"],
                "preview": point["preview"],
            }
        )

    plan = build_plan(points)
    meta = {
        "version": 1,
        "generatedAt": "2026-11-05",
        "source": "27考研政治一页纸·知识点手册（澄潇宇）",
        "examDate": "2026-12-19",
        "planStart": plan[0]["date"],
        "planEnd": plan[-1]["date"],
        "pointCount": len(points),
        "pageCount": 25,
        "cardHint": "卡面只留彩色关键词的填空，答案按原书颜色还原。",
        "sections": [
            {
                "id": key,
                "name": name,
                "startPage": start,
                "endPage": end,
                "color": color,
                "count": sum(1 for point in points if point["section"] == key),
            }
            for key, name, start, end, color in SECTIONS
        ],
    }

    (OUT / "points.json").write_text(
        json.dumps(points, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    (OUT / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    (OUT / "plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    (OUT / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"pages: {doc.page_count}")
    print(f"points: {len(points)}; index: {len(index)}; plan days: {len(plan)}")
    print(f"plan: {plan[0]['date']} -> {plan[-1]['date']}")
    print("points per page:", {page: len(ids) for page, ids in sorted(page_map.items())})
    for point in points[:3] + points[-3:]:
        print(point["id"], point["title"], len(point["blocks"]), "blocks", point["keywords"])
    for number in range(1, 101):
        if not any(point["id"] == f"{number:03d}" for point in points):
            print("MISSING", number)


if __name__ == "__main__":
    main()
