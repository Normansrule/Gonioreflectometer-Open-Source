/* OpenGonio shared runtime: theme, design tokens for canvas/WebGL, motion helpers. Shared by the website (docs/) and
   the control app (copied by `make build`). Load it in <head> without defer so the theme is set before first paint.
   SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  const root = document.documentElement;
  root.classList.add("js");
  const KEY = "opengonio-theme";
  const read = () => { try { return localStorage.getItem(KEY); } catch (e) { return null; } };
  const write = v => { try { localStorage.setItem(KEY, v); } catch (e) { /* private window: theme lasts this visit */ } };
  const saved = read();
  if (saved === "light" || saved === "dark") root.dataset.theme = saved;

  const mqLight = window.matchMedia("(prefers-color-scheme: light)");
  const mqReduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const current = () => root.dataset.theme || (mqLight.matches ? "light" : "dark");

  const cache = {};
  function tokens() {
    const cs = getComputedStyle(root), v = n => cs.getPropertyValue(n).trim();
    return Object.assign(cache, {
      ground: v("--ground"), g2: v("--ground-2"), g3: v("--ground-3"), g4: v("--ground-4"),
      ink: v("--ink"), ink2: v("--ink-2"), ink3: v("--ink-3"), rule: v("--rule"),
      light: v("--light"), lightText: v("--light-text"), lightInk: v("--light-ink"),
      red: v("--patch-red"), green: v("--patch-green"), blue: v("--patch-blue"), grey: v("--patch-grey"),
      text: v("--font-text"), display: v("--font-display"), theme: current(),
    });
  }
  function alpha(hex, a) {
    const h = hex.replace("#", ""), n = parseInt(h.length === 3 ? h.replace(/./g, "$&$&") : h, 16);
    return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`;
  }
  function rgb(hex) { const n = parseInt(hex.replace("#", ""), 16); return [(n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255]; }
  const changed = () => { tokens(); window.dispatchEvent(new CustomEvent("og:theme", { detail: current() })); };
  function setTheme(t) { root.dataset.theme = t; write(t); syncButtons(); changed(); }
  function syncButtons() {
    document.querySelectorAll("[data-theme-toggle]").forEach(b => {
      const dark = current() === "dark";
      b.setAttribute("aria-pressed", String(!dark));
      b.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
      const label = b.querySelector("[data-theme-label]"); if (label) label.textContent = dark ? "Light" : "Dark";
    });
  }
  mqLight.addEventListener("change", () => { if (!root.dataset.theme) { syncButtons(); changed(); } });

  /* critically damped spring toward a target: the lamp and anything that follows the pointer */
  function spring(x0, stiffness = 120, damping = 22) {
    const s = { x: x0, v: 0, target: x0, step(dt) {
      const f = stiffness * (s.target - s.x) - damping * s.v; s.v += f * dt; s.x += s.v * dt;
      return Math.abs(s.target - s.x) > 1e-4 || Math.abs(s.v) > 1e-4; } };
    return s;
  }

  document.addEventListener("DOMContentLoaded", () => {
    tokens(); syncButtons();
    document.querySelectorAll("[data-theme-toggle]").forEach(b =>
      b.addEventListener("click", () => setTheme(current() === "dark" ? "light" : "dark")));
  });

  window.OG = { tokens, alpha, rgb, theme: current, setTheme, spring,
    get reduced() { return mqReduce.matches; }, onReduce: f => mqReduce.addEventListener("change", f) };
})();
