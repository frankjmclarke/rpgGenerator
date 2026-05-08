/* GMA / lists.js
   Generic CRUD helpers for the Threads and Characters lists. Both lists
   share the same shape: array of { id, name, notes, archived } entries. */

(function () {
  function genId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  }
  function addEntry(list, name, notes) {
    list.push({
      id: genId(),
      name: (name || "").trim(),
      notes: (notes || "").trim(),
      archived: false,
    });
  }
  function updateEntry(list, id, patch) {
    const i = list.findIndex((e) => e.id === id);
    if (i >= 0) Object.assign(list[i], patch);
  }
  function archiveEntry(list, id, archived) {
    updateEntry(list, id, { archived: archived !== false });
  }
  function deleteEntry(list, id) {
    const i = list.findIndex((e) => e.id === id);
    if (i >= 0) list.splice(i, 1);
  }
  function activeEntries(list) {
    return list.filter((e) => !e.archived);
  }
  function pickActive(list) {
    const active = activeEntries(list);
    if (!active.length) return null;
    return active[Math.floor(Math.random() * active.length)];
  }
  window.GMAListUtils = {
    genId, addEntry, updateEntry, archiveEntry,
    deleteEntry, activeEntries, pickActive,
  };
})();
