#!/usr/bin/env python3
r"""
merge.py — merge a hand-curated cards.json into the app's cards.js.

Usage:
    python app\extract\merge.py
    # or with explicit paths:
    python app\extract\merge.py path\to\cards.json path\to\cards.js

cards.json is the authoritative 120-card source. The script:
  - reads cards.json (the user's curated extraction with 120 entries)
  - reads any existing cards.js (auto-detects UTF-8 / UTF-16 BOM)
  - builds a lookup of cards.js cards keyed by lowercased catalyst text
  - for each cards.json card, maps schemas; fills icon fields (difficulty,
    dice, rune, tags, scatter) from cards.js when a catalyst matches
  - writes merged result to cards.js as UTF-8

Schema mapping:
  cards.json                                cards.js
  -------------                             -------------
  id                                        id
  likely_odds.bad/even/good                 odds.bad/even/good
  random_event.verb/adjective/noun          event.verb/adjective/noun
  sensory.sound                             sensory.hear
  sensory.sight                             sensory.see
  sensory.touch                             sensory.feel
  sensory.smell_taste                       sensory.smell
  belongings.category/examples              belongings.category/items
  catalyst, location, virtue, vice, names   (direct)
  auxiliary.element_glyph                   element

Filled from cards.js by catalyst-match (if available):
  difficulty, dice, rune, tags, scatter
"""

import json
import re
import sys
from pathlib import Path

DEFAULT_JSON = Path("app/cards.json")
DEFAULT_JS   = Path("app/cards.js")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_js_cards(path):
    """Read cards.js, auto-detect encoding, parse the GMA_CARDS array."""
    if not path.exists():
        return []
    raw = path.read_bytes()
    if raw[:2] == b"\xff\xfe":
        text = raw.decode("utf-16-le")
    elif raw[:2] == b"\xfe\xff":
        text = raw.decode("utf-16-be")
    elif raw[:3] == b"\xef\xbb\xbf":
        text = raw[3:].decode("utf-8")
    else:
        text = raw.decode("utf-8", errors="replace")
    text = text.lstrip("﻿")

    m = re.search(r"window\.GMA_CARDS\s*=\s*(\[.*?\])\s*;", text, re.DOTALL)
    if not m:
        return []
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return []


def get(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def map_card(json_card, js_lookup):
    """Map cards.json card → cards.js schema; fill icon fields from cards.js."""
    out = {
        "id":         json_card.get("id"),
        "difficulty": None,
        "odds": {
            "bad":  get(json_card, "likely_odds", "bad"),
            "even": get(json_card, "likely_odds", "even"),
            "good": get(json_card, "likely_odds", "good"),
        },
        "dice": {
            "d4": None, "d6": None, "d8": None, "d10": None,
            "d12": None, "d20": None, "d100tens": None, "d100units": None,
        },
        "rune":    None,
        "element": get(json_card, "auxiliary", "element_glyph"),
        "event": {
            "verb":      get(json_card, "random_event", "verb"),
            "adjective": get(json_card, "random_event", "adjective"),
            "noun":      get(json_card, "random_event", "noun"),
        },
        "sensory": {
            "hear":  get(json_card, "sensory", "sound"),
            "see":   get(json_card, "sensory", "sight"),
            "feel":  get(json_card, "sensory", "touch"),
            "smell": get(json_card, "sensory", "smell_taste"),
        },
        "tags":    None,
        "scatter": None,
        "belongings": {
            "category": get(json_card, "belongings", "category"),
            "items":    get(json_card, "belongings", "examples") or [],
        },
        "names":    json_card.get("names") or [],
        "catalyst": json_card.get("catalyst"),
        "location": json_card.get("location"),
        "virtue":   json_card.get("virtue"),
        "vice":     json_card.get("vice"),
    }

    # Fill icon-only / dice / difficulty fields from cards.js by catalyst match
    cat = (out.get("catalyst") or "").strip().lower()
    matched = False
    if cat and cat in js_lookup:
        js = js_lookup[cat]
        matched = True
        if js.get("difficulty") is not None:
            out["difficulty"] = js["difficulty"]
        for k in out["dice"]:
            v = (js.get("dice") or {}).get(k)
            if v is not None:
                out["dice"][k] = v
        for k in ("rune", "tags", "scatter"):
            if js.get(k):
                out[k] = js[k]
    return out, matched


def main(argv):
    json_path = Path(argv[1]) if len(argv) >= 2 else DEFAULT_JSON
    js_path   = Path(argv[2]) if len(argv) >= 3 else DEFAULT_JS

    if not json_path.exists():
        print(f"error: {json_path} not found", file=sys.stderr)
        return 2

    data = read_json(json_path)
    json_cards = data.get("cards", [])
    if not json_cards:
        print("error: cards.json has no 'cards' array", file=sys.stderr)
        return 2

    js_cards = read_js_cards(js_path)
    js_lookup = {}
    for c in js_cards:
        cat = (c.get("catalyst") or "").strip().lower()
        if cat and cat not in js_lookup:
            js_lookup[cat] = c

    merged = []
    matched_count = 0
    for jc in json_cards:
        m, was_matched = map_card(jc, js_lookup)
        merged.append(m)
        if was_matched:
            matched_count += 1

    # Per-field fill rates after merge
    def fill(field_path):
        n = 0
        for c in merged:
            cur = c
            for k in field_path:
                cur = cur.get(k) if isinstance(cur, dict) else None
                if cur is None: break
            if cur is not None and cur != [] and cur != "":
                n += 1
        return n

    print(f"info: {len(json_cards)} cards in cards.json, "
          f"{len(js_cards)} in cards.js, "
          f"{matched_count} matched by catalyst.", file=sys.stderr)
    print("info: per-field fill rates after merge:", file=sys.stderr)
    for field, path_ in [
        ("difficulty",  ["difficulty"]),
        ("odds.bad",    ["odds", "bad"]),
        ("odds.even",   ["odds", "even"]),
        ("odds.good",   ["odds", "good"]),
        ("dice.d4",     ["dice", "d4"]),
        ("dice.d20",    ["dice", "d20"]),
        ("element",     ["element"]),
        ("event.verb",  ["event", "verb"]),
        ("sensory.hear", ["sensory", "hear"]),
        ("belongings.category", ["belongings", "category"]),
        ("names",       ["names"]),
        ("catalyst",    ["catalyst"]),
        ("location",    ["location"]),
        ("virtue",      ["virtue"]),
        ("vice",        ["vice"]),
        ("rune",        ["rune"]),
        ("tags",        ["tags"]),
        ("scatter",     ["scatter"]),
    ]:
        print(f"      {field:24s} {fill(path_)}/{len(merged)}", file=sys.stderr)

    js_path.write_text(
        "/* GMA / cards.js — merged by merge.py */\n"
        "/* primary source: cards.json (120 cards). Icon fields backfilled from "
        "the prior cards.js where catalyst matched. */\n"
        "window.GMA_CARDS = " +
        json.dumps(merged, indent=2, ensure_ascii=False) +
        ";\n",
        encoding="utf-8",
    )
    print(f"info: wrote {len(merged)} cards to {js_path} (UTF-8).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
