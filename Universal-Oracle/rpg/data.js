/* Universal-Oracle / rpg / data.js
   Genre-neutral RPG oracle structures: NPC reaction scale, virtue/vice list.
   Genre-specific content (verbs, names, locations, etc.) lives in rpg/packs/<genre>.js. */

/* 5-step NPC reaction scale, weighted by a 1-23 reference roll. */
const REACTION_SCALE = [
  { range: [1, 3],   key: "hostile",   label: "Hostile",   note: "Open antagonism — refuses, threatens, attacks if cornered." },
  { range: [4, 8],   key: "wary",      label: "Wary",      note: "Defensive. Asks first, decides slow, won't commit to anything." },
  { range: [9, 14],  key: "neutral",   label: "Neutral",   note: "Indifferent. Will hear you out; no preference either way." },
  { range: [15, 20], key: "friendly",  label: "Friendly",  note: "Warm, willing. Offers a small gesture without being asked." },
  { range: [21, 23], key: "helpful",   label: "Helpful",   note: "Goes out of their way. Offers active help, info, or a favour." },
];

function rollReaction() {
  const ref = 1 + window.Oracle.rand(23);
  const slot = REACTION_SCALE.find(s => ref >= s.range[0] && ref <= s.range[1]);
  return { ref, ...slot };
}

/* 12 virtues / 12 vices — genre-neutral character motivation pairs.
   Drawn one of each independently for a Virtue + Vice pairing. */
const VIRTUES = [
  "Charity", "Courage", "Compassion", "Curiosity", "Faith", "Honesty",
  "Honour", "Justice", "Loyalty", "Patience", "Temperance", "Wisdom",
];
const VICES = [
  "Cowardice", "Cruelty", "Envy", "Fear", "Greed", "Gluttony",
  "Lust", "Pride", "Sloth", "Suspicion", "Vanity", "Wrath",
];

/* Names roster mapping — packs supply the actual lists. */
function rollNames(pack, count) {
  const roster = pack.names || {};
  const all = [...(roster.male || []), ...(roster.female || []), ...(roster.neutral || [])];
  if (all.length === 0) return [];
  return window.Oracle.pickN(all, Math.min(count || 3, all.length));
}

window.RPG = {
  REACTION_SCALE,
  rollReaction,
  VIRTUES,
  VICES,
  rollNames,
};
