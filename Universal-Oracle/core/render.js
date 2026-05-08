/* Universal-Oracle / core / render.js
   Shared render helpers: $-shorthand, escapeHtml, banner, modal gallery. */
(function () {
  const $ = (id) => document.getElementById(id);

  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;"
    }[c]));
  }

  /* Banner: a wide pill above the card area showing the latest oracle answer.
     Element conventions: container with id "banner", innerHTML driven here. */
  function setBanner(label, answer, kind, extra) {
    const b = $("banner"); if (!b) return;
    b.classList.remove("empty");
    b.classList.remove("yes", "no", "decisive");
    if (kind) b.classList.add(...kind.split(" "));
    b.innerHTML =
      `<div class="b-label">${escapeHtml(label)}</div>` +
      `<div class="b-answer">${answer}</div>` +
      (extra ? `<div class="b-extra">${extra}</div>` : "");
  }
  function clearBanner(placeholder) {
    const b = $("banner"); if (!b) return;
    b.className = "banner empty";
    b.textContent = placeholder || "Click an action above.";
  }

  /* Modal gallery — shows every card in a deck on demand.
     Caller supplies a render function that turns a single card into HTML. */
  function openGallery(cards, renderOne, title) {
    let dlg = $("oracle-gallery");
    if (!dlg) {
      dlg = document.createElement("dialog");
      dlg.id = "oracle-gallery";
      dlg.innerHTML =
        `<button class="x" onclick="this.closest('dialog').close()">close</button>` +
        `<h2 id="oracle-gallery-title"></h2>` +
        `<div id="oracle-gallery-grid" class="gallery-grid"></div>`;
      document.body.appendChild(dlg);
    }
    $("oracle-gallery-title").textContent = title || "Gallery";
    $("oracle-gallery-grid").innerHTML = cards.map(renderOne).join("");
    dlg.showModal();
  }

  window.Oracle = window.Oracle || {};
  window.Oracle.$ = $;
  window.Oracle.escapeHtml = escapeHtml;
  window.Oracle.setBanner = setBanner;
  window.Oracle.clearBanner = clearBanner;
  window.Oracle.openGallery = openGallery;
})();
