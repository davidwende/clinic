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

  // field name -> { label: "Tab > Group > Field", tabId } -- used to point
  // save errors / verification warnings at the right place on the form.
  const fieldInfo = {};
  function buildFieldInfo() {
    const add = (name, parts, tabId) => {
      fieldInfo[name] = { label: parts.filter(Boolean).join(" \u203a "), tabId };
    };
    for (const tab of VISIT_TABS) {
      for (const group of tab.groups) {
        for (const field of group.fields) {
          add(field.name, [tab.label, group.title, field.label], tab.id);
          for (const child of field.children || []) {
            add(child.name, [tab.label, group.title, field.label, child.label], tab.id);
          }
        }
      }
    }
    for (const tab of VISIT_TEXT_TABS) add(tab.name, [tab.label], tab.id);
    add("procedures", ["Procedures"], "procedures");
    add("diagnoses", ["Diagnoses"], "diagnoses");
  }
  function fieldLabel(name) {
    return (fieldInfo[name] && fieldInfo[name].label) || name;
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
      if (field.maxLength) input.maxLength = field.maxLength;
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
    if (field.wide) wrap.classList.add("field-wide");

    if (field.type === "text" || field.type === "textarea") {
      const label = document.createElement("label");
      if (field.label) label.textContent = field.label;
      const input = document.createElement(field.type === "textarea" ? "textarea" : "input");
      if (field.type === "text") input.type = "text";
      if (field.maxLength) input.maxLength = field.maxLength;
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
    addInput.maxLength = 50; // Procedures.procedure / Diagnoses.diagnosis are str(50)

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

  // Clinical workflow order requested separately from field/DB order (which
  // stays whatever field_lists.py / VISIT_TABS declare -- this only reorders
  // the tab bar and the on-page section order, not the underlying data).
  const TAB_ORDER = [
    "cc", "exam", "back", "hip", "neck", "shoulder", "knee_ankle",
    "tests", "diagnoses", "procedures", "recommend", "summary",
  ];

  function renderTabs() {
    const tabsById = new Map([
      ...VISIT_TABS.map((t) => [t.id, { id: t.id, label: t.label, kind: "grouped", data: t }]),
      ...VISIT_TEXT_TABS.map((t) => [t.id, { id: t.id, label: t.label, kind: "text", data: t }]),
      ["procedures", { id: "procedures", label: "Procedures", kind: "procedures" }],
      ["diagnoses", { id: "diagnoses", label: "Diagnoses", kind: "diagnoses" }],
      ["summary", { id: "summary", label: "Summary", kind: "summary" }],
    ]);
    const allTabs = TAB_ORDER.map((id) => tabsById.get(id));

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
        ta.rows = 6;
        ta.className = "big-textarea";
        if (tab.data.maxLength) ta.maxLength = tab.data.maxLength;
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

  // Modal result dialog for Save. The inline #form-message sits at the very
  // top of a long page, so after scrolling down and clicking Save it was
  // usually off-screen -- a modal can't be missed. Resolves when dismissed.
  function showSaveResultDialog({ ok, title, message, items = [], gotoTabId = null, extra = null }) {
    return new Promise((resolve) => {
      const overlay = document.createElement("div");
      overlay.className = "leave-modal-overlay";
      const box = document.createElement("div");
      box.className = "leave-modal-box save-result-box " + (ok ? "save-ok" : "save-failed");
      box.setAttribute("role", "alertdialog");

      const h = document.createElement("h3");
      h.className = "save-result-title";
      h.textContent = (ok ? "\u2714 " : "\u2716 ") + title;
      box.appendChild(h);

      const p = document.createElement("p");
      p.textContent = message;
      box.appendChild(p);

      if (items.length) {
        const ul = document.createElement("ul");
        ul.className = "save-result-items";
        for (const text of items) {
          const li = document.createElement("li");
          li.textContent = text;
          ul.appendChild(li);
        }
        box.appendChild(ul);
      }
      if (extra) box.appendChild(extra);

      const row = document.createElement("div");
      row.className = "button-row";
      const finish = () => { overlay.remove(); document.removeEventListener("keydown", onKey); resolve(); };
      const onKey = (e) => { if (e.key === "Escape" || e.key === "Enter") { e.preventDefault(); finish(); } };
      if (gotoTabId) {
        const btnGo = document.createElement("button");
        btnGo.type = "button";
        btnGo.textContent = "Show me the field";
        btnGo.addEventListener("click", () => { finish(); scrollToTab(gotoTabId); });
        row.appendChild(btnGo);
      }
      const btnOk = document.createElement("button");
      btnOk.type = "button";
      btnOk.textContent = "OK";
      btnOk.addEventListener("click", finish);
      row.appendChild(btnOk);
      box.appendChild(row);

      overlay.appendChild(box);
      document.body.appendChild(overlay);
      document.addEventListener("keydown", onKey);
      btnOk.focus();
    });
  }

  // Turns a non-2xx save response into {message, field}. The server sends a
  // structured {reason, message, field} detail for save failures, but older
  // paths (404 patient-not-found, FastAPI's own 422 body validation, a proxy
  // error page) send other shapes, so all of them are handled.
  async function describeSaveError(res) {
    const payload = await res.json().catch(() => null);
    const d = payload && payload.detail;
    if (d && typeof d === "object" && !Array.isArray(d) && d.message) {
      return { message: d.message, field: d.field || null };
    }
    if (typeof d === "string") return { message: `${d} The visit was NOT saved.`, field: null };
    if (Array.isArray(d)) {
      const parts = d.map((e) => {
        const loc = (e.loc || []).filter((x) => x !== "body");
        return `${loc.length ? fieldLabel(loc[0]) : "Request"}: ${e.msg}`;
      });
      const first = d[0] && (d[0].loc || []).filter((x) => x !== "body")[0];
      return {
        message: `The server rejected some of the values (${parts.join("; ")}). The visit was NOT saved.`,
        field: first || null,
      };
    }
    return {
      message: `The server returned an error (HTTP ${res.status}${res.statusText ? " " + res.statusText : ""}). The visit was NOT saved.`,
      field: null,
    };
  }

  // Compares what was sent with what the server read back from the database
  // after committing, so "saved" means "verified stored", and anything the
  // DB layer silently changed (save_visit truncates some text to 49/99
  // characters) is reported rather than lost quietly.
  function compareSaved(sent, saved) {
    const diffs = [];
    for (const [name, entry] of Object.entries(registry)) {
      let a = sent[name];
      let b = saved[name];
      if (entry.kind === "checkbox" || entry.kind === "radio_bool") {
        if (!!a === !!b) continue;
        diffs.push(`${fieldLabel(name)}: was ${a ? "ticked" : "unticked"}, stored as ${b ? "ticked" : "unticked"}`);
        continue;
      }
      a = String(a ?? "");
      b = String(b ?? "");
      if (a === b) continue;
      if (a.startsWith(b)) {
        diffs.push(`${fieldLabel(name)}: shortened from ${a.length} to ${b.length} characters`);
      } else {
        diffs.push(`${fieldLabel(name)}: stored differently from what was entered`);
      }
    }
    for (const kind of ["procedures", "diagnoses"]) {
      const sentMap = sent[kind] || {};
      const savedMap = saved[kind] || {};
      const noun = kind === "procedures" ? "Procedure" : "Diagnosis";
      for (const key of Object.keys(sentMap)) {
        if (!(key in savedMap)) diffs.push(`${noun} "${key}" is missing from the saved visit`);
        else if (String(sentMap[key] ?? "") !== String(savedMap[key] ?? "")) diffs.push(`${noun} "${key}": details stored differently`);
      }
      for (const key of Object.keys(savedMap)) {
        if (!(key in sentMap)) diffs.push(`${noun} "${key}" is in the saved visit but was not on the form`);
      }
    }
    return diffs;
  }

  function setSaving(saving) {
    for (const btn of [els.btnSave, els.btnSaveTop]) {
      if (!btn) continue;
      if (saving) {
        btn.dataset.label = btn.textContent;
        btn.textContent = "Saving\u2026";
        btn.disabled = true;
      } else {
        btn.textContent = btn.dataset.label || btn.textContent;
        btn.disabled = currentDate !== todayISO;
      }
    }
  }

  async function saveFailed(message, { field = null, extra = null } = {}) {
    showMessage("Visit NOT saved: " + message, "error");
    const where = field && fieldInfo[field];
    await showSaveResultDialog({
      ok: false,
      title: "Visit NOT saved",
      message,
      items: where ? [`Field: ${where.label}`] : [],
      gotoTabId: where ? where.tabId : null,
      extra,
    });
    return false;
  }

  // Returns true on a verified successful save, false otherwise --
  // resolveLeaveIntent uses that to decide whether it's safe to leave.
  async function saveVisit({ skipConfirm = false } = {}) {
    if (currentDate !== todayISO) return false;
    if (!skipConfirm && !confirm(`You requested to save this visit data from ${currentDate}`)) return false;
    const body = gatherFormData();
    const savedDate = currentDate;

    let res;
    setSaving(true);
    try {
      // Plain fetch, not apiFetch: apiFetch redirects to /login on a 401,
      // which here would throw away every unsaved entry on the form.
      res = await fetch(`/api/patients/${encodeURIComponent(tz)}/visits/${savedDate}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } catch (err) {
      return saveFailed(
        "Could not reach the clinic web server (the network connection may be down, or the server is not running). " +
        "The visit was NOT saved. Your entries are still on screen -- try again once the connection is back."
      );
    } finally {
      setSaving(false);
    }

    if (res.status === 401) {
      const extra = document.createElement("p");
      const a = document.createElement("a");
      a.href = "/login";
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = "Open the login page in a new tab";
      extra.appendChild(a);
      return saveFailed(
        "Your login session has expired, so the server refused the save. The visit was NOT saved. " +
        "Your entries are still on screen: log in again in a new tab, then come back to this tab and click Save again.",
        { extra }
      );
    }
    if (!res.ok) {
      const { message, field } = await describeSaveError(res);
      return saveFailed(message, { field });
    }

    const data = await res.json().catch(() => null);
    if (!data) {
      return saveFailed(
        "The server answered, but its reply could not be read, so the save could not be confirmed. " +
        "Reopen this visit to check whether it was stored before re-entering anything."
      );
    }

    const diffs = compareSaved(body, data);
    loadIntoForm(data);
    updateDateBadge(false);
    const time = new Date().toLocaleTimeString();
    const procCount = Object.keys(data.procedures || {}).length;
    const diagCount = Object.keys(data.diagnoses || {}).length;
    const summary =
      `The visit of ${savedDate} was saved at ${time} and read back from the database to confirm it ` +
      `(${diagCount} diagnos${diagCount === 1 ? "is" : "es"}, ${procCount} procedure${procCount === 1 ? "" : "s"}).`;
    if (diffs.length) {
      showMessage(`Visit saved at ${time}, but ${diffs.length} field(s) were stored differently -- see details.`, "error");
      await showSaveResultDialog({
        ok: true,
        title: "Visit saved -- with changes",
        message: summary + " Some values were stored differently from what was entered (the form now shows the stored values):",
        items: diffs,
      });
    } else {
      showMessage(`Visit saved and verified at ${time}`, "success");
      await showSaveResultDialog({ ok: true, title: "Visit saved", message: summary });
    }
    return true;
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
  buildFieldInfo();
  els.btnSaveTop.addEventListener("click", () => saveVisit());
  loadLibraries();
  loadDates();
})();
