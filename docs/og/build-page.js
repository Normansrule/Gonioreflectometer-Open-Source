/* docs/build.html: the build book. One step per page; the CAD assembly (og/model/rig.js) drawn in WebGL with the parts
   already on in grey and this step's parts in colour, sliding in along dashed arrows. Steps from build-book.js
   (tools/build_book.py, from docs/assembly.yaml + .github/phases.yml). `?print` lays every step out as a page.
   SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  "use strict";
  const R = window.RIG, B = window.BOOK;
  if (!R || !B || !R.spans) return;
  const $ = id => document.getElementById(id);
  const printing = /[?&]print\b/.test(location.search);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const steps = B.steps, N = steps.length;
  const stepOf = new Int16Array(R.names.length).fill(-1);
  steps.forEach((s, k) => s.parts.forEach(i => { stepOf[i] = k; }));
  const kindOf = {};
  steps.forEach(s => s.items.forEach(it => it.parts.forEach(i => { kindOf[i] = it.kind; })));

  /* ---------- matrices (column-major, as rigview.js) ---------- */
  function mul(a, b) { const o = new Array(16).fill(0);
    for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) for (let k = 0; k < 4; k++) o[c * 4 + r] += a[k * 4 + r] * b[c * 4 + k]; return o; }
  const sub = (a, b) => a.map((x, i) => x - b[i]), dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const norm = a => { const l = Math.hypot(...a) || 1; return a.map(x => x / l); };
  function lookAt(eye, at, up) {
    const z = norm(sub(eye, at)), x = norm(cross(up, z)), y = cross(z, x);
    return [x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -dot(x, eye), -dot(y, eye), -dot(z, eye), 1];
  }
  function persp(fov, asp, n, f) { const t = 1 / Math.tan(fov / 2);
    return [t / asp, 0, 0, 0, 0, t, 0, 0, 0, 0, (f + n) / (n - f), -1, 0, 0, 2 * f * n / (n - f), 0]; }
  function project(VP, p, w, h) {
    const x = VP[0] * p[0] + VP[4] * p[1] + VP[8] * p[2] + VP[12], y = VP[1] * p[0] + VP[5] * p[1] + VP[9] * p[2] + VP[13],
      q = VP[3] * p[0] + VP[7] * p[1] + VP[11] * p[2] + VP[15];
    return [(x / q * 0.5 + 0.5) * w, (0.5 - y / q * 0.5) * h];
  }

  /* ---------- GL ---------- */
  const VERT = `
attribute vec3 aPos; attribute vec3 aNrm; uniform mat4 uVP; uniform float uScale; uniform vec3 uOff;
varying vec3 vN; varying vec3 vW;
void main(){ vec3 w = aPos * uScale + uOff; vW = w; vN = aNrm; gl_Position = uVP * vec4(w, 1.0); }`;
  const FRAG = `
precision highp float;
varying vec3 vN; varying vec3 vW; uniform vec3 uCol; uniform vec3 uEye; uniform vec3 uKey; uniform vec3 uSky; uniform vec3 uFloor;
uniform float uGlow; uniform vec3 uGlowCol;
void main(){
  vec3 n = normalize(vN); vec3 v = normalize(uEye - vW);
  if (dot(n, v) < 0.0) n = -n;
  float diff = max(dot(n, uKey), 0.0);
  vec3 h = normalize(uKey + v); float spec = pow(max(dot(n, h), 0.0), 40.0) * 0.18;
  vec3 hemi = mix(uFloor, uSky, n.z * 0.5 + 0.5);
  float edge = pow(1.0 - max(dot(n, v), 0.0), 2.0);
  vec3 c = uCol * (hemi + 0.72 * diff) + spec - uCol * 0.35 * edge + uGlowCol * uGlow * edge;
  gl_FragColor = vec4(pow(clamp(c, 0.0, 1.0), vec3(1.0/2.2)), 1.0);
}`;
  const lin = c => c.map(x => Math.pow(x, 2.2));
  const hex = h => OG.rgb(h.trim().length === 4 ? "#" + h.trim().slice(1).replace(/./g, "$&$&") : h.trim());

  const canvas = $("view");
  let gl = null, P, U = {}, nIdx = 0, info = null;

  async function inflate(b64) {
    const bin = Uint8Array.from(atob(b64), ch => ch.charCodeAt(0));
    const ds = new DecompressionStream("deflate");
    return new Uint8Array(await new Response(new Blob([bin]).stream().pipeThrough(ds)).arrayBuffer());
  }

  async function init() {
    gl = canvas.getContext("webgl", { antialias: true, alpha: false, preserveDrawingBuffer: true });
    if (!gl || typeof DecompressionStream === "undefined" || !gl.getExtension("OES_element_index_uint")) { gl = null; return; }
    const raw = await inflate(R.data);
    const ST = R.stride, vbytes = R.vertices * ST;
    const sh = (t, src) => { const s = gl.createShader(t); gl.shaderSource(s, src); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
    P = gl.createProgram(); gl.attachShader(P, sh(gl.VERTEX_SHADER, VERT)); gl.attachShader(P, sh(gl.FRAGMENT_SHADER, FRAG));
    gl.linkProgram(P);
    const vb = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, vb); gl.bufferData(gl.ARRAY_BUFFER, raw.subarray(0, vbytes), gl.STATIC_DRAW);
    const ib = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint32Array(raw.buffer.slice(raw.byteOffset + vbytes, raw.byteOffset + raw.byteLength)), gl.STATIC_DRAW);
    nIdx = (raw.byteLength - vbytes) / 4;
    gl.useProgram(P);
    const pos = gl.getAttribLocation(P, "aPos"), nrm = gl.getAttribLocation(P, "aNrm");
    gl.enableVertexAttribArray(pos); gl.vertexAttribPointer(pos, 3, gl.SHORT, false, ST, 0);
    gl.enableVertexAttribArray(nrm); gl.vertexAttribPointer(nrm, 3, gl.BYTE, true, ST, 6);
    ["uVP", "uScale", "uOff", "uCol", "uEye", "uKey", "uSky", "uFloor", "uGlow", "uGlowCol"].forEach(n => { U[n] = gl.getUniformLocation(P, n); });
    gl.uniform1f(U.uScale, R.scale);
    gl.enable(gl.DEPTH_TEST);
    /* per-part centre and box, from the mesh itself */
    const dv = new DataView(raw.buffer, raw.byteOffset, vbytes);
    info = R.spans.map(([v0, nv]) => {
      const lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9];
      for (let k = v0; k < v0 + nv; k++) for (let a = 0; a < 3; a++) {
        const x = dv.getInt16(k * ST + a * 2, true) * R.scale; if (x < lo[a]) lo[a] = x; if (x > hi[a]) hi[a] = x; }
      return { lo, hi, c: lo.map((x, a) => (x + hi[a]) / 2) };
    });
  }

  /* where each new part starts: `from` in docs/assembly.yaml */
  function offsets(k) {
    const s = steps[k], lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9];
    s.parts.forEach(i => { for (let a = 0; a < 3; a++) { lo[a] = Math.min(lo[a], info[i].lo[a]); hi[a] = Math.max(hi[a], info[i].hi[a]); } });
    const mid = lo.map((x, a) => (x + hi[a]) / 2), size = Math.max(...hi.map((x, a) => x - lo[a]));
    const d = Math.min(150, 70 + 0.25 * size);
    const o = {};
    s.parts.forEach((i, j) => {
      const c = info[i].c;
      switch (s.from) {
        case "+x": o[i] = [d, 0, 0]; break;
        case "-x": o[i] = [-d, 0, 0]; break;
        case "+y": o[i] = [0, d, 0]; break;
        case "-y": o[i] = [0, -d, 0]; break;
        case "out": {
          let v = [c[0] - mid[0], c[1] - mid[1], 0];
          if (Math.hypot(v[0], v[1]) < 1) v = [0, 0, 1];
          v = norm(v); o[i] = [v[0] * d * 0.6, v[1] * d * 0.6, v[2] ? d : 0.25 * d]; break;
        }
        default: o[i] = [0, 0, d];
      }
      if (s.stack) o[i] = o[i].map(x => x * (0.35 + 0.45 * j));   // a stack: each part further out, in the order it goes in
    });
    return { o, lo, hi };
  }

  function colours() {
    const cs = getComputedStyle(document.body), K = OG.tokens();
    const light = K.theme === "light";
    return { bg: lin(hex(cs.getPropertyValue("--paper") || K.g2)), done: lin(hex(cs.getPropertyValue("--done"))),
      print: lin(hex(cs.getPropertyValue("--new-print"))), buy: lin(hex(cs.getPropertyValue("--new-buy"))),
      thumb: lin(hex(K.g3)), glow: lin(hex(K.light)), light,
      sky: light ? [0.62, 0.62, 0.64] : [0.46, 0.47, 0.52], floor: light ? [0.32, 0.31, 0.3] : [0.16, 0.15, 0.15] };
  }

  /* a camera that frames a box (with the start positions of moving parts) */
  function camera(lo, hi, view, aspect, fov) {
    const at = lo.map((x, a) => (x + hi[a]) / 2);
    const r = Math.max(110, Math.hypot(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]) / 2);
    const fx = 2 * Math.atan(Math.tan(fov / 2) * aspect), f = Math.min(fov, fx);
    const dist = r / Math.sin(f / 2) * 1.02;
    const y = view[0] * Math.PI / 180, p = view[1] * Math.PI / 180;
    return { at, eye: [at[0] + dist * Math.cos(p) * Math.cos(y), at[1] + dist * Math.cos(p) * Math.sin(y), at[2] + dist * Math.sin(p)] };
  }

  function drawParts(list, VP, eye, C, colourOf, off, glow) {
    gl.uniformMatrix4fv(U.uVP, false, VP);
    gl.uniform3fv(U.uEye, eye);
    const key = norm(sub(eye, [0, 0, 0])), side = norm(cross([0, 0, 1], key));
    gl.uniform3fv(U.uKey, norm([key[0] * 0.55 + side[0] * 0.5, key[1] * 0.55 + side[1] * 0.5, 0.75]));
    gl.uniform3fv(U.uSky, C.sky); gl.uniform3fv(U.uFloor, C.floor); gl.uniform3fv(U.uGlowCol, C.glow);
    for (const i of list) {
      const [, , i0, ni] = R.spans[i];
      gl.uniform3fv(U.uCol, colourOf(i));
      gl.uniform3fv(U.uOff, off ? off(i) : [0, 0, 0]);
      gl.uniform1f(U.uGlow, glow ? glow(i) : 0);
      gl.drawElements(gl.TRIANGLES, ni, gl.UNSIGNED_INT, i0 * 4);
    }
  }

  const FOV = 0.6;
  /* the slide: each part in the order listed, 70 ms apart, 900 ms each, exponential ease-out (fast start, soft landing) */
  const SLIDE = 0.9, STAGGER = 0.07;
  const settle = (el, j) => { const x = Math.max(0, Math.min(1, (el - j * STAGGER) / SLIDE)); return x >= 1 ? 1 : 1 - Math.pow(2, -10 * x); };
  const slideEnd = k => SLIDE + STAGGER * (steps[k].parts.length - 1);

  /* one frame of step k, `el` seconds into its slide (0 = every part at the start of its arrow, Infinity = all in place) */
  function render(k, el, adj, w, h, shift) {
    const s = steps[k], C = colours(), { o, lo, hi } = offsets(k);
    const blo = lo.slice(), bhi = hi.slice();
    s.parts.forEach(i => { for (let a = 0; a < 3; a++) { blo[a] = Math.min(blo[a], info[i].lo[a] + o[i][a]); bhi[a] = Math.max(bhi[a], info[i].hi[a] + o[i][a]); } });
    const base = s.view || [-45, 30];
    const view = [base[0] + adj.yaw, Math.max(4, Math.min(86, base[1] + adj.pitch))];
    const cam = camera(blo, bhi, view, w / h * (1 - Math.abs(shift)), FOV);
    const S = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, shift, 0, 0, 1];
    const VP = mul(S, mul(persp(FOV, w / h, 10, 8000), lookAt(cam.eye, cam.at, [0, 0, 1])));
    gl.viewport(0, 0, w, h);
    gl.clearColor(C.bg[0] ** (1 / 2.2), C.bg[1] ** (1 / 2.2), C.bg[2] ** (1 / 2.2), 1);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    const done = []; for (let i = 0; i < stepOf.length; i++) if (stepOf[i] >= 0 && stepOf[i] < k) done.push(i);
    drawParts(done, VP, cam.eye, C, () => C.done);
    const order = new Map(s.parts.map((i, j) => [i, j])), off = i => { const e = settle(el, order.get(i)); return o[i].map(x => x * (1 - e)); };
    drawParts(s.parts, VP, cam.eye, C, i => (kindOf[i] === "buy" ? C.buy : C.print), off, () => 0.6);
    const arrows = s.parts.map(i => [project(VP, info[i].c.map((x, a) => x + o[i][a]), w, h), project(VP, info[i].c, w, h)])
      .filter(([a, b]) => Math.hypot(b[0] - a[0], b[1] - a[1]) > 18);
    return { arrows, w, h };
  }

  /* a part on its own, for the parts box */
  function thumbnail(i, size, C) {
    const { lo, hi } = info[i];
    const cam = camera(lo, hi, [-40, 28], 1, 0.5);
    const r = Math.max(8, Math.hypot(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]) / 2);
    const dist = r / Math.sin(0.25) * 1.05, d = norm(sub(cam.eye, cam.at)), eye = cam.at.map((x, a) => x + d[a] * dist);
    const VP = mul(persp(0.5, 1, 1, 20000), lookAt(eye, cam.at, [0, 0, 1]));
    gl.enable(gl.SCISSOR_TEST); gl.scissor(0, 0, size, size); gl.viewport(0, 0, size, size);
    gl.clearColor(C.thumb[0] ** (1 / 2.2), C.thumb[1] ** (1 / 2.2), C.thumb[2] ** (1 / 2.2), 1);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.disable(gl.SCISSOR_TEST);
    drawParts([i], VP, eye, C, () => (kindOf[i] === "buy" ? C.buy : C.print));
  }
  function thumbInto(target, i, size, C) {
    thumbnail(i, size, C);
    target.width = size; target.height = size;
    target.getContext("2d").drawImage(canvas, 0, canvas.height - size, size, size, 0, 0, size, size);
  }

  /* ---------- the words ---------- */
  const SHANK = { M2: 4, M3: 5.5, M4: 7, M8: 12 };
  function screwSvg(sc) {
    const L = Math.min(62, 4 + sc.len * 2.6), wv = SHANK[sc.size] || 4, hw = wv * 1.9, x = 20;
    let th = "";
    for (let y = 12; y < 8 + L - 2; y += 3) th += `<rect x="${x - wv / 2 - 0.6}" y="${y}" width="${wv + 1.2}" height="1" class="screw-h" opacity="0.35"/>`;
    return `<svg viewBox="0 0 40 72" aria-hidden="true"><rect x="${x - hw / 2}" y="2" width="${hw}" height="6" rx="1.5" class="screw-h"/>
      <rect x="${x - wv / 2}" y="8" width="${wv}" height="${L}" class="screw-s"/>${th}</svg>`;
  }
  function stagesOf() {          // the chips: parts of the machine (`section` in docs/assembly.yaml)
    const out = [];
    steps.forEach((s, k) => { const last = out[out.length - 1];
      if (last && last.section === s.section) last.steps.push(k); else out.push({ section: s.section, steps: [k] }); });
    return out;
  }
  const runs = stagesOf();
  const stageName = st => `${st.slice(0, 2)} · ${(B.stages[st] || {}).title || st}`;
  const githubDir = st => B.repo.replace("/blob/", "/tree/") + "phases/" + st;

  function partsList(s) {
    return `<ul class="parts-list">${s.items.map(it => `<li><span class="q">${it.parts.length} ×</span><span>${esc(it.what)}
      <span class="id">${esc(it.id)} · ${it.kind === "buy" ? "bought" : "printed"}${it.stl ? ` · <a href="${esc(it.stl)}">STL</a>` : ""}</span></span></li>`).join("")}</ul>`;
  }
  function body(k) {
    const s = steps[k], firstOfStage = !k || steps[k - 1].stage !== s.stage, st = B.stages[s.stage] || {};
    return `${firstOfStage && st.safety ? `<p class="warn">${st.safety}</p>` : ""}
      ${printing ? partsList(s) : ""}
      <ol class="steps-text">${s.text.map(x => `<li>${x}</li>`).join("")}</ol>
      ${s.note ? `<p class="note">${s.note}</p>` : ""}
      <p class="ref">Checklist step ${esc(s.ref)} · ${esc(s.refTitle)} (<a href="${githubDir(s.stage)}">stage ${esc(stageName(s.stage))}</a>)</p>`;
  }
  function calloutHtml(s) {
    return s.items.map((it, j) => `<div class="it ${it.kind}"><canvas data-j="${j}" width="144" height="144"></canvas>
        <span><b>${it.parts.length}×</b> ${esc(it.id)}</span></div>`).join("")
      + s.screws.map(sc => `<div class="screw">${screwSvg(sc)}<span>${sc.n.length ? `<b>${sc.n.join(" / ")}×</b> ` : ""}${esc(sc.size)} × ${sc.len}</span></div>`).join("");
  }

  /* ---------- interactive page ---------- */
  let cur = 0, adj = { yaw: 0, pitch: 0 }, t0 = performance.now(), raf = 0, playing = false;
  const arrowsSvg = $("arrows");
  const chips = runs.map(run => {
    const b = document.createElement("button");
    b.type = "button";
    b.innerHTML = `<b>${esc(run.section)}</b><span>${run.steps.length > 1 ? `Steps ${run.steps[0] + 1}–${run.steps[run.steps.length - 1] + 1}` : `Step ${run.steps[0] + 1}`}</span><span class="meter"><i></i></span>`;
    b.addEventListener("click", () => go(run.steps[0]));
    $("sections").append(b);
    return b;
  });

  function wide() { return innerWidth > 720; }
  function frame(now) {
    raf = 0;
    if (!gl) return;
    const dpr = Math.min(devicePixelRatio || 1, 2), w = Math.round(canvas.clientWidth * dpr), h = Math.round(canvas.clientHeight * dpr);
    if (!w || !h) return;
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    const el = playing && !OG.reduced ? (now - t0) / 1000 : Infinity;
    if (el >= slideEnd(cur)) playing = false;
    const r = render(cur, el, adj, w, h, wide() ? 0.22 : 0);
    arrowsSvg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    arrowsSvg.style.height = canvas.clientHeight + "px";
    arrowsSvg.innerHTML = arrowPaths(r.arrows, dpr);
    if (playing && !document.hidden) raf = requestAnimationFrame(frame);   // idle once the parts land: no frames, no battery
  }
  function arrowPaths(list, dpr) {
    return list.map(([a, b]) => {
      const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, hs = 9 * dpr;
      const e = [b[0] - ux * hs * 0.4, b[1] - uy * hs * 0.4];
      const p1 = [e[0] - ux * hs - uy * hs * 0.55, e[1] - uy * hs + ux * hs * 0.55], p2 = [e[0] - ux * hs + uy * hs * 0.55, e[1] - uy * hs - ux * hs * 0.55];
      const d = `M${a[0].toFixed(1)} ${a[1].toFixed(1)}L${(e[0] - ux * hs).toFixed(1)} ${(e[1] - uy * hs).toFixed(1)}`;
      const pts = `${e.map(v => v.toFixed(1))} ${p1.map(v => v.toFixed(1))} ${p2.map(v => v.toFixed(1))}`;
      return `<path class="halo" d="${d}" vector-effect="non-scaling-stroke"/><polygon class="halo" points="${pts}"/>
        <path d="${d}" vector-effect="non-scaling-stroke"/><polygon class="head" points="${pts}"/>`;
    }).join("");
  }
  function kick() { if (!raf) raf = requestAnimationFrame(frame); }
  function thumbs() {
    if (!gl) return;
    const C = colours(), s = steps[cur];
    $("callout").querySelectorAll("canvas[data-j]").forEach(cv => thumbInto(cv, s.items[+cv.dataset.j].parts[0], 144, C));
    kick();
  }

  function show(k) {
    cur = k; adj = { yaw: 0, pitch: 0 }; $("reset").hidden = true; play();
    const s = steps[k];
    $("big-n").textContent = k + 1;
    $("big-of").textContent = `/${N}`;
    $("k-sec").textContent = `Stage ${stageName(s.stage)}`;
    $("k-step").textContent = `Step ${k + 1} of ${N}`;
    $("s-title").textContent = s.title;
    $("s-parts").innerHTML = partsList(s);
    $("s-body").innerHTML = body(k);
    $("callout").innerHTML = calloutHtml(s);
    $("back").disabled = k === 0;
    $("next").textContent = k === N - 1 ? "Done" : "Next";
    $("next").disabled = k === N - 1;
    runs.forEach((run, j) => {
      const on = run.steps.includes(k);
      chips[j].setAttribute("aria-current", String(on));
      chips[j].querySelector(".meter i").style.transform = `scaleX(${(run.steps.filter(x => x < k).length / run.steps.length).toFixed(3)})`;
      if (on) chips[j].scrollIntoView({ block: "nearest", inline: "nearest" });
    });
    if (location.hash !== `#step-${k + 1}`) history.replaceState(null, "", `#step-${k + 1}`);
    thumbs();
  }
  function play() { t0 = performance.now(); playing = true; kick(); }
  function go(k) { show(Math.max(0, Math.min(N - 1, k))); }

  function wire() {
    $("back").addEventListener("click", () => go(cur - 1));
    $("next").addEventListener("click", () => go(cur + 1));
    document.addEventListener("keydown", e => {
      if (e.target.closest && e.target.closest("input, textarea, select")) return;
      if (e.key === "ArrowRight") go(cur + 1);
      if (e.key === "ArrowLeft") go(cur - 1);
    });
    const fromHash = () => { const m = /^#step-(\d+)$/.exec(location.hash); return m ? +m[1] - 1 : 0; };
    addEventListener("hashchange", () => { const k = fromHash(); if (k !== cur) go(k); });
    let drag = null;
    /* mouse: drag turns and tilts. Touch: sideways turns; up and down still scroll the page (touch-action: pan-y) */
    canvas.addEventListener("pointerdown", e => {
      if (e.button > 0) return;
      drag = [e.clientX, e.clientY, adj.yaw, adj.pitch, e.pointerType === "touch"];
      canvas.setPointerCapture(e.pointerId);
    });
    canvas.addEventListener("pointermove", e => {
      if (!drag) return;
      adj = { yaw: drag[2] - (e.clientX - drag[0]) * 0.4, pitch: drag[4] ? drag[3] : drag[3] + (e.clientY - drag[1]) * 0.3 };
      $("reset").hidden = false; kick();
    });
    const drop = () => { drag = null; };
    ["pointerup", "pointercancel", "lostpointercapture"].forEach(t => canvas.addEventListener(t, drop));
    addEventListener("blur", drop);
    const reset = () => { adj = { yaw: 0, pitch: 0 }; $("reset").hidden = true; kick(); };
    canvas.addEventListener("dblclick", reset);
    $("reset").addEventListener("click", reset);
    $("replay").addEventListener("click", play);
    addEventListener("resize", kick);
    addEventListener("og:theme", thumbs);
    document.addEventListener("visibilitychange", kick);
    const motion = () => { $("replay").hidden = OG.reduced; kick(); };   // reduced motion: nothing to play again
    OG.onReduce(motion); motion();
    go(fromHash());
  }

  /* ---------- ?print: every step as a page (Print → Save as PDF; tools/build_book.py --pdf) ---------- */
  async function printBook() {
    document.body.classList.add("printing");
    document.documentElement.dataset.theme = "light";               // paper: light pages whatever the screen theme
    const pages = $("pages"); pages.hidden = false;
    const W = 1400, H = 900;
    canvas.width = W; canvas.height = H;
    const C = colours(), tmp = document.createElement("canvas");
    let html = `<p class="note print-hint">Print this page (Ctrl+P or ⌘P) and choose “Save as PDF” for a file: one step per landscape page.</p>`;
    steps.forEach((s, k) => {
      const r = render(k, s.stack ? 0 : Infinity, { yaw: 0, pitch: 0 }, W, H, 0);
      tmp.width = W; tmp.height = H;
      const g = tmp.getContext("2d"); g.drawImage(canvas, 0, 0);
      const cs = getComputedStyle(document.body);
      [[cs.getPropertyValue("--ground"), 7, []], [cs.getPropertyValue("--ink"), 3, [10, 10]]].forEach(([col, lw, dash]) => {
        g.strokeStyle = col; g.lineWidth = lw; g.setLineDash(dash);
        r.arrows.forEach(([a, b]) => { g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); });
      });
      g.fillStyle = cs.getPropertyValue("--ink");
      r.arrows.forEach(([a, b]) => {                                     // heads
        const L = Math.hypot(b[0] - a[0], b[1] - a[1]), ux = (b[0] - a[0]) / L, uy = (b[1] - a[1]) / L, hs = 16;
        g.beginPath(); g.moveTo(b[0], b[1]); g.lineTo(b[0] - ux * hs - uy * hs * 0.55, b[1] - uy * hs + ux * hs * 0.55);
        g.lineTo(b[0] - ux * hs + uy * hs * 0.55, b[1] - uy * hs - ux * hs * 0.55); g.closePath(); g.fill();
      });
      g.setLineDash([]);
      const pic = tmp.toDataURL("image/jpeg", 0.88);
      const items = s.items.map(it => { thumbInto(tmp, it.parts[0], 144, C);
        return `<div class="it ${it.kind}"><img src="${tmp.toDataURL()}" width="72" height="72" alt=""><span><b>${it.parts.length}×</b> ${esc(it.id)}</span></div>`; }).join("")
        + s.screws.map(sc => `<div class="screw">${screwSvg(sc)}<span>${sc.n.length ? `<b>${sc.n.join(" / ")}×</b> ` : ""}${esc(sc.size)} × ${sc.len}</span></div>`).join("");
      html += `<section class="page"><div class="pic"><img src="${pic}" alt="Step ${k + 1}: ${esc(s.title)}"><p class="big-n display num">${k + 1}</p>
          <div class="callout">${items}</div></div>
        <div class="txt"><h2>${esc(s.title)}</h2><p class="meta">Stage ${esc(stageName(s.stage))} · step ${k + 1} of ${N}</p>${body(k)}</div></section>`;
    });
    pages.innerHTML = html;
    await Promise.all([...pages.querySelectorAll("img")].map(i => i.decode().catch(() => {})));
    if (document.fonts) await document.fonts.ready;
  }

  window.__book = { ready: false, steps: () => N, go };
  (async () => {
    try { await init(); } catch (e) { gl = null; }
    if (!gl) { $("no-gl").hidden = false; canvas.hidden = true; canvas.parentElement.classList.add("nogl"); }
    if (printing && gl) await printBook(); else wire();
    window.__book.ready = true;
  })();
})();
