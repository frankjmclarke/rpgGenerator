/* Universal-Oracle / core / oracle.js
   Yes/No with odds (BAD/EVEN/GOOD), chaos factor, scene test, random event.
   Adapted from Solo-System Mythic Variations 2 logic (chaosThreshold, testScene,
   drawRandomEvent at app/index.html ~lines 1163-1260). */
(function () {
  // ---------- yes / no with odds ----------
  /* Three-tier probability with critical results.
     A 1-23 reference is rolled and compared to threshold = base + odds offset.
       BAD  = -6
       EVEN =  0
       GOOD = +6
     Critical doubles (11 or 22) ≤ threshold escalate YES → YES! and NO → NO!. */
  const ODDS_OFFSET = { bad: -6, even: 0, good: +6 };
  const DEFAULT_BASE = 12;

  function ratingOffset(odds) {
    return ODDS_OFFSET[odds] != null ? ODDS_OFFSET[odds] : 0;
  }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function threshold(base, odds) {
    return clamp(base + ratingOffset(odds), 0, 23);
  }
  function isCritical(ref) { return ref === 11 || ref === 22; }

  function yesNo(odds, base) {
    base = base == null ? DEFAULT_BASE : base;
    const ref = 1 + window.Oracle.rand(23);
    const t = threshold(base, odds);
    const yes = ref <= t;
    const critical = isCritical(ref) && ref <= base;
    let answer;
    if (yes && critical)      answer = "YES!";
    else if (yes)             answer = "yes";
    else if (!yes && critical) answer = "NO!";
    else                       answer = "no";
    return { answer, yes, critical, ref, threshold: t, odds, base };
  }

  // ---------- scene test ----------
  /* Mythic-style scene test: draw a 1-23 reference vs current chaos.
       ref >  chaos        → expected (scene plays as planned)
       ref <= chaos & odd  → modified (one twist)
       ref <= chaos & even → interrupted (different scene; auto-fire random event) */
  function sceneTest(chaos) {
    const ref = 1 + window.Oracle.rand(23);
    let outcome, interp;
    if (ref > chaos) {
      outcome = "expected";
      interp = "Proceed with your scene as planned.";
    } else if (ref % 2 === 1) {
      outcome = "modified";
      interp = "Same scene, but something is different. Add one twist.";
    } else {
      outcome = "interrupted";
      interp = "A different scene unfolds entirely.";
    }
    return { ref, chaos, outcome, interp };
  }

  // ---------- generic random-event keyword draw ----------
  /* Returns one entry from each of the four keyword arrays passed in.
     Used by the RPG and Strategic apps for verb/adj/noun-style prompts. */
  function randomEvent(focusList, subjectList, actionList, descriptionList) {
    const pick = window.Oracle.pick;
    return {
      focus:       focusList       ? pick(focusList)       : null,
      subject:     subjectList     ? pick(subjectList)     : null,
      action:      actionList      ? pick(actionList)      : null,
      description: descriptionList ? pick(descriptionList) : null,
    };
  }

  window.Oracle = window.Oracle || {};
  window.Oracle.yesNo = yesNo;
  window.Oracle.sceneTest = sceneTest;
  window.Oracle.randomEvent = randomEvent;
  window.Oracle.threshold = threshold;
  window.Oracle.isCritical = isCritical;
  window.Oracle.ODDS_OFFSET = ODDS_OFFSET;
})();
