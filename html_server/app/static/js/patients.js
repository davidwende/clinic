// Patients page -- equivalent of MainWindow's patient panel
// (Application_Main/main.py) rebuilt against /api/patients.
(() => {
  const state = { selectedTz: null };
  // Persists the current patient across a round trip to Visits/Blood/Past
  // History and back, so returning to the list doesn't lose the "ongoing
  // patient" context. sessionStorage (not localStorage) so it clears when
  // the tab/browser closes rather than sticking around into a new session.
  const STORAGE_KEY = "clinic_selected_tz";

  const els = {
    search: document.getElementById("search"),
    rows: document.getElementById("patient-rows"),
    total: document.getElementById("total-count"),
    dateFrom: document.getElementById("date-from"),
    dateTo: document.getElementById("date-to"),
    visitsCount: document.getElementById("visits-count"),
    procCount: document.getElementById("proc-count"),
    label: document.getElementById("current-patient-label"),
    message: document.getElementById("form-message"),
    tz: document.getElementById("f-tz"),
    fname: document.getElementById("f-fname"),
    surname: document.getElementById("f-surname"),
    email: document.getElementById("f-email"),
    phone: document.getElementById("f-phone"),
    dob: document.getElementById("f-dob"),
    male: document.getElementById("f-male"),
    female: document.getElementById("f-female"),
    smoker: document.getElementById("f-smoker"),
    consent: document.getElementById("f-consent"),
  };

  function todayISO() {
    return new Date().toISOString().slice(0, 10);
  }

  function showMessage(text, kind) {
    els.message.textContent = text || "";
    els.message.className = "form-message" + (kind ? " " + kind : "");
  }

  async function apiFetch(url, options) {
    const res = await fetch(url, options);
    if (res.status === 401) {
      window.location.href = "/login";
      throw new Error("Not authenticated");
    }
    return res;
  }

  function errorsToMessage(detail) {
    if (!detail) return "Request failed.";
    if (typeof detail === "string") return detail;
    return Object.values(detail).join(" ");
  }

  // --- Patient list / search --------------------------------------------

  let searchTimer = null;
  els.search.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadPatients, 200); // mirrors the 200ms Qt debounce
  });

  async function loadPatients() {
    const q = encodeURIComponent(els.search.value.trim());
    const res = await apiFetch(`/api/patients?q=${q}`);
    const rows = await res.json();
    renderRows(rows);
    els.total.textContent = String(rows.length);
  }

  function renderRows(rows) {
    els.rows.innerHTML = "";
    for (const p of rows) {
      const tr = document.createElement("tr");
      tr.dataset.tz = p.tz;
      if (p.tz === state.selectedTz) tr.classList.add("selected");
      tr.innerHTML = `<td>${p.visit_count}</td><td>${p.tz}</td><td>${escapeHtml(p.fname)}</td><td>${escapeHtml(p.surname)}</td>`;
      tr.addEventListener("click", () => selectPatient(p.tz));
      els.rows.appendChild(tr);
    }
  }

  function escapeHtml(s) {
    const div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  async function selectPatient(tz) {
    const res = await apiFetch(`/api/patients/${encodeURIComponent(tz)}`);
    if (!res.ok) {
      showMessage("Could not load patient.", "error");
      return;
    }
    const p = await res.json();
    state.selectedTz = p.tz;
    sessionStorage.setItem(STORAGE_KEY, p.tz);
    fillForm(p);
    els.label.textContent = `${p.tz}   ${p.fname} ${p.surname}`;
    showMessage("");
    [...els.rows.children].forEach((tr) => {
      const isSelected = tr.dataset.tz === tz;
      tr.classList.toggle("selected", isSelected);
      if (isSelected) tr.scrollIntoView({ block: "nearest" });
    });
  }

  function fillForm(p) {
    els.tz.value = p.tz;
    els.fname.value = p.fname;
    els.surname.value = p.surname;
    els.email.value = p.email;
    els.phone.value = p.phone;
    els.dob.value = p.dob;
    els.male.checked = p.male;
    els.female.checked = !p.male;
    els.smoker.checked = p.smoker;
    els.consent.checked = p.consent;
  }

  function readForm() {
    return {
      tz: els.tz.value.trim(),
      fname: els.fname.value.trim(),
      surname: els.surname.value.trim(),
      email: els.email.value.trim(),
      phone: els.phone.value.trim(),
      dob: els.dob.value,
      male: els.male.checked,
      smoker: els.smoker.checked,
      consent: els.consent.checked,
    };
  }

  function clearForm() {
    state.selectedTz = null;
    sessionStorage.removeItem(STORAGE_KEY);
    els.tz.value = "";
    els.fname.value = "";
    els.surname.value = "";
    els.email.value = "";
    els.phone.value = "";
    els.dob.value = "";
    els.male.checked = false;
    els.female.checked = false;
    els.smoker.checked = false;
    els.consent.checked = false;
    els.label.textContent = "No patient selected";
    showMessage("");
    [...els.rows.children].forEach((tr) => tr.classList.remove("selected"));
  }

  // --- Save / Modify (with the same "invalid TZ, save anyway?" flow as
  // the Qt app's check_new_patient confirmation dialog) -------------------

  async function submitPatient(isCreate) {
    const body = readForm();
    const url = isCreate ? "/api/patients" : `/api/patients/${encodeURIComponent(state.selectedTz)}`;
    const method = isCreate ? "POST" : "PUT";

    let forceTz = false;
    for (let attempt = 0; attempt < 2; attempt++) {
      const qs = forceTz ? "?force_tz=true" : "";
      const res = await apiFetch(url + qs, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        const p = await res.json();
        if (isCreate) {
          clearForm();
        } else {
          state.selectedTz = p.tz;
          sessionStorage.setItem(STORAGE_KEY, p.tz);
          els.label.textContent = `${p.tz}   ${p.fname} ${p.surname}`;
        }
        showMessage(`Patient ${p.fname} ${p.surname} saved.`, "success");
        await loadPatients();
        return;
      }
      const payload = await res.json().catch(() => ({}));
      const detail = payload.detail;
      if (
        !forceTz &&
        detail &&
        typeof detail === "object" &&
        detail.tz &&
        detail.tz.includes("force_tz")
      ) {
        if (confirm("Invalid TZ number! Do you want to proceed anyway?")) {
          forceTz = true;
          continue;
        }
      }
      showMessage(errorsToMessage(detail), "error");
      return;
    }
  }

  document.getElementById("btn-save").addEventListener("click", () => submitPatient(true));
  document.getElementById("btn-modify").addEventListener("click", () => {
    if (!state.selectedTz) {
      showMessage("Choose a patient first.", "error");
      return;
    }
    submitPatient(false);
  });
  document.getElementById("btn-clear").addEventListener("click", clearForm);
  document.getElementById("btn-refresh").addEventListener("click", () => {
    loadPatients();
    loadSummary();
  });

  document.getElementById("btn-delete").addEventListener("click", async () => {
    if (!state.selectedTz) {
      showMessage("Choose a patient first.", "error");
      return;
    }
    if (!confirm("Really delete the patient?")) return;
    const res = await apiFetch(`/api/patients/${encodeURIComponent(state.selectedTz)}`, {
      method: "DELETE",
    });
    if (res.status === 204) {
      showMessage("Patient deleted.", "success");
      clearForm();
      await loadPatients();
    } else {
      const payload = await res.json().catch(() => ({}));
      showMessage(errorsToMessage(payload.detail) || "Cannot delete patient with visits!", "error");
    }
  });

  document.getElementById("btn-history").addEventListener("click", () => {
    if (!state.selectedTz) {
      showMessage("Choose a patient first.", "error");
      return;
    }
    window.location.href = `/patients/${encodeURIComponent(state.selectedTz)}/history`;
  });

  document.getElementById("btn-visits").addEventListener("click", () => {
    if (!state.selectedTz) {
      showMessage("Choose a patient first.", "error");
      return;
    }
    window.location.href = `/patients/${encodeURIComponent(state.selectedTz)}/visits`;
  });

  document.getElementById("btn-blood").addEventListener("click", () => {
    if (!state.selectedTz) {
      showMessage("Choose a patient first.", "error");
      return;
    }
    window.location.href = `/patients/${encodeURIComponent(state.selectedTz)}/blood`;
  });

  document.getElementById("btn-diag-proc").addEventListener("click", () => {
    // Unlike the other nav buttons, this one isn't patient-specific --
    // matches Qt's show_diag_proc(), which opens DiagProcWindow with no
    // arguments and no "choose a patient first" guard.
    window.location.href = "/diag-proc";
  });

  document.getElementById("btn-modify-tz").addEventListener("click", async () => {
    if (!state.selectedTz) {
      showMessage("Choose a patient first.", "error");
      return;
    }
    const newTz = prompt("Enter new TZ number:", state.selectedTz);
    if (newTz === null) return;
    const res = await apiFetch(`/api/patients/${encodeURIComponent(state.selectedTz)}/tz`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ new_tz: newTz.trim() }),
    });
    if (res.ok) {
      const p = await res.json();
      showMessage("TZ modified successfully.", "success");
      state.selectedTz = p.tz;
      sessionStorage.setItem(STORAGE_KEY, p.tz);
      fillForm(p);
      els.label.textContent = `${p.tz}   ${p.fname} ${p.surname}`;
      await loadPatients();
    } else {
      const payload = await res.json().catch(() => ({}));
      showMessage(errorsToMessage(payload.detail), "error");
    }
  });

  // --- Visit / procedure date-range summary -------------------------------

  async function loadSummary() {
    const from = els.dateFrom.value;
    const to = els.dateTo.value;
    if (!from || !to) return;
    const res = await apiFetch(`/api/patients/summary?from=${from}&to=${to}`);
    if (!res.ok) return;
    const s = await res.json();
    els.visitsCount.textContent = String(s.visits);
    els.procCount.textContent = String(s.visits_with_procedures);
  }

  els.dateFrom.addEventListener("change", loadSummary);
  els.dateTo.addEventListener("change", loadSummary);

  // --- Restore the ongoing patient after a round trip to Visits/Blood/
  // Past History (or any other return to this page) ------------------------

  function restoreSelection() {
    const storedTz = sessionStorage.getItem(STORAGE_KEY);
    if (!storedTz) return;
    const stillListed = [...els.rows.children].some((tr) => tr.dataset.tz === storedTz);
    if (stillListed) {
      selectPatient(storedTz);
    } else {
      // e.g. deleted, or filtered out by a leftover search term -- don't
      // keep pointing at a patient that's no longer selectable.
      sessionStorage.removeItem(STORAGE_KEY);
    }
  }

  // --- Init ----------------------------------------------------------------

  els.dateFrom.value = todayISO();
  els.dateTo.value = todayISO();
  loadPatients().then(restoreSelection);
  loadSummary();
})();
