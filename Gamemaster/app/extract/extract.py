#!/usr/bin/env python3
"""
extract.py — turn a pdftotext-layout dump of GMA_Base_PnP into cards.js.

Usage:
    pdftotext -layout GMA_Base_PnP_5_9_15.pdf raw.txt
    python extract.py raw.txt > ../cards.js

What it does:
    1. Splits the dump on form-feed (\\f) into pages.
    2. Skips front-matter pages (those without 6 occurrences of "Likely Odds").
    3. For each card page: uses the column positions of the 6 "Likely Odds"
       labels to slice the page into 3 columns × 2 rows of card regions.
    4. For each region: extracts text-based fields with regex against known
       markers ("Likely Odds", "Names", "Catalyst", etc.).
    5. Emits a JavaScript file: window.GMA_CARDS = [{...}, {...}, ...].

What it does NOT do (because these are icon-based on the printed cards
and don't appear as text in pdftotext output):
    - Norse Rune (24 Elder Futhark) — left null; fill in by hand from the PDF.
    - Element (Earth / Fire / Air / Water) — left null; fill in by hand.
    - Tag Symbols (3 of 10 icons) — left null; fill in by hand.
    - Scatter Die (compass + hit/miss) — left null; fill in by hand.
    - Some dice values may be missing depending on layout — verify after run.

Tuning:
    Different PnP versions may align fields slightly differently. If a field
    comes out blank or wrong, look at the FIELD_PATTERNS dict below and adjust
    the regex / position rules.
"""

import re
import sys
import json
from pathlib import Path

# --- Tunables ---------------------------------------------------------------

# Labels we expect on the printed cards. Used both as page-detection anchors
# and as field markers during extraction. Order matters for anchor-priority:
# Catalyst extracts most reliably as text in this PnP, so try it first.
LABELED_FIELDS = [
    "Likely Odds", "Belongings", "Catalyst", "Location",
    "Names", "Virtue", "Vice",
]
# Anchor priority for column/row detection: skip "Likely Odds" first because
# on some pages it's rendered as an image and doesn't extract.
ANCHOR_PRIORITY = [
    "Catalyst", "Location", "Names", "Virtue", "Vice", "Belongings",
    "Likely Odds",
]
# A page is a "card page" if any anchor label appears at least this many times.
MIN_CARDS_PER_PAGE = 3

# Public-domain enumerations (these are common knowledge, not GMA content):
ELDER_FUTHARK = [
    "Fehu", "Uruz", "Thurisaz", "Ansuz", "Raidho", "Kenaz", "Gebo", "Wunjo",
    "Hagalaz", "Naudhiz", "Nauthiz", "Isa", "Jera", "Eihwaz", "Perthro",
    "Algiz", "Sowilo", "Tiwaz", "Berkano", "Ehwaz", "Mannaz", "Laguz",
    "Ingwaz", "Dagaz", "Othala",
]
ELEMENTS = ["Earth", "Fire", "Air", "Water"]
SCATTER_DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


# --- Parsing primitives -----------------------------------------------------

def is_card_page(page_text):
    """
    A card page has at least 3 distinct anchor labels each appearing
    >= MIN_CARDS_PER_PAGE times. This rejects instruction pages that mention
    one or two label names in body text without forming a card layout.
    """
    qualifying = sum(
        1 for lbl in ANCHOR_PRIORITY
        if page_text.count(lbl) >= MIN_CARDS_PER_PAGE
    )
    return qualifying >= 3


def find_marker_positions(line, marker):
    """Return all positions where marker starts on a line."""
    out, start = [], 0
    while True:
        i = line.find(marker, start)
        if i < 0:
            break
        out.append(i)
        start = i + len(marker)
    return out


def cluster_positions(positions, gap):
    """Group sorted positions into clusters separated by at least `gap`."""
    if not positions:
        return []
    sorted_p = sorted(positions)
    clusters = [sorted_p[0]]
    for p in sorted_p[1:]:
        if p - clusters[-1] > gap:
            clusters.append(p)
    return clusters


def split_into_card_regions(page_text):
    """
    Adaptively slice a card page. Pick the highest-count anchor label that
    appears at least MIN_CARDS_PER_PAGE times; use its (line, x) positions to
    derive column anchors and row anchors; slice the page into one region
    per card (cols × rows).
    """
    lines = page_text.splitlines()

    # Pick the anchor label with the most occurrences (>= MIN), preferring
    # earlier entries in ANCHOR_PRIORITY when counts tie.
    best_label, best_count = None, 0
    for lbl in ANCHOR_PRIORITY:
        c = page_text.count(lbl)
        if c >= MIN_CARDS_PER_PAGE and c > best_count:
            best_label, best_count = lbl, c

    if not best_label:
        return []

    # Collect (line_idx, x_pos) for every occurrence of the anchor label.
    occurrences = []
    for li, line in enumerate(lines):
        for x in find_marker_positions(line, best_label):
            occurrences.append((li, x))
    if not occurrences:
        return []

    # Column starts: cluster X positions with a wide gap (columns are far apart).
    column_xs = cluster_positions([o[1] for o in occurrences], gap=20)
    # Row starts: cluster line indices with a moderate gap.
    row_lis = cluster_positions(sorted(set(o[0] for o in occurrences)), gap=10)

    n_cols = len(column_xs)
    n_rows = len(row_lis)
    if n_cols == 0 or n_rows == 0:
        return []

    # Boundaries that include the left edge / top edge.
    col_bounds = [0] + column_xs[1:] + [10_000]
    row_bounds = [0] + row_lis[1:] + [len(lines)]

    regions = []
    for ri in range(n_rows):
        row_lines = lines[row_bounds[ri]:row_bounds[ri + 1]]
        for ci in range(n_cols):
            col_text = []
            for line in row_lines:
                seg = line[col_bounds[ci]:col_bounds[ci + 1]].rstrip()
                col_text.append(seg)
            regions.append("\n".join(col_text).strip())
    return regions


# --- Field extractors -------------------------------------------------------

def extract_likely_odds(region):
    """
    The Odds field shows three answers (Bad, Even, Good) printed near the
    "Likely Odds" label — sometimes on the same line, sometimes on the next.
    Take a window of text starting at the label and harvest the first three
    YES!/Yes/No/NO! tokens.
    """
    odds = {"bad": None, "even": None, "good": None}
    idx = region.find("Likely Odds")
    if idx == -1:
        return odds
    # Grab a window after the label that's big enough to span typical layouts
    chunk = region[idx:idx + 300]
    answers = re.findall(r"YES!|NO!|Yes|No", chunk)
    if len(answers) >= 3:
        norm = lambda a: ("YES!" if a == "YES!" else "NO!" if a == "NO!"
                          else "yes" if a == "Yes" else "no")
        odds["bad"]  = norm(answers[0])
        odds["even"] = norm(answers[1])
        odds["good"] = norm(answers[2])
    return odds


def extract_difficulty(region):
    """
    The Difficulty field is a number 1-10. pdftotext typically renders it as a
    standalone digit near the top of the card. Heuristic: first single-digit
    number 1-10 that isn't in a labelled context.
    """
    # Strip out lines that contain known labels — the remaining numbers are
    # less likely to be Likely Odds tier indicators.
    candidates = re.findall(r"(?<![A-Za-z0-9])(\d{1,2})(?![A-Za-z0-9])", region)
    for c in candidates:
        n = int(c)
        if 1 <= n <= 10:
            return n
    return None


def extract_dice(region):
    """
    Dice values: d4, d6, d8, d10, d12, d20, d100tens, d100units. The PnP
    layout positions these around the dice-wheel artwork, so they appear as
    a cluster of small numbers without labels. We collect numbers that are
    plausible for each die and return what we can.
    """
    # Greedy: collect all standalone numbers, in order of appearance.
    nums = [int(n) for n in re.findall(r"(?<![A-Za-z])(\d{1,3})(?![A-Za-z])",
                                       region)]
    dice = {"d4": None, "d6": None, "d8": None, "d10": None, "d12": None,
            "d20": None, "d100tens": None, "d100units": None}
    # Heuristic: look for the first occurrence of values in valid ranges.
    consumed = set()
    def take(low, high):
        for i, n in enumerate(nums):
            if i in consumed: continue
            if low <= n <= high:
                consumed.add(i); return n
        return None
    dice["d4"]  = take(1, 4)
    dice["d6"]  = take(1, 6)
    dice["d8"]  = take(1, 8)
    dice["d10"] = take(0, 9) or take(1, 10)
    dice["d12"] = take(1, 12)
    dice["d20"] = take(1, 20)
    dice["d100tens"]  = take(0, 9)
    dice["d100units"] = take(0, 9)
    return dice


def extract_after_label(region, label, end_labels=None):
    """
    Return the text after `label`, up to the next labeled field. Does NOT
    stop at blank lines, because GMA card layouts space label and content
    apart with several blank lines.
    """
    end_labels = end_labels or LABELED_FIELDS
    idx = region.find(label)
    if idx == -1:
        return None
    after = region[idx + len(label):]
    # Strip leading punctuation/whitespace that often follows a label
    after = re.sub(r"^[\s:—\-]+", "", after)
    # Stop only at next labeled field
    others = [l for l in end_labels if l != label]
    if others:
        end_pat = re.compile(r"\n\s*(?:" + "|".join(re.escape(l) for l in others) + r")")
        m = end_pat.search(after)
        text = after[:m.start()] if m else after
    else:
        text = after
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def extract_names(region):
    text = extract_after_label(region, "Names")
    if not text:
        return None
    # Names are typically 3 capitalized words separated by whitespace.
    tokens = [t.strip() for t in re.split(r"[\s,/]+", text) if t.strip()]
    return tokens[:3] if tokens else None


def extract_belongings(region):
    text = extract_after_label(region, "Belongings")
    if not text:
        return {"category": None, "items": []}
    # Common pattern: "Category: item1, item2, item3" or "Category — item1, item2, item3"
    m = re.match(r"([^:—\-]+)[:—\-]+(.*)", text)
    if m:
        cat = m.group(1).strip()
        items = [i.strip() for i in re.split(r"[,;]", m.group(2)) if i.strip()]
        return {"category": cat or None, "items": items[:3]}
    return {"category": None, "items": [text]}


def extract_virtue_vice(region):
    return {
        "virtue": extract_after_label(region, "Virtue") or None,
        "vice":   extract_after_label(region, "Vice")   or None,
    }


def extract_catalyst(region):
    return extract_after_label(region, "Catalyst")


def extract_location(region):
    return extract_after_label(region, "Location")


def extract_event_phrase(region):
    """
    The Random Event field is three single capitalized words printed as a row
    on the card (no labels). Look for a line that is exactly three
    capitalized alphabetical words and nothing else.

    Caveat: a sensory-snippet line that happens to be three capitalized words
    can match too. If that happens often, prefer scanning only the upper half
    of the region, or set this field to None and fill in by hand.
    """
    # Slash-separated form first (rare).
    m = re.search(r"\b([A-Z][a-z]+)\s*[/|]\s*([A-Z][a-z]+)\s*[/|]\s*([A-Z][a-z]+)",
                  region)
    if m:
        return {"verb": m.group(1), "adjective": m.group(2), "noun": m.group(3)}
    # Three-capitalized-words-on-a-line form (common GMA layout).
    for line in region.splitlines():
        m = re.match(
            r"^\s*([A-Z][a-z]+)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)\s*$",
            line,
        )
        if m:
            return {"verb": m.group(1), "adjective": m.group(2), "noun": m.group(3)}
    return {"verb": None, "adjective": None, "noun": None}


def extract_sensory(region):
    """
    Sensory snippets: 4 short phrases (hear/see/feel/smell). They're typically
    in the middle of the card without labels and are hard to extract reliably
    from text-layout output. Returns nulls — fill in by hand.
    """
    return {"hear": None, "see": None, "feel": None, "smell": None}


def parse_card(region, card_id):
    """Parse one card region into the schema dict."""
    odds = extract_likely_odds(region)
    bel  = extract_belongings(region)
    vv   = extract_virtue_vice(region)
    return {
        "id":         card_id,
        "difficulty": extract_difficulty(region),
        "odds":       odds,
        "dice":       extract_dice(region),
        "rune":       None,    # icon — fill in by hand
        "element":    None,    # icon — fill in by hand
        "event":      extract_event_phrase(region),
        "sensory":    extract_sensory(region),
        "tags":       None,    # icons — fill in by hand
        "scatter":    None,    # icon — fill in by hand
        "belongings": bel,
        "names":      extract_names(region),
        "catalyst":   extract_catalyst(region),
        "location":   extract_location(region),
        "virtue":     vv["virtue"],
        "vice":       vv["vice"],
    }


# --- Driver -----------------------------------------------------------------

def fill_rates(cards):
    """Compute per-field non-null rates for diagnostics."""
    if not cards:
        return {}
    keys = ["difficulty", "odds.bad", "odds.even", "odds.good",
            "dice.d4", "dice.d6", "dice.d20", "event.verb",
            "belongings.category", "names", "catalyst", "location",
            "virtue", "vice"]
    counts = {k: 0 for k in keys}
    for c in cards:
        if c.get("difficulty") is not None: counts["difficulty"] += 1
        for t in ("bad", "even", "good"):
            if (c.get("odds") or {}).get(t): counts[f"odds.{t}"] += 1
        for d in ("d4", "d6", "d20"):
            if (c.get("dice") or {}).get(d) is not None: counts[f"dice.{d}"] += 1
        if (c.get("event") or {}).get("verb"): counts["event.verb"] += 1
        if (c.get("belongings") or {}).get("category"): counts["belongings.category"] += 1
        if c.get("names"):    counts["names"] += 1
        if c.get("catalyst"): counts["catalyst"] += 1
        if c.get("location"): counts["location"] += 1
        if c.get("virtue"):   counts["virtue"] += 1
        if c.get("vice"):     counts["vice"] += 1
    return {k: f"{v}/{len(cards)}" for k, v in counts.items()}


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    debug = "--debug" in flags

    if not args:
        print("usage: python extract.py raw.txt [--debug] [> ../cards.js]",
              file=sys.stderr)
        return 2

    path = Path(args[0])
    raw = path.read_text(encoding="utf-8", errors="replace")
    pages = raw.split("\f")

    cards = []
    skipped = 0
    first_card_dumped = False
    for page_idx, page in enumerate(pages, 1):
        if not is_card_page(page):
            skipped += 1
            continue
        regions = split_into_card_regions(page)
        if not regions:
            print(f"warn: page {page_idx} produced 0 regions; skipping",
                  file=sys.stderr)
            continue
        if debug and not first_card_dumped:
            for ri, region in enumerate(regions):
                print(f"=== DEBUG: page {page_idx} region {ri+1}/6 ===",
                      file=sys.stderr)
                print(region or "(empty)", file=sys.stderr)
                print("---", file=sys.stderr)
            print("=== END DEBUG ===\n", file=sys.stderr)
            first_card_dumped = True
        for region in regions:
            cards.append(parse_card(region, len(cards) + 1))

    rates = fill_rates(cards)
    print(f"info: parsed {len(cards)} cards from {len(pages)} pages "
          f"({skipped} pages skipped as front-matter).", file=sys.stderr)
    print("info: per-field fill rates (non-null / total):", file=sys.stderr)
    for k, v in rates.items():
        print(f"      {k:24s} {v}", file=sys.stderr)
    print("info: rune / element / tags / scatter / sensory are left null — "
          "those are icons on the printed cards. Fill in by hand.",
          file=sys.stderr)

    # Force stdout to UTF-8 so non-ASCII chars (curly quotes, replacement
    # markers) don't crash on Windows' default cp1252 console codec.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, TypeError):
        pass

    # Strip U+FFFD replacement characters that pdftotext sometimes leaves in
    # for unrenderable glyphs — they're noise for text fields.
    def scrub(obj):
        if isinstance(obj, str):
            return obj.replace("�", "").strip() or None
        if isinstance(obj, list):
            return [scrub(x) for x in obj]
        if isinstance(obj, dict):
            return {k: scrub(v) for k, v in obj.items()}
        return obj
    cards = [scrub(c) for c in cards]

    # Emit the JS file.
    sys.stdout.write("/* GMA / cards.js — generated by extract.py */\n")
    sys.stdout.write("/* edit freely; rune / element / tags / scatter / "
                     "sensory need manual fill-in from the PDF */\n")
    sys.stdout.write("window.GMA_CARDS = ")
    sys.stdout.write(json.dumps(cards, indent=2, ensure_ascii=False))
    sys.stdout.write(";\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
