/* Universal-Oracle / core / deck.js
   Generic Fisher-Yates deck with draw, discard, and auto-reshuffle.
   Lifted from Solo-System app/index.html lines 825-849. */
(function () {
  class Deck {
    constructor(name, cards) {
      this.name = name;
      this.draw_pile = [...cards];
      this.discard = [];
      this.shuffle();
    }
    shuffle() {
      const all = [...this.draw_pile, ...this.discard];
      for (let i = all.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [all[i], all[j]] = [all[j], all[i]];
      }
      this.draw_pile = all;
      this.discard = [];
    }
    draw() {
      if (this.draw_pile.length === 0) this.shuffle();
      const card = this.draw_pile.pop();
      this.discard.push(card);
      return card;
    }
    remaining() { return this.draw_pile.length; }
  }

  function rand(n)  { return Math.floor(Math.random() * n); }
  function pick(a)  { return a[rand(a.length)]; }
  function pickN(a, n) {
    const pool = [...a];
    const out = [];
    while (out.length < n && pool.length) {
      out.push(pool.splice(rand(pool.length), 1)[0]);
    }
    return out;
  }

  window.Oracle = window.Oracle || {};
  window.Oracle.Deck = Deck;
  window.Oracle.rand = rand;
  window.Oracle.pick = pick;
  window.Oracle.pickN = pickN;
})();
