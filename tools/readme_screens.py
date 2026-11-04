#!/usr/bin/env python3
"""docs/assets/screens/: README screenshots of the website and the control app, and two looping animations
(hero.webp: the lamp going round the samples; rig.webp: the four axes in turn).

    python tools/readme_screens.py [--animations]   (needs playwright + Chromium; starts its own servers; nothing is published)

The app runs on the simulated machine only. Run by hand after a visual change; the images are committed.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import functools
import http.server
import io
import math
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "screens"
ARGS = ["--no-sandbox", "--enable-unsafe-swiftshader", "--use-angle=swiftshader"]


def serve_docs() -> str:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT / "docs")))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}"


def jpg(png: bytes, name: str, width: int | None = None) -> None:
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGB")
    if width and im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(OUT / name, quality=86, optimize=True, progressive=True)
    print(f"docs/assets/screens/{name} {im.width}x{im.height}")


def webp(frames, name: str, ms: int) -> None:
    frames[0].save(OUT / name, save_all=True, append_images=frames[1:], duration=ms, loop=0, quality=72, method=6)
    print(f"docs/assets/screens/{name} {frames[0].width}x{frames[0].height}, {len(frames)} frames, "
          f"{(OUT / name).stat().st_size / 1e6:.2f} MB")


def animations(p, base: str) -> None:
    """README: the hero with its lamp going round (hero.webp) and the four axes in turn (rig.webp), both looping."""
    from PIL import Image
    # reduced motion: the page stops animating by itself, so every frame is one we set (and the software renderer keeps up)
    pg = p.new_page(viewport={"width": 1440, "height": 900}, color_scheme="dark", device_scale_factor=1, reduced_motion="reduce")
    pg.set_default_timeout(120000)
    pg.goto(f"{base}/index.html", wait_until="networkidle"); pg.wait_for_timeout(1200)
    frames = []
    for i in range(48):
        t = 2 * math.pi * i / 48
        pg.evaluate(f"__hero.set({50 - 16 * math.cos(t):.3f}, {90 + 80 * math.sin(t):.3f})"); pg.wait_for_timeout(40)
        frames.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB").resize((960, 600), Image.LANCZOS))
    webp(frames, "hero.webp", 110)
    # the story section: scroll position -> build-up, each axis, the camera; pinned, so one viewport shows it all.
    # Motion allowed here (with reduced motion the story is a still list), and the page draws nothing else meanwhile.
    pg.close()
    pg = p.new_page(viewport={"width": 1440, "height": 900}, color_scheme="dark", device_scale_factor=1)
    pg.set_default_timeout(120000)
    pg.goto(f"{base}/index.html", wait_until="networkidle"); pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('.rail').style.display = 'none'; const s = document.getElementById('machine');"
                "scrollTo(0, s.getBoundingClientRect().top + scrollY + 10)")
    for _ in range(150):
        if pg.evaluate("window.__story && __story.ready()"):
            break
        pg.wait_for_timeout(100)
    frames = []
    n = 120
    for i in range(n):
        q = i / (n - 1) * 0.985
        pg.evaluate(f"__story.at({q:.4f})"); pg.wait_for_timeout(70)
        im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
        frames.append(im.resize((960, 600), Image.LANCZOS))
    frames += [frames[-1]] * 10                                   # rest on the last chapter before looping
    webp(frames, "rig.webp", 70)
    pg.close()


def site(p, base: str) -> None:
    for theme in ("dark", "light"):
        pg = p.new_page(viewport={"width": 1440, "height": 900}, color_scheme=theme, device_scale_factor=1)
        pg.goto(f"{base}/index.html", wait_until="networkidle"); pg.wait_for_timeout(1500)
        if theme == "light":
            jpg(pg.screenshot(), "site-hero-light.jpg")   # the dark hero is in hero.webp
        if theme == "dark":
            for sel, name in (("#results", "site-results.jpg"), ("#build", "site-build.jpg")):
                pg.evaluate(f"document.querySelector('{sel}').scrollIntoView()"); pg.wait_for_timeout(1400)
                jpg(pg.screenshot(), name)
        pg.close()
    pg = p.new_page(viewport={"width": 390, "height": 844}, color_scheme="dark", device_scale_factor=2)
    pg.goto(f"{base}/index.html", wait_until="networkidle"); pg.wait_for_timeout(1500)
    jpg(pg.screenshot(), "site-phone.jpg", width=390 * 2)
    pg.close()
    pg = p.new_page(viewport={"width": 1440, "height": 900}, color_scheme="dark")
    pg.goto(f"{base}/lab.html", wait_until="networkidle"); pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('#machine').scrollIntoView()"); pg.wait_for_timeout(1400)
    jpg(pg.screenshot(), "lab.jpg")
    pg.close()
    for page, frag, name in (("build.html", "#step-11", "build-book.jpg"), ("wiring.html", "#step-6", "wiring-guide.jpg")):
        pg = p.new_page(viewport={"width": 1440, "height": 900}, color_scheme="dark")      # the two guides, part landed
        pg.goto(f"{base}/{page}{frag}", wait_until="networkidle"); pg.wait_for_timeout(2500)
        pg.evaluate("document.querySelector('.stage').scrollIntoView({block: 'start'}); scrollBy(0, -170)"); pg.wait_for_timeout(600)
        jpg(pg.screenshot(), name)
        pg.close()


def app(p) -> None:
    with tempfile.TemporaryDirectory() as data:
        port = 8797
        proc = subprocess.Popen([sys.executable, "-m", "opengonio.cli", "app", "--sim", "mirror", "--no-browser",
                                 "--port", str(port), "--data", data], cwd=ROOT / "software",
                                env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "software" / "src")})
        try:
            base = f"http://127.0.0.1:{port}"
            for _ in range(50):
                try:
                    __import__("urllib.request").request.urlopen(base + "/api/state", timeout=1)
                    break
                except OSError:
                    time.sleep(0.1)
            for theme, w, h, name in (("dark", 1440, 900, "app-dark.jpg"), ("light", 1440, 900, "app-light.jpg"),
                                      ("dark", 390, 844, "app-phone.jpg")):
                pg = p.new_page(viewport={"width": w, "height": h}, color_scheme=theme, device_scale_factor=2 if w < 500 else 1)
                pg.goto(base + "/"); pg.wait_for_timeout(700)
                if name == "app-dark.jpg":
                    pg.click("#home"); pg.wait_for_timeout(600)
                    pg.click('[data-light="white"]'); pg.wait_for_timeout(300)
                    pg.click("#move"); pg.wait_for_timeout(500)
                    pg.click("#run"); pg.wait_for_timeout(2500)
                    pg.click('[data-light="white"]'); pg.wait_for_timeout(300)
                    pg.fill("#n-M4", "120"); pg.dispatch_event("#n-M4", "change"); pg.click("#specular"); pg.wait_for_timeout(300)
                    pg.click("#move"); pg.wait_for_timeout(1200); pg.click("#grab"); pg.wait_for_timeout(500)
                    pg.click("#spec-read"); pg.wait_for_timeout(500)
                    pg.evaluate("window.scrollTo(0, 0)"); pg.wait_for_timeout(400)   # the clicks scrolled the console
                jpg(pg.screenshot(), name, width=w * (2 if w < 500 else 1))
                pg.close()
            pg = p.new_page(viewport={"width": 1440, "height": 900}, color_scheme="dark")
            pg.goto(base + "/"); pg.wait_for_timeout(500)
            pg.evaluate("fetch('/api/disconnect', {method: 'POST'})"); pg.reload(); pg.wait_for_timeout(700)
            jpg(pg.screenshot(), "app-connect.jpg")
            pg.close()
        finally:
            proc.terminate()


def main() -> int:
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        base = serve_docs()
        animations(b, base)
        if "--animations" not in sys.argv:
            site(b, base)
        if "--animations" not in sys.argv:
            app(b)
        b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
