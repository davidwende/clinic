// Visits page -- equivalent of Visits/visits.py's VisitForm, rebuilt as a
// data-driven renderer over VISIT_TABS / VISIT_TEXT_TABS (visit_fields.js).
(() => {
  const page = document.querySelector(".visit-page");
  const tz = page.dataset.tz;
  const isAdminUser = page.dataset.role === "admin";

  const registry = {}; // field name -> {get, set, kind}
  const pickerState = {
    procedures: {},
    diagnoses: {},
    selected: { procedures: null, diagnoses: null },
  };
  const pickerRenderers = {}; // kind -> () => void
  const pickerLibraryEls = {}; // kind -> <select>

  let currentDate = null;
  let todayISO = null;
  // Snapshot of gatherFormData() taken right after every load/save, so
  // "has this visit been edited since it was last loaded or saved" can be
  // answered by comparing against the live form instead of tracking a
  // dirty flag on every one of the 250+ fields individually.
  let baselineSnapshot = null;

  const els = {
    dateSelect: document.getElementById("visit-date-select"),
    dateBadge: document.getElementById("visit-date-badge"),
    message: document.getElementById("form-message"),
    tabsNav: document.getElementById("visit-tabs"),
    tabContent: document.getElementById("visit-tab-content"),
    btnSave: document.getElementById("btn-save"),
    btnSaveTop: null, // created in renderTabs(), lives in the sticky tab bar
    btnClear: document.getElementById("btn-clear"),
    btnDelete: document.getElementById("btn-delete"),
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

  // --- Generic field rendering -------------------------------------------

  function renderChildField(container, field) {
    if (field.type === "checkbox") {
      const label = document.createElement("label");
      label.className = "checkbox-label child-field";
      const cb = document.createElement("input");
      cb.type = "checkbox";
      label.append(cb, document.createTextNode(field.label));
      container.appendChild(label);
      registry[field.name] = { kind: "checkbox", get: () => cb.checked, set: (v) => { cb.checked = !!v; } };
      return { setEnabled: (e) => { cb.disabled = !e; }, reset: () => { cb.checked = false; } };
    }
    if (field.type === "text") {
      const input = document.createElement("input");
      input.type = "text";
      input.className = "child-field";
      if (field.label) input.placeholder = field.label;
      container.appendChild(input);
      registry[field.name] = { kind: "text", get: () => input.value, set: (v) => { input.value = v || ""; } };
      return { setEnabled: (e) => { input.disabled = !e; }, reset: () => { input.value = ""; } };
    }
    if (field.type === "radio_bool") {
      const span = document.createElement("span");
      span.className = "radio-inline child-field";
      const trueRadio = document.createElement("input");
      const falseRadio = document.createElement("input");
      const trueId = "r_" + field.name + "_true";
      const falseId = "r_" + field.name + "_false";
      trueRadio.type = "radio"; trueRadio.name = field.name; trueRadio.id = trueId;
      falseRadio.type = "radio"; falseRadio.name = field.name; falseRadio.id = falseId;
      const trueLabel = document.createElement("label");
      trueLabel.htmlFor = trueId; trueLabel.textContent = field.trueLabel;
      const falseLabel = document.createElement("label");
      falseLabel.htmlFor = falseId; falseLabel.textContent = field.falseLabel;
      span.append(trueRadio, trueLabel, falseRadio, falseLabel);
      container.appendChild(span);
      registry[field.name] = {
        kind: "radio_bool",
        get: () => trueRadio.checked,
        set: (v) => { trueRadio.checked = !!v; falseRadio.checked = !v; },
      };
      return {
        setEnabled: (e) => { trueRadio.disabled = !e; falseRadio.disabled = !e; },
        reset: () => { trueRadio.checked = false; falseRadio.checked = false; },
      };
    }
    if (field.type === "radio_string") {
      const span = document.createElement("span");
      span.className = "radio-inline child-field";
      const radios = [];
      for (const opt of field.options) {
        const id = "r_" + field.name + "_" + opt;
        const r = document.createElement("input");
        r.type = "radio"; r.name = field.name; r.id = id; r.value = opt;
        const lbl = document.createElement("label");
        lbl.htmlFor = id; lbl.textContent = opt;
        span.append(r, lbl);
        radios.push(r);
      }
      container.appendChild(span);
      registry[field.name] = {
        kind: "radio_string",
        get: () => (radios.find((r) => r.checked) || {}).value || field.default,
        set: (v) => { for (const r of radios) r.checked = r.value === (v || field.default); },
      };
      return {
        setEnabled: (e) => { for (const r of radios) r.disabled = !e; },
        reset: () => { for (const r of radios) r.checked = r.value === field.default; },
      };
    }
    return { setEnabled: () => {}, reset: () => {} };
  }

  function renderField(container, field) {
    const wrap = document.createElement("div");
    wrap.className = "field field-" + field.type;

    if (field.type === "text" || field.type === "textarea") {
      const label = document.createElement("label");
      if (field.label) label.textContent = field.label;
      const input = document.createElement(field.type === "textarea" ? "textarea" : "input");
      if (field.type === "text") input.type = "text";
      label.appendChild(input);
      wrap.appendChild(label);
      registry[field.name] = { kind: field.type, get: () => input.value, set: (v) => { input.value = v || ""; } };
    } else if (field.type === "checkbox") {
      const label = document.createElement("label");
      label.className = "checkbox-label";
      const cb = document.createElement("input");
      cb.type = "checkbox";
      label.append(cb, document.createTextNode(field.label));
      wrap.appendChild(label);

      const childEntries = [];
      if (field.children && field.children.length) {
        const childWrap = document.createElement("span");
        childWrap.className = "field-children";
        for (const child of field.children) childEntries.push(renderChildField(childWrap, child));
        wrap.appendChild(childWrap);
      }

      const applyEnabled = (enabled) => { for (const entry of childEntries) entry.setEnabled(enabled); };
      cb.addEventListener("change", () => {
        if (!cb.checked) for (const entry of childEntries) entry.reset();
        applyEnabled(cb.checked);
      });

      registry[field.name] = {
        kind: "checkbox",
        get: () => cb.checked,
        set: (v) => { cb.checked = !!v; applyEnabled(!!v); },
      };
    }
    container.appendChild(wrap);
  }

  // --- Procedures / diagnoses picker --------------------------------------

  function buildPickerUI(kind) {
    const isProc = kind === "procedures";
    const wrap = document.createElement("div");
    wrap.className = "picker";

    const currentList = document.createElement("ul");
    currentList.className = "picker-current-list";

    const rightCol = document.createElement("div");
    rightCol.className = "picker-right";

    const filterInput = document.createElement("input");
    filterInput.type = "text";
    filterInput.placeholder = "Filter library...";
    filterInput.className = "picker-filter";

    const libraryList = document.createElement("select");
    libraryList.size = 8;
    libraryList.className = "picker-library";
    pickerLibraryEls[kind] = libraryList;

    const addInput = document.createElement("input");
    addInput.type = "text";
    addInput.placeholder = isProc ? "Procedure name" : "Diagnosis name";
    addInput.className = "picker-add-input";

    const addBtn = document.createElement("button");
    addBtn.type = "button";
    addBtn.textContent = isProc ? "Add Procedure" : "Add Diagnosis";

    const detailLabel = document.createElement("div");
    detailLabel.className = "picker-detail-label";
    detailLabel.textContent = (isProc ? "Procedure" : "Diagnosis") + " Details";

    const detailText = document.createElement("textarea");
    detailText.rows = 4;
    detailText.className = "picker-detail";

    const saveDetailBtn = document.createElement("button");
    saveDetailBtn.type = "button";
    saveDetailBtn.textContent = "Save Details";

    libraryList.addEventListener("change", () => { addInput.value = libraryList.value; });
    filterInput.addEventListener("input", () => {
      const q = filterInput.value.toLowerCase();
      for (const opt of libraryList.options) opt.hidden = !opt.value.toLowerCase().includes(q);
    });

    function store() { return isProc ? pickerState.procedures : pickerState.diagnoses; }

    function renderCurrentList() {
      currentList.innerHTML = "";
      for (const name of Object.keys(store())) {
        const li = document.createElement("li");
        if (pickerState.selected[kind] === name) li.classList.add("selected");
        const span = document.createElement("span");
        span.textContent = name;
        span.addEventListener("click", () => {
          pickerState.selected[kind] = name;
          detailLabel.textContent = (isProc ? "Procedure" : "Diagnosis") + " Details: " + name;
          detailText.value = store()[name] || "";
          renderCurrentList();
        });
        const del = document.createElement("button");
        del.type = "button";
        del.textContent = "×";
        del.title = "Remove";
        del.addEventListener("click", (e) => {
          e.stopPropagation();
          delete store()[name];
          if (pickerState.selected[kind] === name) pickerState.selected[kind] = null;
          renderCurrentList();
        });
        li.append(span, del);
        currentList.appendChild(li);
      }
    }
    pickerRenderers[kind] = renderCurrentList;

    addBtn.addEventListener("click", () => {
      const name = addInput.value.trim().toUpperCase();
      if (!name) return;
      if (!(name in store())) store()[name] = "";
      addInput.value = "";
      renderCurrentList();
    });

    saveDetailBtn.addEventListener("click", () => {
      const name = pickerState.selected[kind];
      if (!name) {
        showMessage(`Select a ${isProc ? "procedure" : "diagnosis"} first.`, "error");
        return;
      }
      store()[name] = detailText.value;
      showMessage("Detail set -- don't forget to Save the Visit.", "success");
    });

    rightCol.append(filterInput, libraryList, addInput, addBtn, detailLabel, detailText, saveDetailBtn);
    wrap.append(currentList, rightCol);
    return wrap;
  }

  // --- Summary -- equivalent of Visits/visits.py's review_summary() /
  // print_summary(), which built an HTML report and either sent it to a
  // QPrinter or wrote it to Config.config's configured save_path. Neither
  // of those makes sense for a multi-client web app (there's no single
  // "the printer" or "the save folder" -- every client PC has its own),
  // so this leans on the browser instead: printing opens the report in a
  // new tab and calls window.print() there, which is also how "save as
  // PDF" happens (print destination = Save as PDF, no server-side PDF
  // renderer needed); downloading as HTML fetches the same report and
  // saves it as a file client-side.

  function buildSummaryUI() {
    const wrap = document.createElement("div");
    wrap.className = "summary-panel";

    const controls = document.createElement("div");
    controls.className = "button-row";

    const createBtn = document.createElement("button");
    createBtn.type = "button";
    createBtn.textContent = "Create Visit Summary";

    const printBtn = document.createElement("button");
    printBtn.type = "button";
    printBtn.textContent = "Print / Save as PDF";

    const downloadBtn = document.createElement("button");
    downloadBtn.type = "button";
    downloadBtn.textContent = "Download as HTML";

    controls.append(createBtn, printBtn, downloadBtn);

    const preview = document.createElement("iframe");
    preview.className = "summary-preview";
    preview.title = "Visit summary preview";

    wrap.append(controls, preview);

    function reportUrl() {
      return `/api/patients/${encodeURIComponent(tz)}/visits/${currentDate}/report`;
    }

    async function fetchReportHtml() {
      const res = await apiFetch(reportUrl());
      if (!res.ok) {
        showMessage("Could not generate the visit summary.", "error");
        return null;
      }
      return res.text();
    }

    createBtn.addEventListener("click", async () => {
      const html = await fetchReportHtml();
      if (html === null) return;
      preview.srcdoc = html;
      showMessage("");
    });

    printBtn.addEventListener("click", () => {
      const win = window.open(reportUrl(), "_blank");
      if (!win) {
        showMessage("Pop-up blocked -- allow pop-ups for this site to print.", "error");
        return;
      }
      win.addEventListener("load", () => win.print());
    });

    downloadBtn.addEventListener("click", async () => {
      const html = await fetchReportHtml();
      if (html === null) return;
      const blob = new Blob([html], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      // "2026-08-20" -> "20260820", to match the filename convention
      // Print / Save as PDF suggests (see _report_filename_stem server-side).
      a.download = `${tz}_${currentDate.replaceAll("-", "")}.html`;
      a.click();
      URL.revokeObjectURL(url);
    });

    return wrap;
  }

  // --- Tabs -- jump-links into one continuous scrollable page ------------
  //
  // Originally these hid/showed panes like a classic tab widget, but on a
  // 250+ field form that just hides the length rather than helping you get
  // around it. Now every section stays in the DOM and visible; clicking a
  // tab scrolls to it (CSS scroll-margin-top on .tab-pane keeps it from
  // landing underneath the sticky bar), and the bar itself stays pinned
  // while you scroll so both navigation and Save stay reachable.

  function scrollToTab(id) {
    for (const b of els.tabsNav.querySelectorAll(".tab-button")) {
      b.classList.toggle("active", b.dataset.tab === id);
    }
    document.getElementById("pane-" + id).scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderTabs() {
    const allTabs = [
      ...VISIT_TABS.map((t) => ({ id: t.id, label: t.label, kind: "grouped", data: t })),
      ...VISIT_TEXT_TABS.map((t) => ({ id: t.id, label: t.label, kind: "text", data: t })),
      { id: "procedures", label: "Procedures", kind: "procedures" },
      { id: "diagnoses", label: "Diagnoses", kind: "diagnoses" },
      { id: "summary", label: "Summary", kind: "summary" },
    ];

    for (const tab of allTabs) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "tab-button";
      btn.textContent = tab.label;
      btn.dataset.tab = tab.id;
      btn.addEventListener("click", () => scrollToTab(tab.id));
      els.tabsNav.appendChild(btn);

      const pane = document.createElement("div");
      pane.className = "tab-pane";
      pane.id = "pane-" + tab.id;

      const heading = document.createElement("h3");
      heading.className = "tab-section-heading";
      heading.textContent = tab.label;
      pane.appendChild(heading);

      if (tab.kind === "grouped") {
        for (const group of tab.data.groups) {
          const fieldset = document.createElement("fieldset");
          fieldset.className = "visit-group";
          const legend = document.createElement("legend");
          legend.textContent = group.title;
          fieldset.appendChild(legend);
          for (const field of group.fields) renderField(fieldset, field);
          pane.appendChild(fieldset);
        }
      } else if (tab.kind === "text") {
        const ta = document.createElement("textarea");
        ta.rows = 22;
        ta.className = "big-textarea";
        pane.appendChild(ta);
        registry[tab.data.name] = { kind: "textarea", get: () => ta.value, set: (v) => { ta.value = v || ""; } };
      } else if (tab.kind === "summary") {
        pane.appendChild(buildSummaryUI());
      } else {
        pane.appendChild(buildPickerUI(tab.kind));
      }
      els.tabContent.appendChild(pane);
    }

    const spacer = document.createElement("span");
    spacer.className = "visit-tabs-spacer";
    els.tabsNav.appendChild(spacer);

    const topSave = document.createElement("button");
    topSave.type = "button";
    topSave.id = "btn-save-top";
    topSave.textContent = "Save the Visit";
    topSave.className = "btn-save-top";
    els.tabsNav.appendChild(topSave);
    els.btnSaveTop = topSave;

    if (allTabs.length) scrollToTab(allTabs[0].id);
  }

  // --- Load / save / clear --------------------------------------------------

  function loadIntoForm(data) {
    for (const [name, entry] of Object.entries(registry)) {
      if (name in data) entry.set(data[name]);
    }
    pickerState.procedures = { ...data.procedures };
    pickerState.diagnoses = { ...data.diagnoses };
    pickerState.selected.procedures = null;
    pickerState.selected.diagnoses = null;
    pickerRenderers.procedures();
    pickerRenderers.diagnoses();
    captureBaseline();
  }

  function gatherFormData() {
    const data = {};
    for (const [name, entry] of Object.entries(registry)) data[name] = entry.get();
    data.procedures = { ...pickerState.procedures };
    data.diagnoses = { ...pickerState.diagnoses };
    return data;
  }

  function captureBaseline() {
    baselineSnapshot = JSON.stringify(gatherFormData());
  }

  function isDirty() {
    return baselineSnapshot !== null && JSON.stringify(gatherFormData()) !== baselineSnapshot;
  }

  function clearForm() {
    for (const entry of Object.values(registry)) {
      if (entry.kind === "text" || entry.kind === "textarea") entry.set("");
      else entry.set(false);
    }
    pickerState.procedures = {};
    pickerState.diagnoses = {};
    pickerState.selected.procedures = null;
    pickerState.selected.diagnoses = null;
    pickerRenderers.procedures();
    pickerRenderers.diagnoses();
  }

  function updateDateBadge(isNew) {
    const isToday = currentDate === todayISO;
    els.dateBadge.textContent = isToday ? (isNew ? "New visit (today)" : "Today's visit") : "Past visit (read-only)";
    els.dateBadge.className = "badge " + (isToday ? "badge-today" : "badge-past");
    els.btnSave.disabled = !isToday;
    if (els.btnSaveTop) els.btnSaveTop.disabled = !isToday;
    els.btnDelete.disabled = !isToday && !isAdminUser;
  }

  async function loadVisit(dateStr) {
    currentDate = dateStr;
    const res = await apiFetch(`/api/patients/${encodeURIComponent(tz)}/visits/${dateStr}`);
    if (!res.ok) {
      showMessage("Could not load visit.", "error");
      return;
    }
    const data = await res.json();
    loadIntoForm(data);
    updateDateBadge(data.is_new);
    showMessage("");
  }

  async function loadDates() {
    const res = await apiFetch(`/api/patients/${encodeURIComponent(tz)}/visits/dates`);
    const data = await res.json();
    todayISO = data.today;
    els.dateSelect.innerHTML = "";
    for (const d of data.dates) {
      const opt = document.createElement("option");
      opt.value = d;
      opt.textContent = d;
      els.dateSelect.appendChild(opt);
    }
    const lastDate = data.dates[data.dates.length - 1];
    els.dateSelect.value = lastDate;
    await loadVisit(lastDate);
  }

  async function loadLibraries() {
    const [procRes, diagRes] = await Promise.all([apiFetch("/api/procedures"), apiFetch("/api/diagnoses")]);
    const procs = await procRes.json();
    const diags = await diagRes.json();
    fillLibrarySelect("procedures", procs);
    fillLibrarySelect("diagnoses", diags);
  }

  function fillLibrarySelect(kind, items) {
    const select = pickerLibraryEls[kind];
    select.innerHTML = "";
    for (const item of items) {
      const opt = document.createElement("option");
      opt.value = item;
      opt.textContent = item;
      select.appendChild(opt);
    }
  }

  // --- Unsaved-changes guard --------------------------------------------
  //
  // Anything that would replace or navigate away from the currently-shown
  // visit -- the date dropdown, the Back to Patients links, or the browser
  // itself (back button, closing the tab, typing a new URL) -- routes
  // through here first if the form is dirty, since none of those would
  // otherwise give the user a chance to save first.

  function showLeaveConfirmDialog(canSave) {
    return new Promise((resolve) => {
      const overlay = document.createElement("div");
      overlay.className = "leave-modal-overlay";

      const box = document.createElement("div");
      box.className = "leave-modal-box";

      const message = document.createElement("p");
      message.textContent = canSave
        ? "This visit has unsaved changes. Save them before leaving?"
        : "This past visit has unsaved changes, but only today's visit can be saved. Leaving will discard them.";
      box.appendChild(message);

      const row = document.createElement("div");
      row.className = "button-row";

      function finish(choice) {
        overlay.remove();
        resolve(choice);
      }

      if (canSave) {
        const btnSave = document.createElement("button");
        btnSave.type = "button";
        btnSave.textContent = "Save and Leave";
        btnSave.addEventListener("click", () => finish("save"));
        row.appendChild(btnSave);
      }

      const btnDiscard = document.createElement("button");
      btnDiscard.type = "button";
      btnDiscard.textContent = "Discard and Leave";
      btnDiscard.addEventListener("click", () => finish("discard"));
      row.appendChild(btnDiscard);

      const btnCancel = document.createElement("button");
      btnCancel.type = "button";
      btnCancel.textContent = "Cancel";
      btnCancel.addEventListener("click", () => finish("cancel"));
      row.appendChild(btnCancel);

      box.appendChild(row);
      overlay.appendChild(box);
      document.body.appendChild(overlay);
      btnCancel.focus();
    });
  }

  // Resolves true if it's OK to proceed with leaving/switching (including
  // having saved first, if that's what the user chose), false if the
  // caller should stay put.
  async function resolveLeaveIntent() {
    if (!isDirty()) return true;
    const choice = await showLeaveConfirmDialog(currentDate === todayISO);
    if (choice === "cancel") return false;
    if (choice === "save") return saveVisit({ skipConfirm: true });
    return true; // discard
  }

  window.addEventListener("beforeunload", (e) => {
    // Covers browser-level navigation (back/forward, closing the tab,
    // typing a new URL) that the in-page dialog above can't intercept.
    // Modern browsers ignore any custom message and show their own
    // generic one -- setting returnValue is just what triggers that.
    if (isDirty()) {
      e.preventDefault();
      e.returnValue = "";
    }
  });

  for (const link of document.querySelectorAll(".back-link a")) {
    link.addEventListener("click", async (e) => {
      e.preventDefault();
      const href = link.getAttribute("href");
      if (await resolveLeaveIntent()) window.location.href = href;
    });
  }

  // --- Wiring ----------------------------------------------------------------

  els.dateSelect.addEventListener("change", async (e) => {
    const newDate = e.target.value;
    const previousDate = currentDate;
    if (await resolveLeaveIntent()) {
      await loadVisit(newDate);
    } else {
      els.dateSelect.value = previousDate; // the <select> already flipped visually
    }
  });

  // Returns true on a successful save, false otherwise -- resolveLeaveIntent
  // uses that to decide whether it's safe to proceed with leaving.
  async function saveVisit({ skipConfirm = false } = {}) {
    if (currentDate !== todayISO) return false;
    if (!skipConfirm && !confirm(`You requested to save this visit data from ${currentDate}`)) return false;
    const body = gatherFormData();
    const res = await apiFetch(`/api/patients/${encodeURIComponent(tz)}/visits/${currentDate}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (res.ok) {
      const data = await res.json();
      loadIntoForm(data);
      updateDateBadge(false);
      showMessage("Visit saved OK", "success");
      return true;
    }
    const payload = await res.json().catch(() => ({}));
    showMessage(typeof payload.detail === "string" ? payload.detail : "Could not save visit data.", "error");
    return false;
  }

  els.btnSave.addEventListener("click", () => saveVisit());
  // btnSaveTop is created inside renderTabs(), so wire it after that runs (see Init below).

  els.btnClear.addEventListener("click", () => {
    clearForm();
    showMessage("");
  });

  els.btnDelete.addEventListener("click", async () => {
    if (!confirm("Are you sure about deleting this visit?")) return;
    const res = await apiFetch(`/api/patients/${encodeURIComponent(tz)}/visits/${currentDate}`, { method: "DELETE" });
    if (res.status === 204) {
      showMessage("Visit deleted", "success");
      await loadDates();
    } else {
      const payload = await res.json().catch(() => ({}));
      showMessage(typeof payload.detail === "string" ? payload.detail : "Could not delete visit.", "error");
    }
  });

  // --- Init ----------------------------------------------------------------

  renderTabs();
  els.btnSaveTop.addEventListener("click", () => saveVisit());
  loadLibraries();
  loadDates();
})();
