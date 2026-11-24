// Database backup / restore (admin only -- this script is only included
// on the patients page for admin accounts; the API enforces it too).
//
// Restore needs two separate confirmations because it replaces the whole
// database on the server for every user and every desktop install:
//   1. a warning dialog describing what will happen (Continue / Cancel);
//   2. a final dialog where the word RESTORE must be typed to enable the
//      button.
// The server additionally refuses a restore request that doesn't carry
// ?confirm=RESTORE.
(() => {
  const CONFIRM_WORD = "RESTORE";
  const btnBackup = document.getElementById("btn-db-backup");
  const btnRestore = document.getElementById("btn-db-restore");
  const fileInput = document.getElementById("db-restore-file");
  const message = document.getElementById("db-admin-message");
  if (!btnBackup || !btnRestore) return;

  function showMessage(text, kind) {
    message.textContent = text || "";
    message.className = "form-message" + (kind ? " " + kind : "");
  }

  async function errorText(res) {
    try {
      const body = await res.json();
      if (typeof body.detail === "string") return body.detail;
      return JSON.stringify(body.detail || body);
    } catch {
      return `Request failed (HTTP ${res.status}).`;
    }
  }

  function setBusy(busy) {
    btnBackup.disabled = busy;
    btnRestore.disabled = busy;
  }

  // --- Backup ---------------------------------------------------------------

  btnBackup.addEventListener("click", async () => {
    setBusy(true);
    showMessage("Creating backup…");
    try {
      const res = await fetch("/api/admin/backup");
      if (res.status === 401) { window.location.href = "/login"; return; }
      if (!res.ok) { showMessage(await errorText(res), "error"); return; }
      const disposition = res.headers.get("Content-Disposition") || "";
      const match = disposition.match(/filename="([^"]+)"/);
      const filename = match ? match[1] : "clinic_backup.sql";
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 10000);
      showMessage(`Backup saved as ${filename} (${formatSize(blob.size)}).`, "success");
    } catch (e) {
      showMessage(`Backup failed: ${e.message}`, "error");
    } finally {
      setBusy(false);
    }
  });

  // --- Restore --------------------------------------------------------------

  btnRestore.addEventListener("click", () => {
    showMessage("");
    fileInput.value = ""; // so picking the same file again still fires "change"
    fileInput.click();
  });

  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    const text = await file.text();
    const info = readHeader(text);
    if (!info) {
      showMessage(`"${file.name}" is not a clinic database backup file.`, "error");
      return;
    }

    if (!(await firstConfirm(file, info))) { showMessage("Restore cancelled."); return; }
    if (!(await secondConfirm())) { showMessage("Restore cancelled."); return; }

    setBusy(true);
    showMessage("Restoring database… do not close this page.");
    try {
      const res = await fetch(`/api/admin/restore?confirm=${CONFIRM_WORD}`, {
        method: "POST",
        headers: { "Content-Type": "text/plain; charset=utf-8" },
        body: text,
      });
      if (res.status === 401) { window.location.href = "/login"; return; }
      if (!res.ok) { showMessage(await errorText(res), "error"); return; }
      const result = await res.json();
      const counts = Object.entries(result.tables)
        .map(([t, n]) => `${t}: ${n}`).join(", ");
      showMessage(
        `Database restored from backup created ${result.created || "(unknown)"}. ` +
        `Rows now — ${counts}. The previous database was saved on the server as ` +
        `html_server/data/backups/${result.safety_backup}.`,
        "success",
      );
      // Patient list / selection may have changed completely.
      sessionStorage.removeItem("clinic_selected_tz");
      document.getElementById("btn-clear")?.click();
      document.getElementById("btn-refresh")?.click();
    } catch (e) {
      showMessage(`Restore failed: ${e.message}`, "error");
    } finally {
      setBusy(false);
    }
  });

  function readHeader(text) {
    const lines = text.slice(0, 4096).split(/\r?\n/);
    if (lines[0].trim() !== "-- CLINIC-DB-BACKUP v1") return null;
    const meta = {};
    for (const line of lines.slice(1, 6)) {
      const m = line.match(/^-- (\w+): (.*)$/);
      if (m) meta[m[1]] = m[2];
    }
    return meta;
  }

  function formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  }

  function modal(build) {
    return new Promise((resolve) => {
      const overlay = document.createElement("div");
      overlay.className = "leave-modal-overlay";
      const box = document.createElement("div");
      box.className = "leave-modal-box restore-box";
      overlay.appendChild(box);
      const finish = (value) => {
        document.removeEventListener("keydown", onKey);
        overlay.remove();
        resolve(value);
      };
      const onKey = (e) => { if (e.key === "Escape") finish(false); };
      document.addEventListener("keydown", onKey);
      build(box, finish);
      document.body.appendChild(overlay);
      (box.querySelector("[data-autofocus]") || box.querySelector("button"))?.focus();
    });
  }

  function el(tag, text, cls) {
    const e = document.createElement(tag);
    if (text != null) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  }

  function firstConfirm(file, info) {
    return modal((box, finish) => {
      box.appendChild(el("h3", "Restore database? (step 1 of 2)"));
      box.appendChild(el("p",
        "This will DELETE ALL CURRENT DATA on the server — every patient, visit, " +
        "past history and blood/pulse reading — and replace it with the contents " +
        "of this backup file. It affects every user, including the desktop app."));
      const ul = el("ul");
      ul.appendChild(el("li", `File: ${file.name} (${formatSize(file.size)})`));
      ul.appendChild(el("li", `Backup created: ${info.created || "unknown"}`));
      ul.appendChild(el("li", `Database type: ${info.dialect || "unknown"}`));
      if (info.tables) ul.appendChild(el("li", `Contents: ${info.tables}`));
      box.appendChild(ul);
      box.appendChild(el("p",
        "Anything entered since that backup was made will be lost. A copy of the " +
        "current database is saved on the server automatically before restoring."));
      const row = el("div", null, "button-row");
      const cancel = el("button", "Cancel");
      cancel.type = "button";
      cancel.dataset.autofocus = "";
      cancel.addEventListener("click", () => finish(false));
      const go = el("button", "Continue…", "danger-button");
      go.type = "button";
      go.addEventListener("click", () => finish(true));
      row.append(cancel, go);
      box.appendChild(row);
    });
  }

  function secondConfirm() {
    return modal((box, finish) => {
      box.appendChild(el("h3", "Final confirmation (step 2 of 2)"));
      box.appendChild(el("p",
        `The current database will be overwritten. This cannot be undone from this page. ` +
        `Type ${CONFIRM_WORD} below to confirm.`));
      const input = el("input");
      input.type = "text";
      input.autocomplete = "off";
      input.placeholder = CONFIRM_WORD;
      input.dataset.autofocus = "";
      box.appendChild(input);
      const row = el("div", null, "button-row");
      const cancel = el("button", "Cancel");
      cancel.type = "button";
      cancel.addEventListener("click", () => finish(false));
      const go = el("button", "Overwrite database", "danger-button");
      go.type = "button";
      go.disabled = true;
      input.addEventListener("input", () => { go.disabled = input.value.trim() !== CONFIRM_WORD; });
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !go.disabled) finish(true);
      });
      go.addEventListener("click", () => finish(true));
      row.append(cancel, go);
      box.appendChild(row);
    });
  }
})();
