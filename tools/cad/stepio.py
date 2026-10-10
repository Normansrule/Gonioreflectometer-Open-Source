"""STEP files without a time stamp, so regenerating an unchanged part leaves git clean.
SPDX-License-Identifier: CERN-OHL-S-2.0
"""
from __future__ import annotations

import re
from pathlib import Path

_STAMP = re.compile(r"(FILE_NAME\('[^']*',)'[^']*'")


def stabilise(path: str | Path) -> None:
    """Replace the export time in the STEP header with a fixed one."""
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="surrogateescape")
    new = _STAMP.sub(r"\1'2026-01-01T00:00:00'", text, count=1)
    if new != text:
        p.write_text(new, encoding="utf-8", errors="surrogateescape")
