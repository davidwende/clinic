// Diagnoses / Procedures / Patients lookup -- equivalent of
// DiagProc/diag_proc.py's DiagProcWindow. Not tied to a patient: pick a
// diagnosis and/or a procedure, see the union of patients who have either
// (DiagProcWindow.update_patients_list adds both result sets into one
// set(), not an intersection).
(() => {
  const state = { diagnosis: null, procedure: null };
  let allDiagnoses = [];
  let allProcedures = [];

  const els = {
    message: document.getElementById("form-message"),
    diagFilter: document.getElementById("diag-filter"),
    procFilter: document.getElementById("proc-filter"),
    diagList: document.getElementById("diag-list"),
    procList: document.getElementById("proc-list"),
    patientList: document.getElementById("patient-list"),
  };

  function showMessage(text, kind) {
    els.message.textContent = text || "";
    els.message.className = "form-message" + (kind ? " " + kind : "");
  }

  async function apiFetch(url) {
    const res = await fetch(url);
    if (res.status === 401) {
      window.location.href = "/login";
      throw new Error("Not authenticated");
    }
    return res;
  }

  function renderList(container, items, selected, onSelect) {
    container.innerHTML = "";
    for (const item of items) {
      const li = document.createElement("li");
      li.textContent = item;
      if (item === selected) li.classList.add("selected");
      li.addEventListener("click", () => onSelect(item));
      container.appendChild(li);
    }
  }

  function renderDiagList() {
    const q = els.diagFilter.value.toLowerCase();
    const filtered = allDiagnoses.filter((d) => d.toLowerCase().includes(q));
    renderList(els.diagList, filtered, state.diagnosis, selectDiagnosis);
  }

  function renderProcList() {
    const q = els.procFilter.value.toLowerCase();
    const filtered = allProcedures.filter((p) => p.toLowerCase().includes(q));
    renderList(els.procList, filtered, state.procedure, selectProcedure);
  }

  function selectDiagnosis(name) {
    state.diagnosis = name;
    renderDiagList();
    updatePatients();
  }

  function selectProcedure(name) {
    state.procedure = name;
    renderProcList();
    updatePatients();
  }

  async function updatePatients() {
    els.patientList.innerHTML = "";
    if (!state.diagnosis && !state.procedure) return;
    const params = new URLSearchParams();
    if (state.diagnosis) params.set("diagnosis", state.diagnosis);
    if (state.procedure) params.set("procedure", state.procedure);
    const res = await apiFetch(`/api/diag-proc/patients?${params.toString()}`);
    if (!res.ok) {
      showMessage("Could not load patients.", "error");
      return;
    }
    const patients = await res.json();
    for (const p of patients) {
      const li = document.createElement("li");
      li.textContent = `${p.fname} ${p.surname} (${p.tz})`;
      els.patientList.appendChild(li);
    }
    showMessage("");
  }

  els.diagFilter.addEventListener("input", renderDiagList);
  els.procFilter.addEventListener("input", renderProcList);

  async function init() {
    const [diagRes, procRes] = await Promise.all([apiFetch("/api/diagnoses"), apiFetch("/api/procedures")]);
    allDiagnoses = await diagRes.json();
    allProcedures = await procRes.json();
    renderDiagList();
    renderProcList();
  }

  init();
})();
