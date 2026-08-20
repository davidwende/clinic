// Blood / Pulse page -- equivalent of Blood/blood.py's BloodForm.
(() => {
  const page = document.querySelector(".blood-page");
  const tz = page.dataset.tz;
  const isAdminUser = page.dataset.role === "admin";

  let currentDate = null;
  let todayISO = null;

  const els = {
    dateSelect: document.getElementById("blood-date-select"),
    dateBadge: document.getElementById("blood-date-badge"),
    message: document.getElementById("form-message"),
    rows: document.getElementById("blood-rows"),
    pulse: document.getElementById("f-pulse"),
    systolic: document.getElementById("f-systolic"),
    diastolic: document.getElementById("f-diastolic"),
    btnAdd: document.getElementById("btn-add"),
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

  function fmtTime(isoTime) {
    // "14:30:00.123456" -> "14:30"
    return isoTime.slice(0, 5);
  }

  function renderReadings(readings) {
    els.rows.innerHTML = "";
    const canDelete = currentDate === todayISO || isAdminUser;
    for (const r of readings) {
      const tr = document.createElement("tr");
      const del = document.createElement("button");
      del.type = "button";
      del.textContent = "Delete";
      del.className = "link-button";
      del.disabled = !canDelete;
      del.addEventListener("click", () => deleteReading(r.time));
      tr.innerHTML = `<td>${fmtTime(r.time)}</td><td>${r.pulse ?? ""}</td><td>${r.systolic ?? ""}</td><td>${r.diastolic ?? ""}</td>`;
      const actionCell = document.createElement("td");
      actionCell.appendChild(del);
      tr.appendChild(actionCell);
      els.rows.appendChild(tr);
    }
  }

  function updateDateBadge() {
    const isToday = currentDate === todayISO;
    els.dateBadge.textContent = isToday ? "Today" : "Past visit (read-only)";
    els.dateBadge.className = "badge " + (isToday ? "badge-today" : "badge-past");
    els.btnAdd.disabled = !isToday;
    els.pulse.disabled = !isToday;
    els.systolic.disabled = !isToday;
    els.diastolic.disabled = !isToday;
  }

  async function loadReadings(dateStr) {
    currentDate = dateStr;
    const res = await apiFetch(`/api/patients/${encodeURIComponent(tz)}/blood/${dateStr}`);
    if (!res.ok) {
      showMessage("Could not load readings.", "error");
      return;
    }
    renderReadings(await res.json());
    updateDateBadge();
  }

  async function loadDates() {
    // Blood readings hang off the same Visits rows, so the date list is
    // identical to the Visits tab's -- reuse that endpoint rather than
    // duplicating it.
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
    await loadReadings(lastDate);
  }

  async function deleteReading(time) {
    if (!confirm("Delete this reading?")) return;
    const res = await apiFetch(
      `/api/patients/${encodeURIComponent(tz)}/blood/${currentDate}/${encodeURIComponent(time)}`,
      { method: "DELETE" },
    );
    if (res.status === 204) {
      showMessage("Reading deleted.", "success");
      await loadReadings(currentDate);
    } else {
      const payload = await res.json().catch(() => ({}));
      showMessage(typeof payload.detail === "string" ? payload.detail : "Could not delete reading.", "error");
    }
  }

  els.dateSelect.addEventListener("change", (e) => loadReadings(e.target.value));

  els.btnAdd.addEventListener("click", async () => {
    if (currentDate !== todayISO) return;
    const body = {
      pulse: els.pulse.value === "" ? null : Number(els.pulse.value),
      systolic: els.systolic.value === "" ? null : Number(els.systolic.value),
      diastolic: els.diastolic.value === "" ? null : Number(els.diastolic.value),
    };
    const res = await apiFetch(`/api/patients/${encodeURIComponent(tz)}/blood/${currentDate}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (res.ok) {
      renderReadings(await res.json());
      els.pulse.value = "";
      els.systolic.value = "";
      els.diastolic.value = "";
      showMessage("Reading added.", "success");
    } else {
      const payload = await res.json().catch(() => ({}));
      showMessage(typeof payload.detail === "string" ? payload.detail : "Some values are not valid.", "error");
    }
  });

  loadDates();
})();
