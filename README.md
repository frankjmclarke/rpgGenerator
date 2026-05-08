# rpgGenerator

Two browser-based oracle apps for solo / GM-less roleplaying. Both run from `file://`, save state to `localStorage`, need no server.

Open `index.html` for the launcher, or jump straight to either app:

- [`Universal-Oracle/rpg/index.html`](Universal-Oracle/rpg/index.html) — **Universal RPG Oracle.** GMA-style oracle with six genre packs (Basic Fantasy, Post-Apocalyptic, Cyberpunk, Weird Horror, Steampunk, Sci-Fi). All content ships in the genre packs — runs out of the box.
- [`Gamemaster/app/index.html`](Gamemaster/app/index.html) — **GMA Local Deck.** Front-end for a personal copy of *The GameMaster's Apprentice* deck. All 14 randomizers, Tension counter, Threads & Characters lists, Quick NPC generator. **Ships with an empty `cards.js`** — supply your own deck data (see below).

## Universal RPG Oracle — features

- Yes/No with odds (BAD/EVEN/GOOD, critical YES! / NO!)
- Verb + Adjective + Noun random event
- NPC reaction (5-step: Hostile / Wary / Neutral / Friendly / Helpful)
- Virtue & Vice motivation pair
- Catalyst (inciting incident) and sensory snippet
- 3 names + location generator
- Genre dropdown switches the active word lists live; selection persists

Each genre pack contains ~50–100 verbs/adjectives/nouns, ~24–30 names per gender, ~30–40 locations, ~30–50 catalysts, and 16–24 sensory entries per channel.

## GMA Local Deck — features

All 14 GMA randomizers (Difficulty / Likely Odds / Dice / Norse Rune / Element / Random Event / Sensory / Tag Symbols / Scatter Die / Belongings / Names / Catalyst / Location / Virtue & Vice), plus:

- **Tension** counter — auto-fires a Random Event at threshold and resets.
- **Threads** and **Characters** lists — persistent app state. When Tension auto-fires, a random active entry is picked to anchor the surprise to story you've already established. Cards have no memory of previous state; the app does.
- **Quick NPC** generator — pulls one card's printed values into a complete ready-to-drop NPC (name, reaction, virtue, vice, belongings, element). Save to Characters with one click.
- **Genre overlay** — six genre packs (same as the Universal RPG Oracle) override the card's printed Random Event / Sensory / Belongings / Names / Location with genre-flavoured picks. Card-mode preserves printed values.

### Populating `Gamemaster/app/cards.js`

You must own the GMA PnP. The repo contains a parser; the deck content lives only on your disk. `cards.js` is git-ignored so a populated version can never be accidentally pushed.

First time:

```
# bootstrap an empty cards.js so the app loads with no deck:
cp Gamemaster/app/cards.example.js Gamemaster/app/cards.js
```

Then, from a directory containing your PnP:

```
pdftotext -layout GMA_Base_PnP_5_9_15.pdf raw.txt
python <path-to-repo>/Gamemaster/app/extract/extract.py raw.txt > <path-to-repo>/Gamemaster/app/cards.js
```

If you have a hand-curated `cards.json` extraction with richer content, merge it in:

```
python app/extract/merge.py
```

See [`Gamemaster/app/cards-howto.md`](Gamemaster/app/cards-howto.md) for the full schema and tuning notes. The auto-extractor handles 9 of the 14 fields well; rune / element / tag symbols / scatter / sensory snippets are icon-based on the printed PnP and don't survive `pdftotext` — fill them in by hand or rely on the app's runtime random fill (dice, element, rune, tags, scatter values are generated at deck load when missing).

## What this repo does NOT contain

To stay clear of redistributing commercial third-party content, this repo deliberately excludes:

- The GameMaster's Apprentice card content (`cards.js`, `cards.json`, source PDFs)
- Other PnP decks the apps were inspired by (Solo-System by Chad Mestdagh; Solo Cards by Ray Gaer)
- Sister apps (`skirmish/`, `strategic/`, `boardgame/`) that bake in those third-party decks

If you legally own those decks, you can populate the corresponding files locally — they're git-ignored.

## Credits

- *The GameMaster's Apprentice* — Nathan Rockwood / Larcenous Designs (the deck this app is a front-end for, and the source of the 14-randomizer schema). [larcenousdesigns.com](https://www.larcenousdesigns.com).
- Mythic GME — the conceptual ancestor of the chaos / scene-test loop generalised in the codebase.
- Solo Cards (Ray Gaer) and Solo System (Chad Mestdagh) — solo-wargaming PnPs that informed the card-based oracle pattern.

## License

MIT — see [LICENSE](LICENSE). Original work in this repo (app code, genre pack content, parser, docs) is MIT licensed. Third-party deck content is **not** in this repo and is not licensed to you by this project.
