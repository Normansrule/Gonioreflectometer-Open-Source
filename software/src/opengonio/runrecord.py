"""Run folders and manifest.json: one schema for laptop capture, the standalone station and the scanner.

A run folder is created exclusively (never reused by accident), its manifest is written first with
status "running" and rewritten atomically after every shot, so a crash leaves a readable partial run.

    status   running -> finished | aborted | error        (only "finished" can verify as complete)
    planned  number of shots the plan asked for            (verify compares it with the shots recorded)
    shots    {"i", "pose" (requested, true angles), "reported_pose" (controller), "file", "sha256", "bytes",
              "shape", "exposure_ms", "spectral"}
    errors   what stopped the run;  cleanup_errors  what failed while making the machine safe afterwards
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import time
import uuid
from pathlib import Path

from . import __version__

SCHEMA = 2        # 1: no run_id / planned / status / file hashes (still readable, verified as "legacy")
STATUSES = ("running", "finished", "aborted", "error")


class RunExistsError(FileExistsError):
    pass


class AcquisitionError(RuntimeError):
    pass


def new_run_id() -> str:
    return uuid.uuid4().hex


def stamp(t: float | None = None) -> str:
    return time.strftime("%Y%m%d-%H%M%S", time.localtime(t if t is not None else time.time()))


def make_run_dir(path: str | Path, overwrite: bool = False) -> Path:
    """Create `path` for a new run. An existing run there is refused unless overwrite=True, which moves it aside
    to `<path>.replaced-<time>` (nothing is deleted)."""
    p = Path(path).expanduser()
    if p.exists() and any(p.iterdir()):
        if not overwrite:
            raise RunExistsError(f"{p} already holds a run: choose another --out, or --overwrite (moves the old one aside)")
        aside = p.with_name(f"{p.name}.replaced-{stamp()}-{new_run_id()[:6]}")
        p.rename(aside)
    p.mkdir(parents=True, exist_ok=True)
    try:                                                   # claim it: a second process gets RunExistsError
        (p / ".run").open("x").close()
    except FileExistsError:
        raise RunExistsError(f"{p} is being written by another run") from None
    return p


def unique_child(parent: str | Path, name: str, t: float | None = None) -> Path:
    """New folder parent/<time>-<name>-<id6>: two runs started in the same second still get different folders."""
    parent = Path(parent).expanduser()
    parent.mkdir(parents=True, exist_ok=True)
    while True:
        p = parent / f"{stamp(t)}-{name.replace(' ', '_')}-{new_run_id()[:6]}"
        try:
            p.mkdir()
            return p
        except FileExistsError:
            continue


def write_json_atomic(path: Path, data: dict) -> None:
    """Write via a temporary file + rename: a reader never sees half a manifest."""
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, path)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def config_hash(cfg) -> str:
    """Fingerprint of the machine description used for a run (geometry, axes, lights, camera)."""
    from dataclasses import asdict
    d = asdict(cfg)
    return hashlib.sha256(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()[:16]


def new_manifest(cfg, name: str, light: str | None, cal=None, exposure_ms: float | None = None,
                 run_stamp: str | None = None, planned: int | None = None, kind: str = "measurement") -> dict:
    """manifest.json header: everything needed to re-process the run later on another computer."""
    return {"schema": SCHEMA, "run_id": new_run_id(), "kind": kind, "job": name, "started": run_stamp or stamp(),
            "software": f"opengonio {__version__}", "machine": cfg.name, "machine_config": config_hash(cfg),
            "installed_phase": cfg.installed_phase, "light": light, "exposure_ms": exposure_ms,
            "units": {"angles": "deg, true (after calibration offsets)", "image": "8-bit counts, signal plane = mean(R,G,B)",
                      "spectral": "AS7341 raw counts"},
            "calibration": cal.snapshot() if cal is not None else None,
            "planned": planned, "status": "running", "finished": False, "errors": [], "cleanup_errors": [],
            "reference": None, "shots": []}


def record_file(run_dir: Path, name: str, img=None) -> dict:
    """Describe a saved frame: size, hash and (if given) the array shape. Raises if the file is missing or empty."""
    f = run_dir / name
    if not f.exists() or f.stat().st_size == 0:
        raise AcquisitionError(f"image not written: {name}")
    out = {"file": name, "bytes": f.stat().st_size, "sha256": sha256_file(f)}
    if img is not None and hasattr(img, "shape"):
        out["shape"] = list(img.shape)
    return out


def save_frame(save, run_dir: Path, name: str, img) -> dict:
    """Call the save callback, treat False/exception/missing file as a failed acquisition, return the file record."""
    try:
        ok = save(run_dir / name, img)
    except Exception as exc:                                   # disk full, permission, codec ...
        raise AcquisitionError(f"saving {name} failed: {exc}") from exc
    if ok is False:
        raise AcquisitionError(f"saving {name} failed (writer returned False)")
    return record_file(run_dir, name, img)


def finish(man: dict, status: str, error: BaseException | str | None = None) -> None:
    assert status in STATUSES
    man["status"] = status
    man["finished"] = status == "finished"
    man["ended"] = dt.datetime.now().isoformat(timespec="seconds")
    if error is not None:
        man["errors"].append(f"{type(error).__name__}: {error}" if isinstance(error, BaseException) else str(error))
