# Populating cards.js

The app ships with an empty deck. You own the PnP — you fill the deck in.

## Two-step extraction (recommended)

You need `pdftotext` (Poppler) installed locally; on Windows it's already in your `pdftotext` install (you can confirm with `where pdftotext` from PowerShell or `which pdftotext` in Bash).

```
cd D:\Games\@BOARD\@Systems\Solo\Gamemaster
pdftotext -layout GMA_Base_PnP_5_9_15.pdf raw.txt
python app\extract\extract.py raw.txt > app\cards.js
```

That produces `app\cards.js` with `window.GMA_CARDS = [...]` populated. Open `app\index.html` and the deck is ready.

## What gets extracted automatically

| Field | Extracted? | Notes |
|---|---|---|
| Difficulty (1–10) | ✓ | First standalone 1–10 digit per card region. |
| Likely Odds (Bad / Even / Good) | ✓ | Reads the YES! / Yes / No / NO! values after each "Likely Odds" label. |
| Dice (d4–d100) | ✓ partial | Heuristic — values are unlabeled on the card; verify a few cards by hand. |
| Random Event (verb / adj / noun) | ✓ best-effort | Looks for `Capital / Capital / Capital` triplets. May miss some. |
| Belongings (category + 3 items) | ✓ | After the "Belongings" label. |
| Names (3 names) | ✓ | After the "Names" label. |
| Catalyst | ✓ | After the "Catalyst" label. |
| Location | ✓ | After the "Location" label. |
| Virtue & Vice | ✓ | After the "Virtue" / "Vice" labels. |
| **Norse Rune** | ✗ | Icon on the printed card — fill in by hand. |
| **Element** | ✗ | Icon — fill in by hand (Earth / Fire / Air / Water). |
| **Tag Symbols** (3 of 10) | ✗ | Icons — fill in by hand. |
| **Scatter Die** (direction + hit/miss) | ✗ | Icon — fill in by hand. |
| **Sensory Snippets** (hear / see / feel / smell) | ✗ | Free text near unlabeled icons — heuristic is unreliable; fill in by hand. |

The icon-based fields don't survive `pdftotext` extraction because they're rendered as images on the printed PnP. You can fill them in over time as you use the deck — empty fields just show "—" in the app.

## The card schema (full)

```js
window.GMA_CARDS = [
  {
    id:         1,
    difficulty: 5,
    odds: {
      bad:  "no",     // "YES!" | "yes" | "no" | "NO!"
      even: "yes",
      good: "YES!"
    },
    dice: {
      d4: 3, d6: 5, d8: 7, d10: 9, d12: 11, d20: 17,
      d100tens: 6, d100units: 7
    },
    rune:    "Ansuz",      // one of 24 Elder Futhark
    element: "Fire",       // "Earth" | "Fire" | "Air" | "Water"
    event:   { verb: "Run", adjective: "Hidden", noun: "Promise" },
    sensory: {
      hear:  "Distant bells",
      see:   "A moving shape",
      feel:  "Cold draft",
      smell: "Old smoke"
    },
    tags:    ["Tower", "Crown", "Heart"],   // 3 of 10
    scatter: { dir: "NE", hit: false },     // dir: N/NE/E/SE/S/SW/W/NW
    belongings: {
      category: "Tools",
      items:    ["a knife", "twine", "a flint"]
    },
    names:    ["Aerin", "Brynn", "Caor"],
    catalyst: "An old debt is called in publicly",
    location: "An abandoned watchtower",
    virtue:   "Charity",
    vice:     "Greed"
  },
  // ...more cards
];
```

Any field can be `null` (empty string for text fields also OK) — the app shows "—" in that field's panel.

## Hand-editing

You don't have to use the extractor. If you'd rather transcribe a few cards at a time as you play, just open `cards.js` in any editor and add objects to the `GMA_CARDS` array. The app reads the file fresh on each page reload.

## Sample card

Easiest way to check the app is working: paste this into `cards.js` (replacing `window.GMA_CARDS = [];`) and reload the app.

```js
window.GMA_CARDS = [
  {
    id: 1,
    difficulty: 5,
    odds: { bad: "no", even: "yes", good: "YES!" },
    dice: { d4: 2, d6: 4, d8: 6, d10: 7, d12: 9, d20: 14, d100tens: 5, d100units: 8 },
    rune: "Ansuz",
    element: "Air",
    event: { verb: "Discover", adjective: "Ancient", noun: "Promise" },
    sensory: { hear: "—", see: "—", feel: "—", smell: "—" },
    tags: ["Tower", "Crown", "Heart"],
    scatter: { dir: "NE", hit: false },
    belongings: { category: "Travel kit", items: ["—", "—", "—"] },
    names: ["—", "—", "—"],
    catalyst: "—",
    location: "—",
    virtue: "Wisdom",
    vice:   "Pride"
  }
];
```

## If the extractor breaks

The 2015 PnP layout is hardcoded into `extract.py` (3 columns × 2 rows of cards per page, with "Likely Odds" as the column-anchor marker). Other PnP versions or revisions may align differently. If extraction produces blanks or wrong slots, look at the **Tunables** block at the top of `extract.py` and adjust `CARD_MARKER`, `CARDS_PER_PAGE`, etc.

You can also run the extractor on a single page to debug:

```
pdftotext -layout -f 35 -l 35 GMA_Base_PnP_5_9_15.pdf - | python app\extract\extract.py /dev/stdin > test.js
```

## Mechanics credit

The GameMaster's Apprentice is by Nathan Rockwood / Larcenous Designs. This codebase is a local front-end for a deck you already own; it ships empty and never bundles deck content.
