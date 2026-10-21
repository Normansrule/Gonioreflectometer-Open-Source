/* OpenGonio control app. Talks to opengonio/app/server.py; every number shown comes from the server.
   SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  const $ = id => document.getElementById(id);
  const ORDER = ["M4", "M3", "M2", "M1"];
  const NAMES = { M4: "Lamp arm", M3: "Table", M2: "Tilt", M1: "Spin" };
  const PLAN_INFO = {
    mirror: { label: "Mirror sweep", param: "Specular angle θ", min: 10, max: 80, value: 40, step: 1,
              help: "Holds the lamp at 2θ and sweeps the table 3° either side in 0.2° steps: 31 shots, plus a reference shot before and after. The peak shows the table's real zero." },
    inplane: { label: "In-plane grid", param: "Step", min: 5, max: 40, value: 10, step: 5,
               help: "Every reachable pair of incidence and reflection angles from 0° to 80° in the plane of the lamp and camera." },
    isotropic: { label: "Isotropic", param: "Step", min: 10, max: 45, value: 15, step: 5,
                 help: "Out-of-plane poses for materials that look the same turned any way. Needs the tilt axis." },
  };
  let S = null, target = {}, dirty = new Set(), plan = "mirror", shownRun = null, offline = false, poll = 0, lastJob = null;
  const shown = { M4: 90, M3: 0 };                      // the drawn pose eases toward the reported one
  const springs = { M4: OG.spring(90, 160, 25), M3: OG.spring(0, 160, 25) };

  async function api(path, body) {
    const opt = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
    let r;
    try { r = await fetch(path, opt); } catch (e) { offline = true; render(); throw e; }
    offline = false;
    const j = await r.json().catch(() => ({}));
    if (!r.ok) { const err = new Error(j.error || r.statusText); err.kind = j.kind; throw err; }
    return j;
  }
  let dismissed = "";
  function say(msg) { $("banner-text").innerHTML = codeify(msg || ""); $("banner").hidden = !msg; }
  const codeify = t => esc(t).replace(/`([^`]+)`/g, "<code>$1</code>");
  async function act(path, body, after) {
    try { const r = await api(path, body); say(""); if (after) after(r); }
    catch (e) { if (!offline) say(e.message); }
    await refresh();
  }

  /* ---------- state ---------- */
  async function refresh() {
    try { S = await api("/api/state"); } catch (e) { S = S || null; }
    render();
    clearTimeout(poll);
    poll = setTimeout(refresh, S && S.job && S.job.status === "running" ? 400 : 2000);
  }

  function render() {
    $("app").setAttribute("aria-busy", "false");
    $("loading").hidden = !!S || offline;
    if (offline) {
      $("loading").hidden = false; $("loading").textContent = "The app's server isn't answering. Restart it with: opengonio app";
      setConn("block", "Server stopped"); return;
    }
    if (!S) return;
    const on = S.mode !== "disconnected", running = S.job && S.job.status === "running";
    $("connect").hidden = on; $("controls").hidden = !on; $("exhibit").hidden = !on; $("runs").hidden = !on;
    $("disconnect").hidden = !on;
    document.body.classList.toggle("busy", !!running);
    if (!on) { setConn("open", "Not connected"); fillMaterials(); return; }
    setConn(running ? "lamp live" : S.mode === "sim" ? "sim" : "ok",
      (S.mode === "sim" ? `Simulated machine · ${S.material}` : "Machine over USB · untested") + (running ? " · capturing" : ""));
    if (S.last_error && S.last_error !== dismissed && $("banner").hidden) say(S.last_error);
    renderAxes(running); renderLights(running); renderPose(); renderAngles(); renderRun(running);
  }
  function setConn(kind, text) {
    $("conn").querySelector(".patch").className = "patch " + kind; $("conn-text").textContent = text;
  }
  function fillMaterials() {
    const sel = $("material"); if (sel.options.length) return;
    S.materials.forEach(m => sel.add(new Option(m[0].toUpperCase() + m.slice(1) + (m === "ptfe" ? " (PTFE white reference)" : ""), m)));
  }

  /* ---------- axes ---------- */
  function renderAxes(running) {
    const box = $("axes"), homedAll = ORDER.every(k => !S.axes[k].installed || S.axes[k].homed);
    if (!box.children.length) {
      box.innerHTML = ORDER.map(k => { const a = S.axes[k];
        return `<div class="axis" id="ax-${k}"><label for="r-${k}" title="${NAMES[k]}">${k}</label>` +
          `<input type="range" id="r-${k}" min="${a.min}" max="${a.max}" step="0.5" aria-describedby="act-${k}">` +
          `<input type="number" id="n-${k}" min="${a.min}" max="${a.max}" step="0.1" aria-label="${k} target, degrees">` +
          `<span class="act" id="act-${k}"></span></div>`; }).join("");
      ORDER.forEach(k => {
        const r = $("r-" + k), n = $("n-" + k);
        const set = v => { target[k] = +v; dirty.add(k); r.value = v; n.value = (+v).toFixed(1); renderPose(); check(); };
        r.addEventListener("input", () => set(r.value)); n.addEventListener("change", () => set(n.value));
      });
    }
    ORDER.forEach(k => {
      const a = S.axes[k], row = $("ax-" + k), r = $("r-" + k), n = $("n-" + k);
      if (!dirty.has(k) || target[k] == null) target[k] = S.position[k] ?? (k === "M4" ? 90 : 0);   // follow the machine until edited
      if (document.activeElement !== r && document.activeElement !== n) {
        r.value = target[k]; n.value = a.homed ? (+target[k]).toFixed(1) : "";   // no number until the machine has reported one
        n.placeholder = "–";
      }
      const usable = a.installed && a.homed && !running;
      r.disabled = n.disabled = !usable; row.classList.toggle("off", !a.installed);
      $("act-" + k).textContent = !a.installed ? `${NAMES[k]}: built in stage ${String(a.stage).padStart(2, "0")}`
        : !a.homed ? `${NAMES[k]}: not homed` : `${NAMES[k]} at ${(+S.position[k]).toFixed(2)}°`;
    });
    $("homenote").hidden = homedAll;
    $("home").disabled = !!running;
    $("move").disabled = $("specular").disabled = !homedAll || !!running;
  }
  let checkT = 0;
  function check() {
    clearTimeout(checkT);
    checkT = setTimeout(async () => {
      const pose = pick(target);
      try { const c = await api("/api/check", { pose });
        $("check").textContent = `Target: θi ${c.theta_i.toFixed(1)}°, θr ${c.theta_r.toFixed(1)}°` +
          (c.safe ? "" : " · outside the keep-out: the machine will refuse this") + (c.measurable ? "" : " · light or camera behind the sample");
      } catch (e) { $("check").textContent = ""; }
    }, 120);
  }
  const pick = t => Object.fromEntries(ORDER.filter(k => S.axes[k].installed && t[k] != null).map(k => [k, +t[k]]));

  /* ---------- lights ---------- */
  function renderLights(running) {
    const box = $("lights"), key = S.lights.map(l => l.name).join();
    if (box.dataset.key === key) {                      // built: only update state, so focus and open details survive
      S.lights.forEach(l => { const b = box.querySelector(`[data-light="${l.name}"]`);
        b.setAttribute("aria-checked", String(l.on)); b.disabled = !!(l.blocked || !l.installed || running); });
      return;
    }
    box.dataset.key = key;
    box.innerHTML = S.lights.map(l => {
      const label = l.name === "white" ? "White lamp, 3000 K" : l.name === "multispectral" ? "Colour LED bank" : l.name;
      const why = l.blocked ? `<details><summary><span class="patch block" aria-hidden="true"></span> Blocked: driver circuit unsafe as designed, never switched on</summary><p>${esc(l.blocked)}</p></details>`
        : !l.installed ? "<p>Not installed yet.</p>" : "";
      return `<div class="light"><span id="lt-${l.name}">${label}</span><button class="switch" type="button" role="switch" aria-labelledby="lt-${l.name}"` +
        ` aria-checked="${l.on}" data-light="${l.name}" ${l.blocked || !l.installed || running ? "disabled" : ""}></button>${why}</div>`;
    }).join("");
    renderLights(running);
    box.querySelectorAll("[data-light]").forEach(b => b.addEventListener("click", () =>
      act("/api/light", { name: b.dataset.light, on: b.getAttribute("aria-checked") !== "true" }, grabSoon)));
  }
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  /* ---------- the pose exhibit ---------- */
  const P = (deg, r) => [r * Math.cos(deg * Math.PI / 180), -r * Math.sin(deg * Math.PI / 180)];
  (function ticks() {
    let h = "";
    for (let a = 0; a < 360; a += 30) { const [x1, y1] = P(a, 150), [x2, y2] = P(a, a % 90 ? 158 : 164); h += `<line class="tick" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`;
      if (a % 90 === 0 && a) { const [tx, ty] = P(a, 178); h += `<text class="tick-lbl" x="${tx}" y="${ty + 4}" text-anchor="middle">${a}°</text>`; } }
    $("ticks").innerHTML = h;
  })();
  function arc(el, a0, a1, r) {
    const [x0, y0] = P(a0, r), [x1, y1] = P(a1, r), large = Math.abs(a1 - a0) > 180 ? 1 : 0, sweep = a1 > a0 ? 0 : 1;
    el.setAttribute("d", `M${x0} ${y0} A${r} ${r} 0 ${large} ${sweep} ${x1} ${y1}`);
  }
  function drawPose() {
    const m4 = shown.M4, m3 = shown.M3, [lx, ly] = P(m4, 150);
    $("lamp").setAttribute("cx", lx); $("lamp").setAttribute("cy", ly);
    $("lamp-halo").setAttribute("cx", lx); $("lamp-halo").setAttribute("cy", ly);
    $("ray-in").setAttribute("x1", lx); $("ray-in").setAttribute("y1", ly); $("ray-in").setAttribute("x2", 0); $("ray-in").setAttribute("y2", 0);
    $("sample").setAttribute("transform", `rotate(${-m3})`);
    const short = d => ((d % 360) + 540) % 360 - 180;            // the smaller way round
    arc($("arc-in"), m3, m3 + short(m4 - m3), 56); arc($("arc-out"), 0, short(m3), 84);
    if (S) {
      const tm4 = target.M4 ?? m4, tm3 = target.M3 ?? m3, [gx, gy] = P(tm4, 150);
      $("ghost-lamp").setAttribute("cx", gx); $("ghost-lamp").setAttribute("cy", gy);
      $("ghost-sample").setAttribute("transform", `rotate(${-tm3})`);
      $("ghost").classList.toggle("same", Math.abs(tm4 - (S.position.M4 ?? tm4)) < 0.05 && Math.abs(tm3 - (S.position.M3 ?? tm3)) < 0.05);
      $("pose").classList.toggle("lamp-off", !(S.lights.find(l => l.name === "white") || {}).on);
      $("pose").classList.toggle("unknown", !S.axes.M4.homed || !S.axes.M3.homed);
      $("lamp").setAttribute("aria-valuenow", (target.M4 ?? m4).toFixed(1));
      $("lamp").setAttribute("aria-valuetext", `target ${(target.M4 ?? m4).toFixed(1)} degrees`);
    }
  }
  let raf = 0, last = 0;
  function renderPose() {
    if (!S) return;
    springs.M4.target = S.position.M4 ?? 90; springs.M3.target = S.position.M3 ?? 0;
    if (OG.reduced) { shown.M4 = springs.M4.x = springs.M4.target; shown.M3 = springs.M3.x = springs.M3.target; drawPose(); return; }
    if (!raf) { last = performance.now(); raf = requestAnimationFrame(tick); }
  }
  function tick(now) {
    const dt = Math.min((now - last) / 1000, 1 / 30); last = now;
    const a = springs.M4.step(dt), b = springs.M3.step(dt);
    shown.M4 = springs.M4.x; shown.M3 = springs.M3.x; drawPose();
    raf = a || b ? requestAnimationFrame(tick) : 0;
  }
  function setM4(v) {
    const a = S.axes.M4; v = Math.max(a.min, Math.min(a.max, v));
    target.M4 = +v.toFixed(1); dirty.add("M4"); $("r-M4").value = target.M4; $("n-M4").value = target.M4.toFixed(1); drawPose(); check();
  }
  (function dragLamp() {
    const svg = $("pose"), lamp = $("lamp"); let drag = false;
    const angle = e => { const r = svg.getBoundingClientRect(), x = (e.clientX - r.left) / r.width * 400 - 200, y = (e.clientY - r.top) / r.height * 400 - 200;
      let a = Math.atan2(-y, x) * 180 / Math.PI; return a < 0 ? a + 360 : a; };
    lamp.addEventListener("pointerdown", e => { if ($("r-M4").disabled) return; drag = true; lamp.setPointerCapture(e.pointerId); });
    lamp.addEventListener("pointermove", e => { if (drag) setM4(angle(e)); });
    lamp.addEventListener("pointerup", () => { drag = false; });
    lamp.addEventListener("keydown", e => {
      if ($("r-M4").disabled) return;
      const d = e.shiftKey ? 10 : 1;
      if (e.key === "ArrowRight" || e.key === "ArrowUp") setM4((target.M4 ?? 90) + d);
      else if (e.key === "ArrowLeft" || e.key === "ArrowDown") setM4((target.M4 ?? 90) - d);
      else if (e.key === "Enter") move(); else return;
      e.preventDefault();
    });
  })();
  function renderAngles() {
    const a = S.angles;
    $("a-ti").textContent = a ? a.theta_i.toFixed(1) + "°" : "–"; $("a-tr").textContent = a ? a.theta_r.toFixed(1) + "°" : "–";
    $("a-dp").textContent = a ? a.delta_phi.toFixed(0) + "°" : "–"; $("a-cl").textContent = a ? a.clearance_mm.toFixed(0) + " mm" : "–";
  }
  async function grab() {
    try {
      const r = await fetch("/api/frame.png"); if (!r.ok) throw new Error((await r.json()).error);
      let img = $("frame");
      if (!img) { img = new Image(64, 48); img.id = "frame"; img.alt = "Latest camera frame"; $("frame-box").prepend(img); }
      const url = URL.createObjectURL(await r.blob()), old = img.src;
      img.src = url; $("frame-empty").hidden = true; if (old && old.startsWith("blob:")) URL.revokeObjectURL(old);
      const lit = (S.lights.find(l => l.name === "white") || {}).on;
      $("frame-cap").textContent = (S.mode === "sim" ? "Simulated camera, 64 × 48 px" : "Camera (untested)") + (lit ? "" : ". The lamp is off, so the frame is dark.");
    } catch (e) { $("frame-empty").hidden = false; $("frame-empty").textContent = e.message || "No frame"; }
  }
  let grabT = 0; const grabSoon = () => { clearTimeout(grabT); grabT = setTimeout(grab, 150); };

  /* ---------- moves ---------- */
  function move() { act("/api/move", { pose: pick(target) }, () => { dirty.clear(); grabSoon(); }); }
  $("move").addEventListener("click", move);
  $("specular").addEventListener("click", () => {
    const m4 = target.M4 ?? S.position.M4 ?? 90, m3 = m4 <= 180 ? m4 / 2 : m4 / 2 - 180;
    target.M3 = +m3.toFixed(1); dirty.add("M3"); $("r-M3").value = target.M3; $("n-M3").value = target.M3.toFixed(1); drawPose(); check();
  });
  $("home").addEventListener("click", () => act("/api/home", {}, () => {
    dirty.clear();                       // tilt and spin home at their switches: offer a level sample as the next target
    ["M2", "M1"].forEach(k => { if (S.axes[k].installed) { target[k] = 0; dirty.add(k); } });
    grabSoon();
  }));
  $("grab").addEventListener("click", grab);
  $("stop").addEventListener("click", () => act("/api/stop", {}, () => say("Stopped. The controller was reset: home the axes before moving again.")));
  document.addEventListener("keydown", e => { if (e.key === "Escape" && !e.defaultPrevented) $("stop").click(); });
  const reset = () => { target = {}; dirty.clear(); $("axes").innerHTML = ""; };
  $("disconnect").addEventListener("click", () => act("/api/disconnect", {}, reset));
  $("banner-close").addEventListener("click", () => { dismissed = (S && S.last_error) || $("banner-text").textContent; say(""); });
  $("f-sim").addEventListener("submit", e => { e.preventDefault(); reset();
    setConn("lamp live", "Connecting…"); act("/api/connect", { mode: "sim", material: $("material").value }); });
  $("f-hw").addEventListener("submit", e => { e.preventDefault(); reset();
    setConn("lamp live", "Connecting…"); act("/api/connect", { mode: "hardware" }); });

  /* ---------- capture ---------- */
  (function plans() {
    const box = $("plans");
    box.innerHTML = Object.entries(PLAN_INFO).map(([k, p]) => `<button type="button" role="radio" data-plan="${k}" aria-checked="${k === plan}">${p.label}</button>`).join("");
    const choose = k => { plan = k; box.querySelectorAll("button").forEach(b => b.setAttribute("aria-checked", String(b.dataset.plan === k)));
      const p = PLAN_INFO[k], inp = $("param"); $("param-label").textContent = p.param;
      Object.assign(inp, { min: p.min, max: p.max, step: p.step, value: p.value }); $("plan-help").textContent = p.help; };
    box.addEventListener("click", e => { const b = e.target.closest("[data-plan]"); if (b && !b.disabled) choose(b.dataset.plan); });
    box.addEventListener("keydown", e => { const keys = Object.keys(PLAN_INFO), i = keys.indexOf(plan);
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") { e.preventDefault(); const k = keys[(i + (e.key === "ArrowRight" ? 1 : keys.length - 1)) % keys.length];
        choose(k); box.querySelector(`[data-plan="${k}"]`).focus(); } });
    choose(plan);
  })();
  $("run").addEventListener("click", () => {
    const v = +$("param").value;
    act("/api/run", { plan, theta: v, step: v }, r => { lastJob = r.job.name; $("result").hidden = true; });
  });
  function renderRun(running) {
    const j = S.job, homed = ORDER.every(k => !S.axes[k].installed || S.axes[k].homed);
    $("plans").querySelectorAll("button").forEach(b => b.disabled = !!running || (b.dataset.plan === "isotropic" && !S.axes.M2.installed));
    $("run").disabled = !!running || !homed;
    $("run").textContent = running ? "Capturing…" : homed ? "Run capture" : "Home first to capture";
    $("progress").hidden = !j;
    if (j) {
      const f = Math.min(j.done / Math.max(j.total, 1), 1);
      $("fill").style.transform = `scaleX(${f})`;
      $("progress-text").textContent = j.status === "running" ? `${j.name}: ${j.done} of ${j.total} shots` :
        j.status === "finished" ? `${j.name}: finished, ${j.done} shots` : `${j.name}: ${j.status}${j.error ? " (" + j.error + ")" : ""}`;
      if (j.status === "finished" && shownRun !== j.name) { dirty.clear(); showRun(j.name, j.result); }
    }
    $("datadir").textContent = `Runs are saved in ${S.data_dir}`;
    loadRuns();
  }
  let runsKey = "";
  async function loadRuns() {
    const key = S.job ? S.job.name + S.job.status : "none"; if (key === runsKey) return; runsKey = key;
    try {
      const { runs } = await api("/api/runs"), ul = $("runlist");
      if (!runs.length) { ul.innerHTML = '<li class="empty small">No runs yet. Run a capture and its curve appears here.</li>'; return; }
      ul.innerHTML = runs.map(r => `<li><button type="button" data-run="${esc(r.name)}" ${r.curve ? "" : "disabled"} aria-current="${r.name === shownRun}">` +
        `<span>${esc(r.name)}</span><span>${r.simulated ? "simulated · " : ""}${r.shots} shots · ${esc(r.status)}</span></button></li>`).join("");
      ul.querySelectorAll("[data-run]").forEach(b => b.addEventListener("click", () => showRun(b.dataset.run)));
    } catch (e) { /* the banner already says why */ }
  }
  async function showRun(name, result) {
    shownRun = name;
    let c; try { c = await api("/api/curve?run=" + encodeURIComponent(name)); } catch (e) { say(e.message); return; }
    $("result").hidden = false; $("result-title").textContent = (c.simulated ? "Simulated · " : "") + name;
    const v = result && result.result, kind = v === "PASS" ? "ok" : v === "WARN" ? "lamp" : v === "FAIL" ? "block" : "open";
    $("verdict").innerHTML = v ? `<span class="patch ${kind}" aria-hidden="true"></span>verify: ${v}` : "";
    const notes = result ? [...(result.problems || []), ...(result.notes || [])] : [];
    if (result && result.mirror_peak_error_deg != null) notes.unshift(`Mirror peak ${result.mirror_peak_error_deg > 0 ? "+" : ""}${result.mirror_peak_error_deg}° from the expected angle`);
    if (result && result.lamp_drift_pct != null) notes.push(`Lamp drift over the run: ${result.lamp_drift_pct} %`);
    $("notes").innerHTML = notes.map(n => `<li>${codeify(n)}</li>`).join("");
    curveRows = c.rows; drawCurve(); runsKey = "";
    loadRuns();
  }
  let curveRows = null;
  function drawCurve() {
    if (!curveRows) return;
    const cv = $("curve"), dpr = Math.min(devicePixelRatio || 1, 2), W = cv.clientWidth, H = Math.round(W * +cv.dataset.aspect);
    if (!W) return;
    cv.style.height = H + "px"; cv.width = W * dpr; cv.height = H * dpr;
    const g = cv.getContext("2d"), K = OG.tokens(); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.font = `12px ${K.text}`;
    const mirror = curveRows.every(r => r.M4 === curveRows[0].M4);
    const absolute = !mirror && curveRows.some(r => r.brdf_per_sr);       // BRDF in 1/sr needs a white reference
    const yv = r => absolute ? (r.brdf_per_sr === "" ? null : +r.brdf_per_sr) : (r.linear_mean === "" ? null : +r.linear_mean);
    const pts = curveRows.filter(r => r.valid !== "no").map(r => mirror ? [+r.M3, yv(r), 0] : [+r.theta_r, yv(r), +r.theta_i])
      .filter(p => p[1] != null && isFinite(p[1]));
    if (!pts.length) return;
    const L = 40, R = 10, T = 10, B = 30, xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y1 = Math.max(...ys) * 1.08 || 1;
    const X = x => L + (x - x0) / ((x1 - x0) || 1) * (W - L - R), Y = y => H - B - y / y1 * (H - T - B);
    g.strokeStyle = K.rule; g.fillStyle = K.ink2; g.lineWidth = 1;
    for (let i = 0; i <= 4; i++) { const y = y1 * i / 4; g.beginPath(); g.moveTo(L, Y(y)); g.lineTo(W - R, Y(y)); g.stroke(); g.fillText(y1 < 10 ? y.toFixed(2) : y.toFixed(0), 2, Y(y) + 4); }
    g.textAlign = "right"; g.fillText(mirror ? "table angle M3 (°)" : "reflection angle θr (°)", W - R, H - 6); g.textAlign = "left";
    g.fillText(absolute ? "BRDF, per sr" : "brightness, relative", L + 6, T + 12);
    g.fillText(x0.toFixed(0) + "°", L, H - 14);
    const groups = {}; pts.forEach(p => (groups[p[2]] = groups[p[2]] || []).push(p));
    const keys = Object.keys(groups).sort((a, b) => a - b);
    keys.forEach((k, i) => {
      const t = keys.length > 1 ? i / (keys.length - 1) : 1;
      g.strokeStyle = keys.length > 1 ? OG.alpha(K.blue, 0.35 + 0.65 * t) : K.blue; g.fillStyle = g.strokeStyle; g.lineWidth = 1.75;
      const s = groups[k].sort((a, b) => a[0] - b[0]); g.beginPath(); s.forEach(([x, y], j) => j ? g.lineTo(X(x), Y(y)) : g.moveTo(X(x), Y(y))); g.stroke();
      s.forEach(([x, y]) => { g.beginPath(); g.arc(X(x), Y(y), 2.5, 0, 7); g.fill(); });
    });
    cv.setAttribute("aria-label", mirror ? `Brightness against table angle, ${pts.length} shots` : `BRDF against reflection angle for ${keys.length} incidence angles`);
  }
  window.addEventListener("og:theme", () => { drawCurve(); drawPose(); });
  window.addEventListener("resize", () => { clearTimeout(drawCurve.t); drawCurve.t = setTimeout(drawCurve, 120); });

  refresh().then(() => { if (S && S.mode !== "disconnected") grab(); });
})();
