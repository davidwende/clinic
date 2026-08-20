// Past History page -- equivalent of Past_History/PastHistory.py's
// PastHistoryForm, rebuilt against /api/patients/{tz}/history.
(() => {
  const tz = document.querySelector(".history-page").dataset.tz;
  const state = { nacs: [], acs: [] };

  const els = {
    message: document.getElementById("form-message"),
    hypertension: document.getElementById("h-hypertension"),
    diabetes: document.getElementById("h-diabetes"),
    blood: document.getElementById("h-blood"),
    bloodDescr: document.getElementById("h-blood-descr"),
    malignancy: document.getElementById("h-malignancy"),
    malignancyDate: document.getElementById("h-malignancy-date"),
    malignancyDetails: document.getElementById("h-malignancy-details"),
    malignancyRemiss: document.getElementById("h-malignancy-remiss"),
    disable: document.getElementById("h-disable"),
    disableDetails: document.getElementById("h-disable-details"),
    operations: document.getElementById("h-operations"),
    trauma: document.getElementById("h-trauma"),
    nacList: document.getElementById("nac-list"),
    nacInput: document.getElementById("nac-input"),
    nacOptions: document.getElementById("nac-options"),
    acList: document.getElementById("ac-list"),
    acInput: document.getElementById("ac-input"),
    acOptions: document.getElementById("ac-options"),
  };

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

  function titleCase(s) {
    return s.replace(/\w\S*/g, (w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase());
  }

  function renderMedList(listEl, items, onDelete) {
    listEl.innerHTML = "";
    items.forEach((item, i) => {
      const li = document.createElement("li");
      const span = document.createElement("span");
      span.textContent = item;
      const del = document.createElement("button");
      del.type = "button";
      del.textContent = "×";
      del.title = "Remove";
      del.addEventListener("click", () => onDelete(i));
      li.appendChild(span);
      li.appendChild(del);
      listEl.appendChild(li);
    });
  }

  function renderNacs() {
    renderMedList(els.nacList, state.nacs, (i) => {
      state.nacs.splice(i, 1);
      renderNacs();
    });
  }

  function renderAcs() {
    renderMedList(els.acList, state.acs, (i) => {
      state.acs.splice(i, 1);
      renderAcs();
    });
  }

  function addMed(input, list, render) {
    const value = titleCase(input.value.trim());
    if (value && !list.includes(value)) {
      list.push(value);
      render();
    }
    input.value = "";
  }

  document.getElementById("btn-add-nac").addEventListener("click", () =>
    addMed(els.nacInput, state.nacs, renderNacs)
  );
  document.getElementById("btn-add-ac").addEventListener("click", () =>
    addMed(els.acInput, state.acs, renderAcs)
  );
  els.nacInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); addMed(els.nacInput, state.nacs, renderNacs); }
  });
  els.acInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); addMed(els.acInput, state.acs, renderAcs); }
  });

  function fillForm(h) {
    els.hypertension.checked = h.hypertension;
    els.diabetes.checked = h.diabetes;
    els.blood.checked = h.blood;
    els.bloodDescr.value = h.blood_descr;
    els.malignancy.checked = h.malignancy;
    els.malignancyDate.value = h.malignancy_date;
    els.malignancyDetails.value = h.malignancy_details;
    els.malignancyRemiss.checked = h.malignancy_remiss;
    els.disable.checked = h.disable;
    els.disableDetails.value = h.disable_details;
    els.operations.value = h.operations;
    els.trauma.value = h.trauma;
    state.nacs = [...h.nacs];
    state.acs = [...h.acs];
    renderNacs();
    renderAcs();
  }

  function readForm() {
    return {
      hypertension: els.hypertension.checked,
      diabetes: els.diabetes.checked,
      blood: els.blood.checked,
      blood_descr: els.bloodDescr.value.trim(),
      malignancy: els.malignancy.checked,
      malignancy_date: els.malignancyDate.value.trim(),
      malignancy_details: els.malignancyDetails.value.trim(),
      malignancy_remiss: els.malignancyRemiss.checked,
      disable: els.disable.checked,
      disable_details: els.disableDetails.value.trim(),
      operations: els.operations.value,
      trauma: els.trauma.value,
      nacs: state.nacs,
      acs: state.acs,
    };
  }

  async function loadHistory() {
    const res = await apiFetch(`/api/patients/${encodeURIComponent(tz)}/history`);
    if (!res.ok) {
      showMessage("Could not load past history.", "error");
      return;
    }
    fillForm(await res.json());
  }

  async function loadOptions(url, datalistEl) {
    const res = await apiFetch(url);
    if (!res.ok) return;
    const items = await res.json();
    datalistEl.innerHTML = "";
    for (const item of items) {
      const opt = document.createElement("option");
      opt.value = item;
      datalistEl.appendChild(opt);
    }
  }

  document.getElementById("btn-save").addEventListener("click", async () => {
    const res = await apiFetch(`/api/patients/${encodeURIComponent(tz)}/history`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(readForm()),
    });
    if (res.ok) {
      fillForm(await res.json());
      showMessage("Patient History was saved.", "success");
    } else {
      const payload = await res.json().catch(() => ({}));
      const detail = payload.detail;
      showMessage(typeof detail === "string" ? detail : "Could not save past history.", "error");
    }
  });

  loadHistory();
  loadOptions("/api/nacs", els.nacOptions);
  loadOptions("/api/acs", els.acOptions);
})();
