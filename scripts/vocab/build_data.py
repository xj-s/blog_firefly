#!/usr/bin/env python3
"""Build the static vocabulary dataset used by /vocab/.

Inputs (downloaded by scripts/vocab/fetch_sources.mjs):
  .cache/vocab/netem.json       5530 syllabus words + rank + CEFR + examples
  .cache/vocab/kaoyan.jsonl     9602 考研 word-book entries (definitions, phrases,
                                synonyms, word families, memory hints, examples)
  .cache/vocab/lemma.en.txt     lemma -> inflected forms
  .cache/vocab/ipa.txt          IPA fallback
  .cache/vocab/exams.json       sentences extracted from 2010-2026 papers

Outputs:
  public/vocab/data/meta.json
  public/vocab/data/index.json
  public/vocab/data/words/<letter>.json

Usage:
  python scripts/vocab/build_data.py
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "vocab"
OUT = ROOT / "public" / "vocab" / "data"

SECTION_WEIGHT = {"阅读": 10.0, "翻译": 7.0, "新题型": 6.0}
SECTION_CODE = {"阅读": "阅读", "翻译": "翻译", "新题型": "新题型", "完形": "完形"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate(text: str, limit: int) -> str:
    text = clean_text(text)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------


def load_netem() -> dict[str, dict]:
    payload = load_json(CACHE / "netem.json")
    rows = next(iter(payload.values()))
    out: dict[str, dict] = {}
    for row in rows:
        word = clean_text(str(row.get("单词", ""))).lower()
        if not word or " " in word:
            continue
        out[word] = row
    return out


def load_kyle() -> dict[str, dict]:
    best: dict[str, tuple[int, dict]] = {}
    with (CACHE / "kaoyan.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            word = clean_text(str(payload.get("headWord", ""))).lower()
            if not word or " " in word:
                continue
            content = payload.get("content", {}).get("word", {}).get("content", {})
            score = sum(
                1
                for key in ("trans", "phrase", "syno", "relWord", "sentence", "remMethod")
                if content.get(key)
            )
            score = score * 1000 + len(json.dumps(content, ensure_ascii=False))
            if word not in best or score > best[word][0]:
                best[word] = (score, content)
    return {word: content for word, (_, content) in best.items()}


def load_lemma() -> dict[str, set[str]]:
    forms: dict[str, set[str]] = collections.defaultdict(set)
    with (CACHE / "lemma.en.txt").open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith(";") or "->" not in line:
                continue
            left, right = line.strip().split("->", 1)
            lemma = left.split("/")[0].strip().lower()
            if not lemma:
                continue
            for form in right.split(","):
                form = form.strip().lower()
                if form and form != lemma:
                    forms[lemma].add(form)
    return forms


def load_ipa() -> dict[str, str]:
    out: dict[str, str] = {}
    with (CACHE / "ipa.txt").open(encoding="utf-8") as handle:
        for line in handle:
            if "\t" not in line:
                continue
            word, phone = line.rstrip("\n").split("\t", 1)
            phone = re.split(r"[,;]", phone.strip().strip("/"))[0].strip()
            if word and phone:
                out[word.lower()] = phone
    return out


def load_notes() -> dict[str, str]:
    return {
        key.lower(): value
        for key, value in load_json(ROOT / "scripts" / "vocab" / "notes.json").items()
    }


def load_confusions() -> list[list[str]]:
    return [
        [word.lower() for word in group]
        for group in load_json(ROOT / "scripts" / "vocab" / "confusions.json")
    ]


# ---------------------------------------------------------------------------
# Phonetics
# ---------------------------------------------------------------------------

IPA_CHARS = set("abcdefghijklmnopqrstuvwxyzæɑɒɔəɜɛɪʊʌθðʃʒŋɹɾɻˈˌː()[]; -/.,'")


def normalize_phone(phone: str, ipa_fallback: str | None) -> str | None:
    phone = clean_text(phone or "")
    if not phone:
        phone = clean_text(ipa_fallback or "")
    if not phone:
        return None
    if any("\u4e00" <= ch <= "\u9fff" for ch in phone):
        return None
    if len(phone) > 60:
        return None
    phone = re.split(r"[,;]", phone)[0].strip().strip("/")
    if not phone:
        return None
    # The word-book uses ASCII stress marks; convert to IPA look-alikes.
    phone = phone.replace("'", "ˈ").replace(",", "ˌ")
    phone = phone.replace("ˈˈ", "ˈ")
    phone = re.sub(r"\s+", " ", phone).strip()
    if not phone:
        return None
    if not phone.startswith("/"):
        phone = f"/{phone}/"
    return phone


# ---------------------------------------------------------------------------
# Inflections
# ---------------------------------------------------------------------------

VOWELS = "aeiou"

STOPWORDS = {
    "the", "a", "an", "of", "to", "in", "on", "at", "by", "for", "and", "or",
    "but", "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "it", "this", "that", "these", "those", "i",
    "you", "he", "she", "we", "they", "me", "him", "her", "us", "them", "my",
    "your", "his", "its", "our", "their", "as", "if", "than", "then", "so",
}

# Only irregular forms that cannot be derived by suffix rules. Keeping this
# list explicit avoids the junk entries that the BNC lemma file contains
# (e.g. "thing" listed as a form of "the").
IRREGULAR: dict[str, set[str]] = {
    "be": {"am", "is", "are", "was", "were", "been", "being"},
    "have": {"has", "had", "having"},
    "do": {"does", "did", "done", "doing"},
    "say": {"says", "said", "saying"},
    "go": {"goes", "went", "gone", "going"},
    "get": {"gets", "got", "gotten", "getting"},
    "make": {"makes", "made", "making"},
    "know": {"knows", "knew", "known", "knowing"},
    "think": {"thinks", "thought", "thinking"},
    "take": {"takes", "took", "taken", "taking"},
    "see": {"sees", "saw", "seen", "seeing"},
    "come": {"comes", "came", "coming"},
    "give": {"gives", "gave", "given", "giving"},
    "find": {"finds", "found", "finding"},
    "tell": {"tells", "told", "telling"},
    "become": {"becomes", "became", "becoming"},
    "show": {"shows", "showed", "shown", "showing"},
    "leave": {"leaves", "left", "leaving"},
    "feel": {"feels", "felt", "feeling"},
    "put": {"puts", "putting"},
    "bring": {"brings", "brought", "bringing"},
    "begin": {"begins", "began", "begun", "beginning"},
    "keep": {"keeps", "kept", "keeping"},
    "hold": {"holds", "held", "holding"},
    "write": {"writes", "wrote", "written", "writing"},
    "stand": {"stands", "stood", "standing"},
    "hear": {"hears", "heard", "hearing"},
    "let": {"lets", "letting"},
    "mean": {"means", "meant", "meaning"},
    "set": {"sets", "setting"},
    "meet": {"meets", "met", "meeting"},
    "run": {"runs", "ran", "running"},
    "pay": {"pays", "paid", "paying"},
    "sit": {"sits", "sat", "sitting"},
    "speak": {"speaks", "spoke", "spoken", "speaking"},
    "lie": {"lies", "lay", "lain", "lying"},
    "lead": {"leads", "led", "leading"},
    "read": {"reads", "reading"},
    "grow": {"grows", "grew", "grown", "growing"},
    "lose": {"loses", "lost", "losing"},
    "fall": {"falls", "fell", "fallen", "falling"},
    "send": {"sends", "sent", "sending"},
    "build": {"builds", "built", "building"},
    "understand": {"understands", "understood", "understanding"},
    "draw": {"draws", "drew", "drawn", "drawing"},
    "break": {"breaks", "broke", "broken", "breaking"},
    "spend": {"spends", "spent", "spending"},
    "cut": {"cuts", "cutting"},
    "rise": {"rises", "rose", "risen", "rising"},
    "drive": {"drives", "drove", "driven", "driving"},
    "buy": {"buys", "bought", "buying"},
    "wear": {"wears", "wore", "worn", "wearing"},
    "choose": {"chooses", "chose", "chosen", "choosing"},
    "eat": {"eats", "ate", "eaten", "eating"},
    "drink": {"drinks", "drank", "drunk", "drinking"},
    "sing": {"sings", "sang", "sung", "singing"},
    "swim": {"swims", "swam", "swum", "swimming"},
    "fly": {"flies", "flew", "flown", "flying"},
    "throw": {"throws", "threw", "thrown", "throwing"},
    "catch": {"catches", "caught", "catching"},
    "teach": {"teaches", "taught", "teaching"},
    "fight": {"fights", "fought", "fighting"},
    "seek": {"seeks", "sought", "seeking"},
    "sell": {"sells", "sold", "selling"},
    "sleep": {"sleeps", "slept", "sleeping"},
    "wake": {"wakes", "woke", "woken", "waking"},
    "win": {"wins", "won", "winning"},
    "forget": {"forgets", "forgot", "forgotten", "forgetting"},
    "forgive": {"forgives", "forgave", "forgiven", "forgiving"},
    "freeze": {"freezes", "froze", "frozen", "freezing"},
    "hide": {"hides", "hid", "hidden", "hiding"},
    "ride": {"rides", "rode", "ridden", "riding"},
    "ring": {"rings", "rang", "rung", "ringing"},
    "shake": {"shakes", "shook", "shaken", "shaking"},
    "shoot": {"shoots", "shot", "shooting"},
    "shut": {"shuts", "shutting"},
    "sink": {"sinks", "sank", "sunk", "sinking"},
    "steal": {"steals", "stole", "stolen", "stealing"},
    "stick": {"sticks", "stuck", "sticking"},
    "strike": {"strikes", "struck", "stricken", "striking"},
    "swear": {"swears", "swore", "sworn", "swearing"},
    "sweep": {"sweeps", "swept", "sweeping"},
    "tear": {"tears", "tore", "torn", "tearing"},
    "weave": {"weaves", "wove", "woven", "weaving"},
    "withdraw": {"withdraws", "withdrew", "withdrawn", "withdrawing"},
    "overcome": {"overcomes", "overcame", "overcoming"},
    "undertake": {"undertakes", "undertook", "undertaken", "undertaking"},
    "arise": {"arises", "arose", "arisen", "arising"},
    "awake": {"awakes", "awoke", "awoken", "awaking"},
    "bear": {"bears", "bore", "borne", "bearing"},
    "beat": {"beats", "beaten", "beating"},
    "bend": {"bends", "bent", "bending"},
    "bind": {"binds", "bound", "binding"},
    "bite": {"bites", "bit", "bitten", "biting"},
    "bleed": {"bleeds", "bled", "bleeding"},
    "blow": {"blows", "blew", "blown", "blowing"},
    "breed": {"breeds", "bred", "breeding"},
    "cast": {"casts", "casting"},
    "creep": {"creeps", "crept", "creeping"},
    "deal": {"deals", "dealt", "dealing"},
    "dig": {"digs", "dug", "digging"},
    "feed": {"feeds", "fed", "feeding"},
    "flee": {"flees", "fled", "fleeing"},
    "hang": {"hangs", "hung", "hanging"},
    "hit": {"hits", "hitting"},
    "hurt": {"hurts", "hurting"},
    "kneel": {"kneels", "knelt", "kneeling"},
    "lay": {"lays", "laid", "laying"},
    "lend": {"lends", "lent", "lending"},
    "light": {"lights", "lit", "lighting"},
    "mistake": {"mistakes", "mistook", "mistaken", "mistaking"},
    "prove": {"proves", "proved", "proven", "proving"},
    "quit": {"quits", "quitting"},
    "shrink": {"shrinks", "shrank", "shrunk", "shrinking"},
    "spread": {"spreads", "spreading"},
    "spring": {"springs", "sprang", "sprung", "springing"},
    "sting": {"stings", "stung", "stinging"},
    "strive": {"strives", "strove", "striven", "striving"},
    "child": {"children"},
    "man": {"men"},
    "woman": {"women"},
    "person": {"people"},
    "foot": {"feet"},
    "tooth": {"teeth"},
    "mouse": {"mice"},
    "goose": {"geese"},
    "ox": {"oxen"},
    "analysis": {"analyses"},
    "crisis": {"crises"},
    "phenomenon": {"phenomena"},
    "criterion": {"criteria"},
    "datum": {"data"},
    "medium": {"media"},
    "bacterium": {"bacteria"},
    "curriculum": {"curricula"},
    "index": {"indices", "indexes"},
    "matrix": {"matrices"},
    "thesis": {"theses"},
    "hypothesis": {"hypotheses"},
    "basis": {"bases"},
    "diagnosis": {"diagnoses"},
    "emphasis": {"emphases"},
    "synthesis": {"syntheses"},
    "good": {"better", "best"},
    "bad": {"worse", "worst"},
    "far": {"farther", "further", "farthest", "furthest"},
    "little": {"less", "least"},
    "many": {"more", "most"},
    "much": {"more", "most"},
}


def is_cvc(word: str) -> bool:
    return (
        len(word) >= 3
        and word[-1] not in VOWELS
        and word[-2] in VOWELS
        and word[-3] not in VOWELS
        and word[-1] not in "wxy"
    )


def generated_forms(word: str, pos_tags: set[str]) -> set[str]:
    """Rule-based inflections used to validate the noisy lemma database."""
    out: set[str] = set()
    if not word.isalpha() or word in STOPWORDS:
        return out
    if word in IRREGULAR:
        out |= IRREGULAR[word]
    if len(word) < 3:
        return out
    # plural / third person singular
    if word.endswith(("s", "x", "z", "ch", "sh")):
        out.add(word + "es")
    elif word.endswith("y") and len(word) > 2 and word[-2] not in VOWELS:
        out.add(word[:-1] + "ies")
    else:
        out.add(word + "s")
    # past
    if word.endswith("e"):
        out.add(word + "d")
    elif word.endswith("y") and len(word) > 2 and word[-2] not in VOWELS:
        out.add(word[:-1] + "ied")
    else:
        out.add(word + "ed")
        if is_cvc(word):
            out.add(word + word[-1] + "ed")
    # present participle
    if word.endswith("ie"):
        out.add(word[:-2] + "ying")
    elif word.endswith("e") and not word.endswith("ee"):
        out.add(word[:-1] + "ing")
    else:
        out.add(word + "ing")
        if is_cvc(word):
            out.add(word + word[-1] + "ing")
    # comparative / superlative, only for adjectives and adverbs
    if any(tag.startswith(("adj", "adv")) for tag in pos_tags):
        if word.endswith("y") and len(word) > 2 and word[-2] not in VOWELS:
            out.add(word[:-1] + "ier")
            out.add(word[:-1] + "iest")
        elif word.endswith("e"):
            out.add(word + "r")
            out.add(word + "st")
        else:
            out.add(word + "er")
            out.add(word + "est")
            if is_cvc(word):
                out.add(word + word[-1] + "er")
                out.add(word + word[-1] + "est")
    return {form for form in out if len(form) >= 3 and form != word}


# ---------------------------------------------------------------------------
# Exam sentences
# ---------------------------------------------------------------------------

BAD_EXAM = re.compile(
    r"(?:"
    r"ANSWER\s+SHEET|Directions?\s*[;:]|^\s*\[[A-G]|"
    r"Which of the following|It can be (?:learned|inferred|concluded)|"
    r"The author(?:'s)? (?:attitude|purpose|view)|"
    r"According to (?:Paragraph|the author|the text)|In Paragraph \d|"
    r"The word .{1,30} (?:refers to|is closest in meaning)|"
    r"The phrase .{1,40} (?:refers to|is closest in meaning)|"
    r"Write (?:your|an) (?:answer|essay)|You should (?:write|not)|"
    r"Do not (?:sign|use|write)|_|_{2,}|"
    r"\b[A-D]\.\s.*\b[A-D]\.\s|"
    r"[\^~]{2,}|"
    r"\b\d{1,2}\s+(?:am|is|are|was|were|a|an|the)\b"
    r")",
    re.I,
)


def sentence_ok(text: str) -> bool:
    text = clean_text(text)
    if not (45 <= len(text) <= 380):
        return False
    if not re.search(r"[A-Za-z]{3}", text):
        return False
    if re.search(r"[\u4e00-\u9fff\ufffd]", text):
        return False
    if BAD_EXAM.search(text):
        return False
    letters = sum(ch.isalpha() for ch in text)
    if letters / max(len(text), 1) < 0.6:
        return False
    if text.count(",") > 12 or text.count(";") > 6:
        return False
    return True


def exam_score(item: dict, hit_form: str, headword: str) -> float:
    score = SECTION_WEIGHT.get(item["sec"], 3.0)
    score += max(0, item["y"] - 2010) * 0.35
    length = len(item["text"])
    if 70 <= length <= 220:
        score += 2.0
    elif length <= 300:
        score += 0.8
    if hit_form == headword:
        score += 0.6
    return score


def build_exam_index(exams: list[dict]) -> tuple[list[dict], dict[str, set[int]]]:
    cleaned: list[dict] = []
    seen: set[str] = set()
    for item in exams:
        if item.get("sec") == "完形":
            continue
        text = clean_text(item.get("text", ""))
        if not sentence_ok(text):
            continue
        key = re.sub(r"\W+", "", text.lower())
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(
            {
                "y": int(item["y"]),
                "p": int(item["p"]),
                "sec": item["sec"],
                "src": item.get("src", ""),
                "text": text,
            }
        )
    token_index: dict[str, set[int]] = collections.defaultdict(set)
    for idx, item in enumerate(cleaned):
        for token in re.findall(r"[A-Za-z][A-Za-z'-]*", item["text"].lower()):
            token = token.strip("'-")
            if len(token) < 2:
                continue
            token_index[token].add(idx)
            if token.endswith("'s"):
                token_index[token[:-2]].add(idx)
    return cleaned, token_index


def select_exam(
    word: str,
    forms: set[str],
    token_index: dict[str, set[int]],
    exams: list[dict],
    limit: int = 5,
) -> tuple[list[dict], int]:
    ids: set[int] = set()
    for form in forms:
        ids |= token_index.get(form, set())
    if not ids:
        return [], 0
    candidates: list[tuple[float, int, str]] = []
    for idx in ids:
        item = exams[idx]
        matched = ""
        for token in re.findall(r"[A-Za-z][A-Za-z'-]*", item["text"].lower()):
            token = token.strip("'-")
            if token in forms or (token.endswith("'s") and token[:-2] in forms):
                matched = token
                break
        if not matched:
            continue
        candidates.append((exam_score(item, matched, word), idx, matched))
    candidates.sort(key=lambda row: (-row[0], -exams[row[1]]["y"]))
    selected: list[dict] = []
    year_count: collections.Counter[int] = collections.Counter()
    for _, idx, matched in candidates:
        item = exams[idx]
        if year_count[item["y"]] >= 2:
            continue
        entry = dict(item)
        entry["hit"] = matched
        selected.append(entry)
        year_count[item["y"]] += 1
        if len(selected) >= limit:
            break
    return selected, len(ids)


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args()
    out_dir = Path(args.out)

    netem = load_netem()
    kyle = load_kyle()
    lemma = load_lemma()
    ipa = load_ipa()
    notes = load_notes()
    confusions = load_confusions()
    exams, token_index = build_exam_index(load_json(CACHE / "exams.json"))

    all_words = sorted(set(netem) | set(kyle))
    print(
        f"netem={len(netem)} kyle={len(kyle)} union={len(all_words)} "
        f"exams={len(exams)}"
    )

    # Forms / inflections. The BNC lemma file is noisy, so generated forms are
    # used to validate it; irregular forms come from the explicit table above.
    pos_map: dict[str, set[str]] = {
        word: {
            clean_text(item.get("pos", ""))
            for item in kyle.get(word, {}).get("trans", [])
        }
        for word in all_words
    }
    forms_map: dict[str, set[str]] = {}
    display_forms: dict[str, set[str]] = {}
    for word in all_words:
        generated = generated_forms(word, pos_map.get(word, set()))
        lemma_forms = {
            form
            for form in lemma.get(word, set())
            if form in generated and re.fullmatch(r"[a-z][a-z'-]{1,20}", form)
        }
        valid = lemma_forms or generated
        forms_map[word] = {word} | generated | lemma_forms
        display_forms[word] = {form for form in valid if form != word}

    # Confusion partners, only among words we ship.
    confusion_map: dict[str, list[str]] = collections.defaultdict(list)
    for group in confusions:
        present = [word for word in group if word in all_words]
        if len(present) < 2:
            continue
        for word in present:
            confusion_map[word].extend(other for other in present if other != word)

    worlds: dict[str, dict] = {}
    index_rows: list[list] = []
    covered = 0

    for word in all_words:
        k = kyle.get(word, {})
        n = netem.get(word, {})
        trans: list[dict] = []
        for item in k.get("trans", [])[:6]:
            cn = clean_text(item.get("tranCn", ""))
            if not cn:
                continue
            trans.append(
                {
                    "pos": clean_text(item.get("pos", "")),
                    "cn": truncate(cn, 90),
                    "en": truncate(clean_text(item.get("tranOther", "")), 160),
                }
            )
        if not trans and n.get("释义"):
            trans.append({"pos": "", "cn": truncate(n["释义"], 120), "en": ""})

        phrases = []
        for item in (k.get("phrase", {}) or {}).get("phrases", [])[:8]:
            en = clean_text(item.get("pContent", ""))
            cn = clean_text(item.get("pCn", ""))
            if en:
                phrases.append({"en": truncate(en, 60), "cn": truncate(cn, 80)})

        synonyms = []
        for item in (k.get("syno", {}) or {}).get("synos", [])[:4]:
            words = [
                clean_text(hit.get("w", ""))
                for hit in item.get("hwds", [])[:6]
                if clean_text(hit.get("w", ""))
            ]
            if words:
                synonyms.append(
                    {
                        "pos": clean_text(item.get("pos", "")),
                        "cn": truncate(clean_text(item.get("tran", "")), 70),
                        "words": words,
                    }
                )

        family = []
        family_seen: set[str] = set()
        for item in (k.get("relWord", {}) or {}).get("rels", [])[:6]:
            words = []
            for hit in item.get("words", [])[:5]:
                hwd = clean_text(hit.get("hwd", ""))
                key = hwd.lower()
                if hwd and key != word and key not in family_seen:
                    family_seen.add(key)
                    words.append(
                        {"w": hwd, "cn": truncate(clean_text(hit.get("tran", "")), 50)}
                    )
            if words:
                family.append({"pos": clean_text(item.get("pos", "")), "words": words})

        examples = []
        for item in (k.get("sentence", {}) or {}).get("sentences", [])[:2]:
            en = clean_text(item.get("sContent", ""))
            if en:
                examples.append({"en": truncate(en, 240), "zh": truncate(item.get("sCn", ""), 140)})
        if not examples and n.get("例句"):
            source = clean_text(n.get("例句来源", ""))
            examples.append(
                {
                    "en": truncate(n["例句"], 240),
                    "zh": truncate(n.get("例句翻译", ""), 140),
                    "src": source,
                }
            )

        if word in STOPWORDS:
            selected, exam_count = [], 0
        else:
            selected, exam_count = select_exam(
                word, forms_map[word], token_index, exams
            )
        if selected:
            covered += 1

        legacy = None
        netem_src = clean_text(n.get("例句来源", ""))
        if not selected and netem_src.startswith("真题"):
            match = re.search(r"(\d{4})", netem_src)
            paper_match = re.search(r"英([一二])", netem_src)
            legacy = {
                "y": int(match.group(1)) if match else None,
                "p": 1 if paper_match and paper_match.group(1) == "一" else 2,
                "sec": "真题",
                "src": netem_src,
                "text": truncate(n.get("例句", ""), 320),
                "zh": truncate(n.get("例句翻译", ""), 160),
            }

        uk = normalize_phone(k.get("ukphone", ""), ipa.get(word))
        us = normalize_phone(k.get("usphone", ""), ipa.get(word))
        if uk and us and uk == us:
            us = None

        infl = sorted(display_forms[word])[:8]

        detail = {
            "w": word,
            "uk": uk,
            "us": us,
            "trans": trans,
            "phr": phrases,
            "syn": synonyms,
            "fam": family,
            "mem": truncate(k.get("remMethod", {}).get("val", ""), 180)
            if isinstance(k.get("remMethod"), dict)
            else "",
            "ex": examples,
            "exam": selected,
            "legacy": legacy,
            "note": notes.get(word, ""),
            "confuse": sorted(set(confusion_map.get(word, [])))[:5],
            "infl": infl,
            "syllabus": word in netem,
            "rank": int(n.get("序号", 99999)) if n else 99999,
            "freq": int(n.get("词频", 0)) if n else 0,
            "cefr": clean_text(n.get("CEFR等级", "")) if n else "",
            "cat": clean_text(n.get("分类名称", "")) if n else "",
            "academic": bool(n.get("学术词汇", False)) if n else False,
            "advanced": bool(n.get("高级词汇", False)) if n else False,
            "star": int(k.get("star", 0) or 0),
            "examCount": exam_count,
        }
        # Drop empty optional fields to keep shards small.
        for key in ("uk", "us", "phr", "syn", "fam", "mem", "legacy", "note"):
            if not detail[key]:
                detail.pop(key, None)
        if not detail["exam"]:
            detail.pop("exam")
        if not detail["infl"]:
            detail.pop("infl")
        if not detail["confuse"]:
            detail.pop("confuse")
        if not detail["cat"]:
            detail.pop("cat")
        if not detail["cefr"]:
            detail.pop("cefr")

        world = worlds.get(word)
        # Prefer syllabus entries if a word somehow appears twice.
        if world is None or (detail["syllabus"] and not world.get("syllabus")):
            worlds[word] = detail

        brief = "；".join(item["cn"] for item in trans[:2] if item["cn"])
        index_rows.append(
            [
                word,
                uk or us or "",
                truncate(brief, 52),
                trans[0]["pos"] if trans else "",
                detail["rank"],
                exam_count,
                1 if detail["syllabus"] else 0,
                detail.get("cefr", ""),
                detail["star"],
            ]
        )

    index_rows.sort(key=lambda row: (row[4], row[0]))

    # Shard by first letter.
    shards: dict[str, dict[str, dict]] = collections.defaultdict(dict)
    for word, detail in worlds.items():
        letter = word[0] if word[0].isalpha() else "_"
        shards[letter][word] = detail
    shard_counts = {key: len(value) for key, value in sorted(shards.items())}

    out_dir.mkdir(parents=True, exist_ok=True)
    word_dir = out_dir / "words"
    word_dir.mkdir(parents=True, exist_ok=True)
    for old in word_dir.glob("*.json"):
        old.unlink()
    for letter, entries in shards.items():
        path = word_dir / f"{letter}.json"
        path.write_text(
            json.dumps(entries, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )

    (out_dir / "index.json").write_text(
        json.dumps(index_rows, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    meta = {
        "version": 1,
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "wordCount": len(worlds),
        "syllabusCount": sum(1 for word in worlds if word in netem),
        "examWordCount": covered,
        "examSentenceCount": len(exams),
        "examYears": [2010, 2026],
        "shards": shard_counts,
        "sources": [
            {
                "name": "NETEMVocabulary",
                "url": "https://github.com/exam-data/NETEMVocabulary",
                "license": "CC BY-NC-SA 4.0",
                "use": "考研大纲 5530 词、词频、CMU 分类、CEFR、部分真题例句",
            },
            {
                "name": "KyleBing/english-vocabulary",
                "url": "https://github.com/KyleBing/english-vocabulary",
                "license": "学习用途（原库未声明标准开源协议）",
                "use": "释义、词组、同近义、同根词、记忆法、例句",
            },
            {
                "name": "ECDICT lemma / ipa-dict",
                "url": "https://github.com/skywind3000/ECDICT",
                "license": "MIT",
                "use": "词形还原与音标兜底",
            },
            {
                "name": "2010-2026 考研英语（一/二）真题",
                "url": "https://github.com/Fantasia1999/kaoyanzhenti",
                "license": "仅供个人学习研究",
                "use": "真题例句（按句摘录，标注年份/题型）",
            },
        ],
        "notice": "本数据集为个人学习用途，不包含红宝书、词汇闪过等版权书籍的原文；栏目结构参考其常见编排方式。",
    }
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    sizes = {
        path.name: path.stat().st_size
        for path in sorted(word_dir.glob("*.json"), key=lambda p: p.stat().st_size, reverse=True)[:8]
    }
    print(f"words={len(worlds)} covered={covered} ({covered / max(len(worlds), 1):.1%})")
    print(f"index={ (out_dir / 'index.json').stat().st_size / 1024:.0f}KB")
    print("largest shards:", {key: f"{value / 1024:.0f}KB" for key, value in sizes.items()})
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
