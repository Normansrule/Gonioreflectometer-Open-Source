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
    const born = performance.now();
    const wide = window.matchMedia("(min-width: 901px)"), shift = () => wide.matches ? 0.19 : 0;   // the copy sits on the left
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
      const W = canvas.clientWidth;                     // never closer than 16 px to the screen edge
      labels.forEach((el, i) => { const q = spec.project(spots[i], -1.15), hw = el.offsetWidth / 2 + 16;
        if (q) { el.style.left = Math.max(hw, Math.min(W - hw, q[0])) + "px"; el.style.top = q[1] + "px"; } });
    }
    function frame(now) {
      const dt = Math.min((now - last) / 1000, 1 / 30); last = now;
      const idle = !OG.reduced && now - lastInput > 4000;
      if (idle) { const s = (now - t0) / 1000; th.target = 52 - 18 * Math.cos(0.16 * s); ph.target = 90 + 80 * Math.sin(0.11 * s); }
      const a = th.step(dt), b = ph.step(dt);
      const warm = OG.reduced ? 1 : Math.min(1, (now - born) / 1800), gain = warm * warm * (3 - 2 * warm);   // the lamp comes up like a tungsten filament
      if (spec) { spec.draw(th.x, ph.x, shift(), gain); place(); }
      readout();
      running = visible && (a || b || idle || warm < 1);
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
    window.addEventListener("resize", () => { if (spec) { spec.draw(th.x, ph.x, shift()); place(); } });
    window.addEventListener("og:theme", () => { if (spec) spec.draw(th.x, ph.x, shift()); });
    OG.onReduce(() => { lastInput = performance.now(); kick(); });
    readout(); kick();
    // for tools/readme_screens.py: put the lamp somewhere exact and draw one frame
    window.__hero = { set(t, p) { lastInput = performance.now(); th.x = th.target = t; ph.x = ph.target = p; th.v = ph.v = 0;
      if (spec) { spec.draw(t, p, shift()); place(); } readout(); } };
  })();

  /* the CAD mesh (og/model/rig.js, about 1 MB) loads once, when the first view of it nears the screen */
  let rigLoad = null;
  function loadRig() {
    return rigLoad || (rigLoad = new Promise((ok, fail) => {
      if (window.RIG) return ok();
      const sc = document.createElement("script"); sc.src = "og/model/rig.js"; sc.onload = () => ok(); sc.onerror = fail; document.body.appendChild(sc);
    }));
  }

  /* ---------- the story: scroll builds the machine, then plays each axis, then looks through the camera ---------- */
  (function story() {
    const sec = $("machine"), canvas = $("storyc"); if (!sec || !canvas) return;
    const still = OG.reduced;
    if (still) sec.classList.add("still");
    let sizedW = 0;                                   // fix the height in px once: phone URL bars must not shift the story
    function size() { if (still || innerWidth === sizedW) return; sizedW = innerWidth;
      sec.style.height = Math.round(innerHeight * (innerWidth > 900 ? 6.2 : 5.6)) + "px"; }
    size(); addEventListener("resize", size);
    const B = [0, 0.2, 0.36, 0.52, 0.68, 0.84, 1];                       // chapter starts, as a fraction of the scroll
    const AX = [null, ["M4", [100, 55, 170, 100]], ["M3", [40, 15, 62, 40]], ["M2", [0, 35, -30, 0]], ["M1", [0, 150, 0]], null];
    const base = { M4: 100, M3: 40, M2: 0, M1: 0 };
    const chapters = [...sec.querySelectorAll(".chapter")], dots = [...sec.querySelectorAll("[data-ch]")];
    const sm = x => x * x * (3 - 2 * x), clamp = x => Math.max(0, Math.min(1, x)), lerp = (a, b, t) => a + (b - a) * t;
    const along = (path, u) => { const n = path.length - 1, f = clamp(u) * n, i = Math.min(Math.floor(f), n - 1); return lerp(path[i], path[i + 1], sm(f - i)); };
    let R = null, rv = null, target = 0, p = 0, raf = 0, visible = false, last = 0, shown = -1;
    function progress() { const r = sec.getBoundingClientRect(), span = r.height - innerHeight; return span > 0 ? clamp(-r.top / span) : 0; }
    function frame(q) {
      let ch = B.findIndex((b, i) => q >= b && q < B[i + 1]); if (ch < 0) ch = B.length - 2;
      const u = (q - B[ch]) / (B[ch + 1] - B[ch]);
      const pose = { ...base }; let hi = [];
      if (AX[ch]) { pose[AX[ch][0]] = along(AX[ch][1], u); hi = R.axes[AX[ch][0]].moves; }
      const explode = still ? 0 : 1 - sm(clamp(q / 0.17));
      const yaw = ch === 0 ? lerp(-18, -62, sm(clamp(u))) : lerp(-62, -150, clamp((q - B[1]) / (B[5] - B[1])));
      const zf = innerWidth > 900 ? 1 : 0.72;            // phones: closer, the machine fills the narrow frame
      const orb = rv.orbit({ yaw, pitch: ch === 0 ? lerp(58, 26, sm(u)) : 26, zoom: (ch === 0 ? lerp(1.45, 0.98, sm(u)) : 0.98) * zf }, rv.aspect());
      let cam = orb;
      if (ch === 5) {                                   // into the measuring camera: what it sees, from where it stands
        const t = sm(clamp(u * 1.2)), far = rv.aspect() < 1 ? 1.5 : 1, lens = { eye: [1250 * far, -330 * far, 470 * far], at: [120, 0, 150], fov: 0.52 };   // over the camera's shoulder
        const end = rv.orbit({ yaw: -150, pitch: 26, zoom: 0.98 * zf }, rv.aspect());
        cam = { eye: end.eye.map((e, i) => lerp(e, lens.eye[i], t)), at: end.at.map((a, i) => lerp(a, lens.at[i], t)), fov: lerp(end.fov, lens.fov, t) };
      }
      const wide = innerWidth > 900, shift = wide ? (ch === 5 ? 0.3 : 0.3) : 0;
      rv.draw(pose, cam, { hi, explode, shift, spread: wide ? 1 : 0.45 });
      if (ch !== shown) { shown = ch; chapters.forEach((c, i) => c.classList.toggle("on", i === ch));
        dots.forEach((d, i) => d.setAttribute("aria-current", String(i === ch))); }
      const a = RigView.angles(pose); $("st-ti").textContent = Math.round(a.ti) + "°"; $("st-tr").textContent = Math.round(a.tr) + "°";
      sec.style.setProperty("--chapter-u", u.toFixed(3));
    }
    function loop(now) {
      const dt = Math.min((now - last) / 1000, 0.05); last = now;
      p = still ? target : p + (target - p) * Math.min(1, dt * 7);     // a little inertia, like a heavy dial
      if (rv) frame(p);
      raf = visible && Math.abs(target - p) > 1e-4 ? requestAnimationFrame(loop) : 0;
    }
    function kick() { target = still ? 0.19 : progress(); if (!raf && visible) { last = performance.now(); raf = requestAnimationFrame(loop); } }
    addEventListener("scroll", kick, { passive: true });
    addEventListener("resize", () => { if (rv) frame(p); });
    window.addEventListener("og:theme", () => { if (rv) frame(p); });
    dots.forEach(d => d.addEventListener("click", () => {
      const i = +d.dataset.ch, r = sec.getBoundingClientRect(), span = r.height - innerHeight;
      scrollTo({ top: scrollY + r.top + span * (B[i] + 0.02), behavior: OG.reduced ? "auto" : "smooth" }); }));
    new IntersectionObserver(es => { visible = es[0].isIntersecting;
      if (visible && !R) loadRig().then(async () => {
        R = window.RIG;
        try { rv = await RigView.make(canvas, R); } catch (e) { rv = null; }
        $("st-loading").hidden = true;
        if (!rv) { sec.classList.add("nogl"); return; }
        p = target = still ? 0.19 : progress(); frame(p);   // reduced motion: one still picture, the machine built
        $("st-parts").textContent = R.parts;
      }, () => { $("st-loading").hidden = true; sec.classList.add("nogl"); });
      if (visible) kick(); }, { rootMargin: "600px 0px" }).observe(sec);
    window.__story = { at(q) { p = target = q; if (rv) frame(q); }, ready: () => !!rv };
  })();

  /* ---------- the four-axis machine: CAD mesh, real kinematics, played in turn or driven by hand ---------- */
  (function rig() {
    const stage = $("rig-stage"), canvas = $("rigc"); if (!stage) return;
    const NAMES = { M4: "Lamp arm", M3: "Table", M2: "Tilt", M1: "Spin" };
    const SEQ = [
      { k: "M4", what: "The lamp swings around the 12 inch ring", path: [100, 55, 170, 100] },
      { k: "M3", what: "The table turns the sample toward the camera", path: [40, 15, 62, 40] },
      { k: "M2", what: "The sample tilts out of the plane", path: [0, 35, -30, 0] },
      { k: "M1", what: "The sample spins on its own axis", path: [0, 150, 0] },
    ];
    const pose = { M4: 100, M3: 40, M2: 0, M1: 0 };
    const view = { yaw: -62, pitch: 26, zoom: 0.72 };
    let R = null, rv = null, playing = !OG.reduced, active = "M4", seg = 0, t0 = 0, visible = false, raf = 0, last = 0, drag = null;
    const ease = x => x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
    const SEG = 1.7, HOLD = 0.6;
    function setActive(k, what) {
      active = k; $("rig-axis").textContent = k; $("rig-what").textContent = what || SEQ.find(s => s.k === k).what;
      document.querySelectorAll("[data-rig-axis]").forEach(b => b.setAttribute("aria-current", String(b.dataset.rigAxis === k)));
    }
    function sync() {
      ["M4", "M3", "M2", "M1"].forEach(k => { const r = $("rig-r-" + k); if (r && document.activeElement !== r) r.value = pose[k];
        const o = $("rig-o-" + k); if (o) o.textContent = Math.round(pose[k]) + "°"; });
      const a = RigView.angles(pose); $("rig-ti").textContent = Math.round(a.ti) + "°"; $("rig-tr").textContent = Math.round(a.tr) + "°";
    }
    function draw() { if (rv) rv.draw(pose, view, { hi: R.axes[active].moves }); sync(); }
    function step(now) {
      const dt = Math.min((now - last) / 1000, 0.05); last = now;
      if (playing) {
        if (!OG.reduced && !drag) view.yaw += dt * 4;
        const s = SEQ[seg], legs = s.path.length - 1, total = legs * SEG + HOLD, t = (now - t0) / 1000;
        if (t >= total) { pose[s.k] = s.path[legs]; seg = (seg + 1) % SEQ.length; t0 = now; setActive(SEQ[seg].k); }
        else { const i = Math.min(Math.floor(t / SEG), legs - 1), f = ease(Math.min((t - i * SEG) / SEG, 1));
          pose[s.k] = s.path[i] + (s.path[i + 1] - s.path[i]) * f; }
      }
      draw();
      raf = visible && (playing || drag) ? requestAnimationFrame(step) : 0;
    }
    function kick() { if (!raf && visible) { last = performance.now(); raf = requestAnimationFrame(step); } }
    function setPlaying(p) {
      playing = p; const b = $("rig-play"); b.textContent = p ? "Pause" : "Play"; b.setAttribute("aria-pressed", String(p));
      if (p) { seg = SEQ.findIndex(s => s.k === active); SEQ.forEach(s => { pose[s.k] = s.path[0]; }); t0 = performance.now(); kick(); }
    }
    function controls() {
      $("rig-axes").innerHTML = SEQ.map(s => { const [lo, hi] = R.ranges[s.k];
        return `<div class="rig-axis"><button type="button" class="chip" data-rig-axis="${s.k}" aria-current="false" title="Play ${s.k}">` +
          `<b>${s.k}</b> ${NAMES[s.k]}</button><input type="range" id="rig-r-${s.k}" min="${lo}" max="${hi}" step="1" value="${pose[s.k]}" ` +
          `aria-label="${s.k} ${NAMES[s.k]}, degrees"><output id="rig-o-${s.k}"></output></div>`; }).join("");
      SEQ.forEach(s => {
        $("rig-r-" + s.k).addEventListener("input", e => { setPlaying(false); pose[s.k] = +e.target.value; setActive(s.k, `${NAMES[s.k]} at ${pose[s.k]}°`);
          const a = RigView.angles(pose); $("rig-live").textContent = `${s.k} ${pose[s.k]} degrees: incidence ${Math.round(a.ti)}, reflection ${Math.round(a.tr)}`; draw(); });
      });
      document.querySelectorAll("[data-rig-axis]").forEach(b => b.addEventListener("click", () => {
        const i = SEQ.findIndex(s => s.k === b.dataset.rigAxis); seg = i; SEQ.forEach(s => { pose[s.k] = s.path[0]; });
        setActive(SEQ[i].k); playing = true; $("rig-play").textContent = "Pause"; $("rig-play").setAttribute("aria-pressed", "true");
        t0 = performance.now(); kick(); }));
      $("rig-play").addEventListener("click", () => setPlaying(!playing));
      if (!playing) { $("rig-play").textContent = "Play"; $("rig-play").setAttribute("aria-pressed", "false"); }
    }
    stage.addEventListener("pointerdown", e => { drag = { x: e.clientX, y: e.clientY, yaw: view.yaw, pitch: view.pitch }; stage.setPointerCapture(e.pointerId); kick(); });
    stage.addEventListener("pointermove", e => { if (!drag) return; view.yaw = drag.yaw - (e.clientX - drag.x) * 0.3;
      view.pitch = Math.max(4, Math.min(70, drag.pitch + (e.clientY - drag.y) * 0.25)); if (!playing) draw(); });
    const up = () => { drag = null; }; stage.addEventListener("pointerup", up); stage.addEventListener("pointercancel", up);
    async function init() {
      R = window.RIG;   // loaded by loadRig()
      try { rv = R && window.RigView ? await RigView.make(canvas, R) : null; } catch (e) { rv = null; }
      $("rig-loading").hidden = true;
      if (!rv) { stage.classList.add("nogl"); $("rig-controls").hidden = true; return; }
      controls(); setActive("M4"); t0 = performance.now(); draw(); kick();
    }
    let asked = false;
    new IntersectionObserver(es => { visible = es[0].isIntersecting;
      if (visible && !asked) { asked = true;
        loadRig().then(init, () => { $("rig-loading").hidden = true; stage.classList.add("nogl"); $("rig-controls").hidden = true; }); }
      if (visible) kick(); }, { rootMargin: "400px 0px" }).observe(stage);
    window.addEventListener("og:theme", draw);
    window.addEventListener("resize", () => { if (!raf) draw(); });
    // for tools/readme_screens.py: an exact pose and highlighted axis, one frame
    window.__rig = { ready: () => !!rv, seq: SEQ, set(p, k, yaw) { playing = false; Object.assign(pose, p); if (yaw != null) view.yaw = yaw;
      setActive(k); draw(); } };
  })();

  /* ---------- the cursor is the lamp's handle; buttons lean toward the pointer ---------- */
  (function pointerCraft() {
    const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
    if (!fine || OG.reduced) return;
    const stage = $("stage"), ring = document.createElement("div");
    ring.className = "lamp-cursor"; ring.setAttribute("aria-hidden", "true"); ring.innerHTML = "<span>Lamp</span>";
    stage.appendChild(ring); stage.classList.add("has-cursor");
    const x = OG.spring(0, 380, 34), y = OG.spring(0, 380, 34); let raf = 0, on = false;
    const tick = () => { const a = x.step(1 / 60), b = y.step(1 / 60);
      ring.style.transform = `translate(${x.x}px, ${y.x}px)`; raf = (a || b) ? requestAnimationFrame(tick) : 0; };
    stage.addEventListener("pointermove", e => { const r = stage.getBoundingClientRect();
      x.target = e.clientX - r.left; y.target = e.clientY - r.top;
      if (!on) { on = true; x.x = x.target; y.x = y.target; ring.classList.add("on"); }
      if (!raf) raf = requestAnimationFrame(tick); });
    stage.addEventListener("pointerleave", () => { on = false; ring.classList.remove("on"); });
    document.querySelectorAll(".hero .acts .btn").forEach(btn => {               // magnetic, on a stiff spring, small reach
      const dx = OG.spring(0, 260, 22), dy = OG.spring(0, 260, 22); let r2 = 0;
      const t2 = () => { const a = dx.step(1 / 60), b = dy.step(1 / 60); btn.style.translate = `${dx.x.toFixed(2)}px ${dy.x.toFixed(2)}px`;
        r2 = (a || b) ? requestAnimationFrame(t2) : 0; };
      btn.addEventListener("pointermove", e => { const r = btn.getBoundingClientRect();
        dx.target = (e.clientX - r.left - r.width / 2) * 0.22; dy.target = (e.clientY - r.top - r.height / 2) * 0.3; if (!r2) r2 = requestAnimationFrame(t2); });
      btn.addEventListener("pointerleave", () => { dx.target = dy.target = 0; if (!r2) r2 = requestAnimationFrame(t2); });
    });
  })();

  /* ---------- numbers that count up once, when they arrive ---------- */
  (function counts() {
    const els = [...document.querySelectorAll("[data-count]")];
    const fmt = (el, v) => { const d = +(el.dataset.dec || 0); el.textContent = (el.dataset.pre || "") + v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }); };
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return; io.unobserve(e.target);
      const el = e.target, to = +el.dataset.count;
      if (OG.reduced) return fmt(el, to);
      const t0 = performance.now(), dur = 1400;
      const run = now => { const k = Math.min(1, (now - t0) / dur), ease = 1 - Math.pow(1 - k, 4); fmt(el, to * ease); if (k < 1) requestAnimationFrame(run); };
      requestAnimationFrame(run);
    }), { threshold: 0.6 });
    els.forEach(el => { fmt(el, OG.reduced ? +el.dataset.count : 0); io.observe(el); });
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
  if (SITE.steps) { $("n-steps").dataset.count = SITE.steps; $("n-hours").dataset.count = Math.round(SITE.hours);
    $("n-cost").dataset.count = Math.round(SITE.plan_usd); }
  if (SITE.parts) { $("n-parts").dataset.count = SITE.parts; $("n-parts").textContent = SITE.parts; }
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
