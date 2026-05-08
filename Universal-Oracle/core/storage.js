/* Universal-Oracle / core / storage.js
   Namespaced localStorage save/load. Each app supplies its own namespace string;
   keys live under `oracle.<namespace>.v1`. */
(function () {
  function key(ns) { return "oracle." + ns + ".v1"; }

  function load(ns, defaults) {
    try {
      const raw = localStorage.getItem(key(ns));
      const parsed = raw ? JSON.parse(raw) : {};
      return Object.assign({}, defaults || {}, parsed);
    } catch (_) {
      return Object.assign({}, defaults || {});
    }
  }

  function save(ns, state) {
    try { localStorage.setItem(key(ns), JSON.stringify(state)); }
    catch (_) { /* quota or private mode — silently drop */ }
  }

  function clear(ns) {
    try { localStorage.removeItem(key(ns)); } catch (_) {}
  }

  window.Oracle = window.Oracle || {};
  window.Oracle.storage = { load, save, clear, key };
})();
