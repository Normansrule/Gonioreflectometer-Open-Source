#!/usr/bin/env bash
# Build the opengonio wheel and use it the way a user would: a fresh venv outside the repo, no source tree.
# Fails if the installed package can't find its machine.yaml, `opengonio init` misbehaves, or sim-demo is not ALL PASS.
#   bash scripts/wheel_check.sh          (CI job "wheel"; also run by make ci)
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
export PIP_DISABLE_PIP_VERSION_CHECK=1
cd "$(git rev-parse --show-toplevel)"
PYBIN=$(command -v python3.12 || command -v python3)
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
"$PYBIN" -m venv "$T/build" && "$T/build/bin/pip" install -q build
"$T/build/bin/python" -m build -q --wheel -o "$T/dist" software > /dev/null 2>&1 || { echo "FAIL wheel build"; exit 1; }
"$PYBIN" -m venv "$T/venv" && "$T/venv/bin/pip" install -q "$T"/dist/*.whl
cd "$T"                                                   # away from the checkout: nothing repo-relative may be used
export HOME="$T/home" OPENGONIO_HOME="$T/home/.config/opengonio"
want=$(sed -n 's/^__version__ = "\(.*\)".*/\1/p' "$OLDPWD/software/src/opengonio/__init__.py")
got=$("$T/venv/bin/pip" show opengonio | sed -n 's/^Version: //p')
[ "$got" = "$want" ] || { echo "FAIL wheel version $got != __version__ $want"; exit 1; }
"$T/venv/bin/opengonio" check-pose M4=60 M3=30 > /dev/null
"$T/venv/bin/opengonio" init > /dev/null
if "$T/venv/bin/opengonio" init > /dev/null; then echo "FAIL init overwrote an existing machine.yaml"; exit 1; fi
cmp -s "$OPENGONIO_HOME/machine.yaml" "$OLDPWD/software/config/machine.yaml" || { echo "FAIL packaged machine.yaml is stale: run make build"; exit 1; }
"$T/venv/bin/opengonio" sim-demo --out "$T/sim" > "$T/sim.json" || true
grep -q '"result": "ALL PASS"' "$T/sim.json" || { echo "FAIL sim-demo from the wheel"; tail -5 "$T/sim.json"; exit 1; }
echo "PASS wheel $got: installs, finds its config, init, sim-demo ALL PASS"
