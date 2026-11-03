/* docs/wiring.html: every wire from docs/wiring.yaml (window.WIRING, written by tools/wiring.py), one per step.
   The tungsten rings mark the wire to make now; done wires stay drawn; a dashed outline shows the next one.
   SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  "use strict";
  const W = window.WIRING;
  if (!W) return;
  const NS = "http://www.w3.org/2000/svg";
  const $ = id => document.getElementById(id);
  const svg = $("sheet"), scroll = $("scroll");
  const KINDS = { power: "+24 V power", ground: "Ground (GND, 0 V)", switch: "Limit-switch wire (+24 V line)", logic: "3.3 / 5 V logic power",
    signal: "Signal", motor: "Motor cable", home: "Home switch lead", usb: "USB data", reserved: "Reserved: do not wire" };
  const short = s => s.replace(/\s*\([^)]*\)\s*$/, "");
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

  /* steps: every wire row; a check step after a section that has checks; one step for a blocked section */
  const steps = [];
  W.groups.forEach((g, gi) => {
    if (g.blocked) { steps.push({ g: gi, type: "blocked" }); return; }
    g.wires.forEach((w, wi) => steps.push({ g: gi, type: "wire", w: wi }));
    if (g.checks.length) steps.push({ g: gi, type: "check" });
  });

  /* legend */
  const used = [...new Set(W.groups.flatMap(g => g.wires.map(w => w.kind)))];
  $("legend").innerHTML = used.map(k => `<span>${swatch(k)}${esc(KINDS[k] || k)}</span>`).join("");
  function swatch(k) {
    const edge = k === "ground" ? `<line x1="2" y1="5" x2="28" y2="5" class="wire k-ground-edge" stroke-width="6"/>` : "";
    return `<svg viewBox="0 0 30 10" aria-hidden="true">${edge}<line x1="2" y1="5" x2="28" y2="5" class="wire k-${k}" stroke-width="3.5"/></svg>`;
  }

  /* section chips */
  const chips = W.groups.map((g, gi) => {
    const b = document.createElement("button");
    b.type = "button";
    const n = g.blocked ? "do not wire" : `${g.wires.filter(w => w.d).length} wires`;
    b.innerHTML = `<b>${esc(g.title)}</b><span>Stage ${esc(g.stage)} · ${n}</span><span class="meter"><i></i></span>`;
    b.addEventListener("click", () => go(steps.findIndex(s => s.g === gi)));
    $("sections").append(b);
    return b;
  });

  /* drawing one section */
  const el = (tag, attrs, parent, text) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    if (parent) parent.append(e);
    return e;
  };
  let shown = -1, pinEls = {}, wireEls = [], over;
  function draw(gi) {
    shown = gi;
    const g = W.groups[gi];
    svg.textContent = "";
    el("title", { id: "sheet-title" }, svg, `Wiring diagram: ${g.title}`);
    svg.setAttribute("viewBox", g.view.join(" "));
    fitWidth();
    const defs = el("defs", {}, svg);
    const m = el("marker", { id: "arrow", viewBox: "0 0 10 10", refX: 8, refY: 5, markerWidth: 6, markerHeight: 6, orient: "auto-start-reverse" }, defs);
    el("path", { d: "M1 1 L9 5 L1 9 z", style: "fill:var(--light)" }, m);
    pinEls = {};
    for (const bx of g.boxes) {
      const grp = el("g", {}, svg);
      el("rect", { x: bx.x, y: bx.y, width: bx.w, height: bx.h, rx: 6, class: "box-r" }, grp);
      el("text", { x: bx.x + 12, y: bx.y + 20, class: "box-t" }, grp, bx.name);
      bx.pins.forEach((p, i) => {
        const py = bx.y + g.head + g.row * i + g.row / 2 + 2;
        const pg = el("g", {}, grp);
        el("rect", { x: bx.x + 6, y: py - 9, width: bx.w - 12, height: 18, rx: 3, class: "pin-r" }, pg);
        el("text", { x: bx.x + 14, y: py + 4, class: "pin-t" }, pg, p);
        pinEls[bx.name + "|" + p] = pg;
      });
    }
    wireEls = g.wires.map(w => {
      const grp = el("g", { "data-n": w.n }, svg);
      if (!w.d) {
        el("text", { x: w.a[0] - 12, y: w.a[1] + 4, class: "nc-t", "text-anchor": "end" }, grp, "not connected");
        el("circle", { cx: w.a[0], cy: w.a[1], r: 4, class: "badge-c", style: "stroke:var(--ink-3)" }, grp);
        return { grp, w };
      }
      const width = 3.5;
      if (w.kind === "ground") el("path", { d: w.d, class: "wire k-ground-edge", "stroke-width": width + 2.5 }, grp);
      const core = el("path", { d: w.d, class: `wire k-${w.kind}`, "stroke-width": width }, grp);
      const col = `var(--w-${w.kind === "ground" ? "ground-edge" : w.kind})`;
      for (const p of [w.a, w.b]) el("circle", { cx: p[0], cy: p[1], r: 4.2, style: `fill:${col}` }, grp);
      el("circle", { cx: w.badge[0], cy: w.badge[1], r: 9, class: "badge-c", style: `stroke:${col}` }, grp);
      el("text", { x: w.badge[0], y: w.badge[1] + 3.5, class: "badge-t", "text-anchor": "middle" }, grp, w.n);
      return { grp, core, w };
    });
    over = el("g", {}, svg);
  }

  /* the whole section when it fits with pin labels at >= 85 % size (about 10 px); otherwise scroll, following the wire */
  function fitWidth() {
    const g = W.groups[shown];
    if (!g) return;
    const need = Math.round(g.view[2] * 0.85);
    svg.style.minWidth = scroll.clientWidth >= need ? "0px" : `${Math.max(760, need)}px`;
  }
  addEventListener("resize", fitWidth);

  /* one step */
  let cur = 0;
  function render(i) {
    cur = i;
    const s = steps[i], g = W.groups[s.g];
    if (shown !== s.g) draw(s.g);
    const wi = s.type === "wire" ? s.w : g.wires.length;          // check / blocked: everything drawn
    wireEls.forEach((we, k) => {
      const vis = s.type !== "wire" || k <= wi;
      we.grp.style.display = vis ? "" : "none";
      we.grp.style.opacity = s.type === "wire" && k < wi ? "0.85" : "1";
      if (we.core) we.core.setAttribute("stroke-width", s.type === "wire" && k === wi ? 6 : 3.5);
    });
    Object.values(pinEls).forEach(p => p.classList.remove("pin-on"));
    over.textContent = "";
    let focus = [];
    if (s.type === "wire") {
      const w = g.wires[wi];
      const ends = [w.a].concat(w.b ? [w.b] : []);
      const pa = pinEls[w.from.part + "|" + w.from.pin], pb = w.to && pinEls[w.to.part + "|" + w.to.pin];
      if (pa) pa.classList.add("pin-on");
      if (pb) pb.classList.add("pin-on");
      if (w.d) el("path", { d: w.d, class: "flow", "marker-end": "url(#arrow)" }, over);
      ends.forEach(p => el("circle", { cx: p[0], cy: p[1], r: 11, class: "ring" }, over));
      focus = ends;
      const n = steps[i + 1];
      if (n && n.type === "wire" && n.g === s.g) {
        const nw = g.wires[n.w];
        if (nw.d) el("path", { d: nw.d, class: "ghost" }, over);
        [nw.a].concat(nw.b ? [nw.b] : []).forEach(p => el("circle", { cx: p[0], cy: p[1], r: 9, class: "ring-next" }, over));
      }
    }
    card(s, g);
    chips.forEach((b, gi) => {
      const mine = steps.map((x, k) => [x, k]).filter(([x]) => x.g === gi);
      const done = mine.filter(([, k]) => k < i).length;
      b.setAttribute("aria-current", String(gi === s.g));
      b.querySelector(".meter i").style.transform = `scaleX(${(done / Math.max(1, mine.length)).toFixed(3)})`;
    });
    if (scroll.scrollWidth > scroll.clientWidth + 4 && focus.length) {
      /* both ends in view when they fit; otherwise the start pin with its whole box (pins sit on a box's right edge) */
      const k = svg.getBoundingClientRect().width / g.view[2], xs = focus.map(p => (p[0] - g.view[0]) * k);
      const lo = Math.min(...xs), hi = Math.max(...xs), cw = scroll.clientWidth;
      const left = hi - lo < cw * 0.85 ? (lo + hi) / 2 - cw / 2 : xs[0] - cw * 0.72;
      scroll.scrollTo({ left: Math.max(0, left), behavior: OG && OG.reduced ? "auto" : "smooth" });
    }
    const chip = chips[s.g];
    chip.scrollIntoView({ block: "nearest", inline: "nearest" });
    if (location.hash !== `#step-${i + 1}`) history.replaceState(null, "", `#step-${i + 1}`);
  }

  function card(s, g) {
    const secN = s.g + 1, total = W.groups.length;
    $("k-sec").textContent = `Section ${secN} of ${total} · stage ${g.stage}`;
    $("k-step").textContent = `Step ${cur + 1} of ${steps.length}`;
    const first = steps.findIndex(x => x.g === s.g) === cur;
    const intro = first && g.intro ? `<p class="intro-text">${g.intro}</p>` : "";
    let html = "";
    if (s.type === "blocked") {
      $("s-title").textContent = g.title.replace(/^\d+ · /, "");
      html = `<p class="warn">${g.intro}</p><p class="note">These pins are kept free so nothing else takes them. Nothing to wire here.</p>`;
    } else if (s.type === "check") {
      $("s-title").textContent = "Check before going on";
      html = `<ol class="checks">${g.checks.map(c => `<li>${c}</li>`).join("")}</ol>
        <p class="note">Meter: black probe in COM, red in the V/Ω socket (marked INPUT on some meters; never 10A, mA or µA). Continuity setting for beeps, DC volts (V⎓) for voltage.</p>`;
    } else {
      const w = g.wires[s.w];
      if (!w.d) {
        $("s-title").textContent = `${short(w.from.part)}: ${w.from.pin}`;
        html = `<dl class="ends"><dt>Pin</dt><dd><b>${esc(short(w.from.part))}</b> · ${esc(w.from.pin)}</dd><dt>Action</dt><dd>Leave it unconnected.</dd>
          ${w.note ? `<dt>Note</dt><dd class="note">${w.note}</dd>` : ""}</dl>`;
      } else {
        $("s-title").textContent = `${short(w.from.part)} ${w.from.pin} → ${short(w.to.part)} ${w.to.pin}`;
        html = `<dl class="ends">
          <dt>From</dt><dd><b>${esc(short(w.from.part))}</b> · ${esc(w.from.pin)}</dd>
          <dt>To</dt><dd><b>${esc(short(w.to.part))}</b> · ${esc(w.to.pin)}</dd>
          <dt>Wire</dt><dd><span class="kind">${swatch(w.kind)}${esc(KINDS[w.kind] || w.label)}</span><br>${w.wire}</dd>
          ${w.note ? `<dt>Note</dt><dd class="note">${w.note}</dd>` : ""}</dl>`;
      }
    }
    $("s-body").innerHTML = intro + html;
    $("back").disabled = cur === 0;
    $("next").textContent = cur === steps.length - 1 ? "Done" : "Next";
    $("next").disabled = cur === steps.length - 1;
  }

  function go(i) { render(Math.max(0, Math.min(steps.length - 1, i))); }
  $("back").addEventListener("click", () => go(cur - 1));
  $("next").addEventListener("click", () => go(cur + 1));
  document.addEventListener("keydown", e => {
    if (e.target.closest && e.target.closest("input, textarea, select, #scroll")) return;   // in the diagram, arrows scroll it
    if (e.key === "ArrowRight") go(cur + 1);
    if (e.key === "ArrowLeft") go(cur - 1);
  });
  const fromHash = () => { const m = /^#step-(\d+)$/.exec(location.hash); return m ? +m[1] - 1 : 0; };
  window.addEventListener("hashchange", () => { const k = fromHash(); if (k !== cur) go(k); });
  go(fromHash());
  window.__wiring = { steps: () => steps.length, go };
})();
