#!/usr/bin/env python3
"""docs/og/img/*.png: the website's pictures, made from the project's own tools (no stock images, no photographs).

    python tools/site_pictures.py            simulator frames + specimen render (needs playwright + Chromium)
    python tools/site_pictures.py --cad      also the CAD assembly in raking light (needs cadquery, matplotlib)

Run by hand after the lab page, the CAD or the specimen shader change; the PNGs are committed. Everything here is
a render or a simulation, and the page captions say so.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import base64
import functools
import http.server
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
IMG = DOCS / "og" / "img"
GROUND = (12, 11, 10)            # --ground (dark): pictures keep the dark room in both themes

# lab simulator poses: (file, build stage, phase, M4, M3, M2, M1, view)
MOMENTS = [
    ("moment-lamp", 17, 6, 150, 0, 0, 0, {"yaw": -70, "pitch": 30, "zoom": 1.15}),
    ("moment-table", 17, 6, 80, 40, 0, 0, {"yaw": -100, "pitch": 26, "zoom": 1.3}),
    ("moment-tilt", 17, 8, 100, 30, 35, 0, {"yaw": -40, "pitch": 20, "zoom": 1.5}),
    ("moment-spin", 17, 9, 100, 30, 20, 60, {"yaw": -60, "pitch": 46, "zoom": 1.5}),
    ("moment-camera", 17, 6, 60, 30, 0, 0, {"yaw": -90, "pitch": 70, "zoom": 1.0}),
]


def serve() -> str:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Quiet, directory=str(DOCS))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}"


def save(data_url: str, name: str, ground: bool = True) -> None:
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(base64.b64decode(data_url.split(",", 1)[1]))).convert("RGBA")
    if ground:
        bg = Image.new("RGBA", im.size, GROUND + (255,))
        im = Image.alpha_composite(bg, im)
    im.convert("RGB").save(IMG / f"{name}.png", optimize=True)
    print(f"docs/og/img/{name}.png {im.size[0]}x{im.size[1]}")


def browser() -> None:
    from playwright.sync_api import sync_playwright
    base = serve()
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-angle=swiftshader"])
        pg = b.new_page(viewport={"width": 1800, "height": 1300}, color_scheme="dark", reduced_motion="reduce")
        pg.goto(f"{base}/lab.html", wait_until="networkidle")
        pose = """([build, phase, m4, m3, m2, m1, v]) => {
            const set = (id, x) => { const el = document.getElementById(id); el.value = x; el.dispatchEvent(new Event('input')); };
            set('build', build); setPhase(phase); set('m4', m4); set('m3', m3); set('m2', m2); set('m1', m1);
            view = Object.assign({yaw: -70, pitch: 24, zoom: 1}, v); draw();
            return document.getElementById('sim').toDataURL('image/png'); }"""
        for name, *args in MOMENTS:
            save(pg.evaluate(pose, args), name)
        save(pg.evaluate("() => { const set = (id, x) => { const el = document.getElementById(id); el.value = x; el.dispatchEvent(new Event('input')); };"
                         "set('bti', 40); set('brg', 0.32); set('bbc', 0.35); set('bmt', 0);"
                         "return document.getElementById('lobe').toDataURL('image/png'); }"), "moment-lobe")
        for st in range(1, 18):
            save(pg.evaluate(pose, [st, 9 if st >= 9 else 8 if st >= 8 else 6, 110, 35, 20 if st >= 8 else 0, 30 if st >= 9 else 0,
                                    {"yaw": -64, "pitch": 28, "zoom": 1.05}]), f"stage-{st:02d}")
        pg.goto(f"{base}/index.html", wait_until="networkidle")
        url = pg.evaluate("""() => { const c = document.createElement('canvas'); c.style.cssText = 'position:fixed;left:0;top:0;width:1600px;height:1200px';
            document.body.appendChild(c); Object.defineProperty(window, 'devicePixelRatio', {value: 1});
            const s = Specimen.make(c, {keep: true}); s.draw(36, 92); return c.toDataURL('image/png'); }""")
        save(url, "specimen", ground=False)
        b.close()


def cad() -> None:
    """The assembly from tools/cad/assembly.py, shaded with one low warm lamp on the dark ground."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    sys.path.insert(0, str(ROOT / "tools"))
    sys.path.insert(0, str(ROOT / "tools" / "cad"))
    import assembly as A
    from paper_assets import subdivide
    tris, cols = [], []
    for shape, _, loc, col in A.build():
        if shape is None:
            continue
        s = shape.moved(loc) if loc else shape
        v, f = s.tessellate(0.6, 0.3)
        v = np.array([[q.x, q.y, q.z] for q in v])
        c = col.toTuple()[:3] if col else (0.6, 0.6, 0.6)
        for t in f:
            tris.append(v[list(t)])
            cols.append(c)
    tris, cols = subdivide(np.array(tris), np.array(cols), 22.0)
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= np.linalg.norm(n, axis=1)[:, None] + 1e-9
    lamp = np.array([-0.62, -0.55, 0.36]); lamp /= np.linalg.norm(lamp)        # low, from the front left: raking light
    view = np.array([0.53, -0.85, 0.42]); view /= np.linalg.norm(view)
    nd = np.abs(n @ lamp)
    h = lamp + view; h /= np.linalg.norm(h)
    spec = np.abs(n @ h) ** 60
    warm = np.array([1.0, 0.80, 0.55])
    base = np.array(cols)
    fc = 0.035 + base * warm * (0.12 + 1.05 * nd[:, None]) + 0.35 * spec[:, None] * warm
    fc = np.clip(fc, 0, 1) ** (1 / 1.15)
    bg = tuple(x / 255 for x in (12, 11, 10))
    fig = plt.figure(figsize=(10, 5.5), facecolor=bg)
    ax = fig.add_subplot(projection="3d", facecolor=bg)
    ax.add_collection3d(Poly3DCollection(tris, facecolors=fc, edgecolors="none"))
    mn, mx = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
    ax.set_xlim(mn[0], mx[0]); ax.set_ylim(mn[1], mx[1]); ax.set_zlim(mn[2], mx[2])
    ax.set_box_aspect(tuple(mx - mn), zoom=1.15); ax.view_init(22, -58); ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    out = IMG / "assembly.png"
    fig.savefig(out, dpi=380, facecolor=bg)
    plt.close(fig)
    from PIL import Image, ImageChops
    im = Image.open(out).convert("RGB")
    box = ImageChops.difference(im, Image.new("RGB", im.size, (12, 11, 10))).point(lambda x: 255 if x > 6 else 0).getbbox()
    if box:
        pad = 40
        im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width), min(box[3] + pad, im.height)))
    im.save(out, optimize=True)
    print(f"docs/og/img/assembly.png {im.size[0]}x{im.size[1]}")


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    if "--cad" in sys.argv:
        cad()
    if "--cad-only" not in sys.argv:
        browser()
    return 0


if __name__ == "__main__":
    sys.exit(main())
