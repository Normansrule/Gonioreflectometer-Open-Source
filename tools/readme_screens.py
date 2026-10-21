#!/usr/bin/env python3
"""docs/assets/screens/: README screenshots of the website and the control app, plus the hero lamp as a GIF.

    python tools/readme_screens.py      (needs playwright + Chromium; starts its own servers; nothing is published)

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


def site(p, base: str) -> None:
    for theme in ("dark", "light"):
        pg = p.new_page(viewport={"width": 1440, "height": 900}, color_scheme=theme, device_scale_factor=1)
        pg.goto(f"{base}/index.html", wait_until="networkidle"); pg.wait_for_timeout(1500)
        jpg(pg.screenshot(), f"site-hero-{theme}.jpg")
        if theme == "dark":
            for sel, name in (("#results", "site-results.jpg"), ("#build", "site-build.jpg")):
                pg.evaluate(f"document.querySelector('{sel}').scrollIntoView()"); pg.wait_for_timeout(1400)
                jpg(pg.screenshot(), name)
            # the lamp following a pointer, as a GIF
            from PIL import Image
            box = pg.evaluate("(() => { scrollTo(0, 0); const r = document.getElementById('stage').getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })()")
            pg.wait_for_timeout(400)
            frames = []
            for i in range(36):
                t = i / 36 * 2 * math.pi
                x = box[0] + box[2] * (0.5 + 0.38 * math.sin(t)); y = box[1] + box[3] * (0.27 + 0.32 * (1 - math.cos(t)) / 2)
                pg.mouse.move(x, y); pg.wait_for_timeout(90)
                shot = pg.screenshot(clip={"x": box[0], "y": box[1] + box[3] * 0.06, "width": box[2], "height": box[3] * 0.72})
                im = Image.open(io.BytesIO(shot)).convert("RGB")
                frames.append(im.resize((560, round(im.height * 560 / im.width)), Image.LANCZOS))
            pal = [f.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
            pal[0].save(OUT / "site-lamp.gif", save_all=True, append_images=pal[1:], duration=90, loop=0, optimize=True)
            print(f"docs/assets/screens/site-lamp.gif {frames[0].width}x{frames[0].height}, {len(frames)} frames")
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
        site(b, serve_docs())
        app(b)
        b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
