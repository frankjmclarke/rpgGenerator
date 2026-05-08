/* GMA / cards.js
   Your card deck. This file ships empty; populate it from your own legally-
   owned PnP using `app/extract/extract.py` (see cards-howto.md), or
   hand-edit. Do not commit a populated cards.js to a public repo —
   that redistributes commercial card content.

   Schema per card (see cards-howto.md for full field-by-field detail):
     {
       id:        Number,
       difficulty: Number,
       odds:      { bad, even, good },
       dice:      { d4, d6, d8, d10, d12, d20, d100tens, d100units },
       rune:      String,
       element:   "Earth" | "Fire" | "Air" | "Water",
       event:     { verb, adjective, noun },
       sensory:   { hear, see, feel, smell },
       tags:      [String, String, String],
       scatter:   { dir, hit },
       belongings:{ category, items: [a, b, c] },
       names:     [String, String, String],
       catalyst:  String,
       location:  String,
       virtue:    String,
       vice:      String
     }
*/

window.GMA_CARDS = [];
