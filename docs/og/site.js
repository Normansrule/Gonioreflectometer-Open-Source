/* The landing page: specimen hero, section rail, reveals, the drag row, results charts, the evidence ledger and the
   stage list. Numbers come from site-data.js (tools/site_data.py) and og/sim-examples.js (tools/make_assets.py).
   SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  const $ = id => document.getElementById(id);
  const SITE = window.SITE || { stages: [], evidence: [] }, SIM = window.SIM_EXAMPLES || null;
  const REPO = "https://github.com/Normansrule/Gonioreflectometer-Open-Source";
  const usd = v => "$" + v.toFixed(2);

  /* ---------- hero: the lamp follows the pointer on a spring, drifts when left alone ---------- */
  (function hero() {
    const stage = $("stage"), canvas = $("spec");
    let spec = null;
    try { spec = window.Specimen && Specimen.make(canvas, {}); } catch (e) { spec = null; }
    if (!spec) { stage.classList.add("nogl"); }
    const th = OG.spring(34, 90, 19), ph = OG.spring(90, 90, 19);
    let lastInput = -1e9, running = false, visible = true, t0 = performance.now(), last = t0;
    const clampTh = v => Math.max(12, Math.min(87, v)), wrap = v => ((v % 360) + 360) % 360;
    const gl = $("glamp"), gr = $("gray"), gc = $("gcam"), rti = $("rti"), live = $("lampread");
    const cam = 35 * Math.PI / 180; gc.setAttribute("cx", (-34 * Math.sin(cam)).toFixed(1)); gc.setAttribute("cy", (-34 * Math.cos(cam)).toFixed(1));
    function readout() {
      const t = th.x, p = ph.x, side = Math.sin(p * Math.PI / 180) >= 0 ? 1 : -1, a = side * t * Math.PI / 180;
      const x = (34 * Math.sin(a)).toFixed(1), y = (-34 * Math.cos(a)).toFixed(1);
      gl.setAttribute("cx", x); gl.setAttribute("cy", y); gr.setAttribute("x2", x); gr.setAttribute("y2", y);
      rti.textContent = Math.round(t) + "°";
    }
    const labels = [...$("labels").children], spots = [-1.09, 0, 1.09];
    let placed = "";
    function place() {                                  // keep each label under its strip as the canvas resizes
      const key = canvas.clientWidth + "x" + canvas.clientHeight; if (key === placed) return; placed = key;
      labels.forEach((el, i) => { const q = spec.project(spots[i], -1.15); if (q) { el.style.left = q[0] + "px"; el.style.top = q[1] + "px"; } });
    }
    function frame(now) {
      const dt = Math.min((now - last) / 1000, 1 / 30); last = now;
      const idle = !OG.reduced && now - lastInput > 4000;
      if (idle) { const s = (now - t0) / 1000; th.target = 52 - 18 * Math.cos(0.16 * s); ph.target = 90 + 80 * Math.sin(0.11 * s); }
      const a = th.step(dt), b = ph.step(dt);
      if (spec) { spec.draw(th.x, ph.x); place(); }
      readout();
      running = visible && (a || b || idle);
      if (running) requestAnimationFrame(frame);
    }
    function kick() { if (!running && visible) { running = true; last = performance.now(); requestAnimationFrame(frame); } }
    function aim(e) {
      const r = stage.getBoundingClientRect(), px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
      ph.target = 90 + (0.5 - px) * 200; th.target = clampTh(15 + py * 72);
      lastInput = performance.now(); stage.classList.add("touched"); kick();
    }
    stage.addEventListener("pointermove", aim);
    stage.addEventListener("pointerdown", aim);
    stage.addEventListener("keydown", e => {
      const d = e.shiftKey ? 15 : 5;
      if (e.key === "ArrowLeft") ph.target += d; else if (e.key === "ArrowRight") ph.target -= d;
      else if (e.key === "ArrowUp") th.target = clampTh(th.target - d); else if (e.key === "ArrowDown") th.target = clampTh(th.target + d);
      else if (e.key === "Home") { th.target = 35; ph.target = 90; }
      else return;
      e.preventDefault(); lastInput = performance.now(); stage.classList.add("touched"); kick();
      clearTimeout(aim.t); aim.t = setTimeout(() => {
        live.textContent = `Lamp ${Math.round(th.target)} degrees from the normal, azimuth ${Math.round(wrap(ph.target))} degrees` +
          (Math.abs(th.target - 35) < 4 && Math.abs(wrap(ph.target) - 90) < 6 ? ": the mirror reflects the lamp into the camera." : ".");
      }, 350);
    });
    if (OG.reduced) { th.x = th.target = 35; ph.x = ph.target = 96; }   // a still, readable pose: the mirror just catching the lamp
    new IntersectionObserver(es => { visible = es[0].isIntersecting; if (visible) kick(); }).observe(stage);
    window.addEventListener("resize", () => { if (spec) { spec.draw(th.x, ph.x); place(); } });
    window.addEventListener("og:theme", () => { if (spec) spec.draw(th.x, ph.x); });
    OG.onReduce(() => { lastInput = performance.now(); kick(); });
    readout(); kick();
  })();

  /* ---------- rail: appears after the hero, marks the section in view ---------- */
  (function rail() {
    const nav = document.querySelector(".rail"), links = [...nav.querySelectorAll("a")];
    const secs = links.map(a => document.querySelector(a.getAttribute("href")));
    new IntersectionObserver(es => nav.classList.toggle("on", !es[0].isIntersecting), { threshold: 0 })
      .observe(document.querySelector(".hero"));
    new IntersectionObserver(es => nav.classList.toggle("off", es[0].isIntersecting), { rootMargin: "0px 0px -40% 0px" })
      .observe(document.querySelector(".foot"));
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) links.forEach((a, i) => a.setAttribute("aria-current", String(secs[i] === e.target)));
    }), { rootMargin: "-45% 0px -50% 0px" });
    secs.forEach(s => s && io.observe(s));
  })();

  /* ---------- reveal: sections come into the light as they arrive ---------- */
  (function reveal() {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("lit"); io.unobserve(e.target); } }),
      { rootMargin: "0px 0px 15% 0px" });
    document.querySelectorAll(".reveal").forEach(el => io.observe(el));
  })();

  /* ---------- the drag row: pointer drag with momentum, snap on rest, buttons and keys ---------- */
  (function row() {
    const el = $("row"); let down = null, v = 0, raf = 0;
    const step = () => (el.querySelector(".moment")?.getBoundingClientRect().width || 300) + 16;
    el.addEventListener("pointerdown", e => {
      if (e.pointerType !== "mouse") return;               // touch and pen already scroll natively
      cancelAnimationFrame(raf); down = { x: e.clientX, s: el.scrollLeft, t: performance.now(), lx: e.clientX, moved: false };
      el.setPointerCapture(e.pointerId);
    });
    el.addEventListener("pointermove", e => {
      if (!down) return; const dx = e.clientX - down.x;
      if (!down.moved && Math.abs(dx) > 4) { down.moved = true; el.classList.add("dragging"); }
      const now = performance.now(); v = (e.clientX - down.lx) / Math.max(now - down.t, 1); down.lx = e.clientX; down.t = now;
      el.scrollLeft = down.s - dx;
    });
    const end = () => {
      if (!down) return; const moved = down.moved; down = null;
      if (!moved) { el.classList.remove("dragging"); return; }
      let vel = -v * 16;
      const coast = () => { el.scrollLeft += vel; vel *= 0.92;
        if (Math.abs(vel) > 0.5 && !OG.reduced) raf = requestAnimationFrame(coast); else el.classList.remove("dragging"); };
      raf = requestAnimationFrame(coast);
    };
    el.addEventListener("pointerup", end); el.addEventListener("pointercancel", end);
    document.querySelectorAll("[data-row]").forEach(b => b.addEventListener("click", () =>
      el.scrollBy({ left: +b.dataset.row * step(), behavior: OG.reduced ? "auto" : "smooth" })));
    el.addEventListener("keydown", e => {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      e.preventDefault(); el.scrollBy({ left: (e.key === "ArrowRight" ? 1 : -1) * step(), behavior: OG.reduced ? "auto" : "smooth" });
    });
  })();

  /* ---------- numbers from the repo ---------- */
  if (SITE.plan_usd) $("costline").textContent = `Planned cost: ${usd(SITE.plan_usd)} of parts, under a hard cap of ${usd(SITE.cap_usd)}.`;
  if (SITE.steps) $("build-lead").textContent = `${SITE.steps} steps, about ${Math.round(SITE.hours)} hours of work and ${usd(SITE.plan_usd)} of parts. ` +
    "Each stage ends with something that works, and each step is a checklist: what you need, what to do, how to check it, and what to do if the check fails.";

  /* ---------- evidence ledger ---------- */
  (function ledger() {
    const dl = $("ledger");
    const kind = s => /^blocked/i.test(s) ? ["block", "Blocked"] : /^simulated/i.test(s) ? ["sim", "Simulated"]
      : /^modeled|^modelled/i.test(s) ? ["model", "Modelled"] : ["open", "Not yet"];
    const md = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/`([^`]+)`/g, "<code>$1</code>");
    dl.innerHTML = SITE.evidence.map(r => { const [k, label] = kind(r.evidence);
      return `<div><dt>${md(r.claim)}</dt><dd><span class="patch ${k}" aria-hidden="true"></span><span><span class="sr-only">${label}: </span>${md(r.evidence)}</span></dd></div>`; }).join("");
  })();

  /* ---------- stages: sticky simulator frame, active list item ---------- */
  (function stages() {
    const list = $("stage-list"), frames = $("frames");
    const pic = id => +id === 0 ? "og/img/assembly.png" : `og/img/stage-${String(Math.min(+id, 17)).padStart(2, "0")}.png`;
    const seen = new Set();
    SITE.stages.forEach(s => { const src = pic(s.id); if (seen.has(src)) return; seen.add(src);
      const im = new Image(); im.src = src; im.alt = ""; im.loading = "lazy"; im.decoding = "async"; im.dataset.src = src; frames.appendChild(im); });
    list.innerHTML = SITE.stages.map(s => `<li data-id="${s.id}"><h3><a href="${REPO}/tree/main/phases/${s.folder}">${s.title}</a></h3>` +
      `<p>${s.goal}</p><p class="meta">Stage ${+s.id} · ${s.steps} steps · ${s.hours} h${s.cost ? " · " + usd(s.cost) : ""}</p></li>`).join("");
    const items = [...list.children];
    function set(li) {
      items.forEach(x => x.classList.toggle("on", x === li));
      const s = SITE.stages.find(x => x.id === li.dataset.id), src = pic(s.id);
      frames.querySelectorAll("img").forEach(im => im.classList.toggle("on", im.dataset.src === src));
      $("fcap-t").textContent = s.title; $("fcap-n").textContent = "Stage " + +s.id;
    }
    if (items.length) set(items[0]);
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) set(e.target); }), { rootMargin: "-40% 0px -55% 0px" });
    items.forEach(li => io.observe(li));
  })();

  /* ---------- results: simulated runs drawn in the page's colours ---------- */
  (function results() {
    if (!SIM) return;
    const f = SIM.plastic.fit, m = SIM.plastic.made_with;
    const row = (h, o) => `<tr><th scope="row">${h}</th><td>${o.base_color.toFixed(3)}</td><td>${o.roughness.toFixed(3)}</td><td>${o.metallic.toFixed(3)}</td></tr>`;
    $("trio").tBodies[0].innerHTML = row("Made with", m) + row("Fitted", f);
    $("trio").insertAdjacentHTML("afterend", `<p>Fit error ${f.rms_pct_of_peak} % of the peak over ${f.rows} photos; ` +
      `${SIM.plastic.holdout.rms_pct_of_peak} % on ${SIM.plastic.holdout.rows_held_out} photos held out of the fit.</p>`);
    $("matte").textContent = SIM.matte_brdf.got.toFixed(4);
    const rows = SIM.mirror_40.rows, pk = rows.reduce((a, r) => r[1] > a[1] ? r : a), want = SIM.mirror_40.m4 / 2;
    $("c-mirror").setAttribute("aria-label", `Brightness against table angle for a simulated mirror lit at ${SIM.mirror_40.m4} degrees: ` +
      `the peak sits at ${pk[0]} degrees instead of ${want}.`);
    $("mirror-text").innerHTML = `Simulated run. The peak should sit at ${want}°, half the lamp angle. It sits at ${pk[0]}°: the simulator hid a ` +
      `${(want - pk[0]).toFixed(1)}° error in the table, and <code>calibrate mirror</code> measures it and takes it out.`;

    const D = Math.PI / 180, sph = (t, p) => [Math.sin(t * D) * Math.cos(p * D), Math.sin(t * D) * Math.sin(p * D), Math.cos(t * D)];
    function ggx(wi, wo, base, rough, metal) {                        // software/src/opengonio/brdf/models.py ggx_brdf
      const ci = wi[2], co = wo[2]; if (ci <= 0 || co <= 0) return 0;
      let h = [wi[0] + wo[0], wi[1] + wo[1], wi[2] + wo[2]]; const hn = Math.hypot(...h); h = h.map(x => x / hn);
      const a = Math.max(rough * rough, 1e-4), a2 = a * a, f0 = 0.04 * (1 - metal) + base * metal;
      const F = f0 + (1 - f0) * (1 - (wi[0] * h[0] + wi[1] * h[1] + wi[2] * h[2])) ** 5;
      const d = h[2] * h[2] * (a2 - 1) + 1, Dd = a2 / (Math.PI * d * d);
      const G = 2 * ci * co / (co * Math.sqrt(ci * ci * (1 - a2) + a2) + ci * Math.sqrt(co * co * (1 - a2) + a2));
      return (1 - metal) * (1 - F) * base / Math.PI + Dd * G * F / (4 * ci * co);
    }
    const pts = SIM.plastic.rows.filter(r => r[4] != null).map(r => [r[4], ggx(sph(r[0], r[1]), sph(r[2], r[3]), f.base_color, f.roughness, f.metallic)]);

    function sized(cv) {                                   // crisp at any width: draw in CSS pixels on a device-pixel canvas
      const dpr = Math.min(window.devicePixelRatio || 1, 2), W = cv.clientWidth, H = Math.round(W * +cv.dataset.aspect);
      cv.style.height = H + "px"; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      const g = cv.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0);
      const K = OG.tokens(); g.font = `${W < 480 ? 11 : 13}px ${K.text}`; g.lineWidth = 1;
      return { g, W, H, K };
    }
    function mirror() {
      const { g, W, H, K } = sized($("c-mirror")), L = 44, R = 12, T = 20, B = 40;
      const x0 = rows[0][0], x1 = rows[rows.length - 1][0], ymax = 220;
      const X = x => L + (x - x0) / (x1 - x0) * (W - L - R), Y = y => H - B - y / ymax * (H - T - B);
      g.strokeStyle = K.rule; g.fillStyle = K.ink2;
      [0, 50, 100, 150, 200].forEach(t => { g.beginPath(); g.moveTo(L, Y(t)); g.lineTo(W - R, Y(t)); g.stroke(); g.fillText(t, 10, Y(t) + 4); });
      for (let x = Math.ceil(x0); x <= x1; x++) g.fillText(x + "°", X(x) - 10, H - B + 20);
      g.textAlign = "right"; g.fillText("table angle M3", W - R, H - 4); g.textAlign = "left";
      g.strokeStyle = K.light; g.lineWidth = 1.5; g.setLineDash([5, 5]); g.beginPath(); g.moveTo(X(want), T); g.lineTo(X(want), H - B); g.stroke(); g.setLineDash([]);
      g.fillStyle = K.lightText; g.fillText(`expected ${want}°`, X(want) + 8, T + 12);
      g.strokeStyle = K.blue; g.lineWidth = 2; g.beginPath(); rows.forEach(([x, y], i) => i ? g.lineTo(X(x), Y(y)) : g.moveTo(X(x), Y(y))); g.stroke();
      g.fillStyle = K.blue; rows.forEach(([x, y]) => { g.beginPath(); g.arc(X(x), Y(y), 3, 0, 7); g.fill(); });
      g.strokeStyle = K.ink; g.lineWidth = 2; g.beginPath(); g.arc(X(pk[0]), Y(pk[1]), 8, 0, 7); g.stroke();
      g.fillStyle = K.ink; g.fillText(`peak ${pk[0]}°`, X(pk[0]) - 84, Y(pk[1]) + 4);
    }
    function fit() {
      const { g, W, H, K } = sized($("c-fit")), L = 44, R = 12, T = 16, B = 40;
      const lo = Math.log10(0.05), hi = Math.log10(2), X = v => L + (Math.log10(v) - lo) / (hi - lo) * (W - L - R), Y = v => H - B - (Math.log10(v) - lo) / (hi - lo) * (H - T - B);
      g.strokeStyle = K.rule; g.fillStyle = K.ink2;
      [0.05, 0.1, 0.2, 0.5, 1, 2].forEach(t => { g.beginPath(); g.moveTo(L, Y(t)); g.lineTo(W - R, Y(t)); g.stroke(); g.fillText(t, 12, Y(t) + 4); g.fillText(t, X(t) - 8, H - B + 20); });
      g.textAlign = "right"; g.fillText("simulated measurement, per sr (log)", W - R, H - 4); g.textAlign = "left";
      g.strokeStyle = K.light; g.lineWidth = 1.5; g.beginPath(); g.moveTo(X(0.05), Y(0.05)); g.lineTo(X(2), Y(2)); g.stroke();
      g.fillStyle = OG.alpha(K.blue, 0.85);
      pts.forEach(([m, p]) => { g.beginPath(); g.arc(X(m), Y(p), 4, 0, 7); g.fill(); });
      g.fillStyle = K.ink2; g.fillText("fitted, per sr", L + 8, T + 14);
    }
    const draw = () => { mirror(); fit(); };
    draw(); window.addEventListener("og:theme", draw);
    let rz; window.addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(draw, 120); });
    document.fonts && document.fonts.ready.then(draw);
  })();
})();
