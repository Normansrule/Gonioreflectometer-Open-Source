# OpenGonio framework commands. Run `make help`.
# SPDX-License-Identifier: GPL-3.0-or-later
PY := $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)
m ?= update

.PHONY: help setup build check test parts publish all sim release done next

help:            ## list commands
	@grep -E '^[a-z]+:.*## ' Makefile | sed 's/:.*## /\t/'

setup:           ## once: .venv with the software, tests and tools
	python3 -m venv .venv
	.venv/bin/pip install -q -e "./software[dev]" pyyaml numpy
	@echo "done. optional for 3D parts: .venv/bin/pip install cadquery numpy-stl matplotlib"

build:           ## regenerate checklists, README tables, figures, budgets, 3D index (+ apply PARTS.md decisions)
	$(PY) tools/part_images.py > /dev/null
	$(PY) tools/parts_doc.py
	$(PY) tools/roadmap.py
	$(PY) tools/export_machine.py > /dev/null
	$(PY) tools/bom_check.py
	$(PY) tools/power_budget.py > /dev/null
	$(PY) tools/optics.py > /dev/null
	$(PY) tools/make_assets.py > /dev/null
	$(PY) tools/cad/placement_template.py > /dev/null
	$(PY) tools/cad/index.py

parts:           ## regenerate every printed part (STEP + STL) and the parts picture (needs cadquery)
	$(PY) tools/cad/parts.py
	$(PY) tools/cad/index.py
	$(PY) tools/cad/gallery.py
	$(PY) tools/part_images.py --stl

check:           ## milestones, parts lists, budget, references, links, machine config
	$(PY) tools/check.py

test:            ## software tests
	$(PY) -m pytest -q software

all: build check test   ## everything before a commit

sim:             ## simulated machine: capture -> verify -> calibrate -> curve, ends with ALL PASS
	$(PY) -m opengonio.cli sim-demo --out data/sim

release:         ## after a stage passes:  make release s=06  (tag v0.6 + 3D files zip on GitHub)
	bash scripts/release.sh "$(s)"

publish: all     ## commit + push + sync GitHub milestones/issues:  make publish m="what changed"
	bash scripts/update.sh "$(m)"

done:            ## a step passed its Verify:  make done id=M05.1  (closes the issue, ticks it everywhere, publishes)
	$(PY) tools/roadmap.py --close "$(id)"
	bash scripts/update.sh "$(id) done"

next:            ## print the next step to do
	@$(PY) -c "import sys; sys.path.insert(0,'tools'); import roadmap, roadmap_svg; st, ms = roadmap.load(); n = roadmap_svg.next_step(ms, roadmap.done_steps()); print(f'{n[1][\"id\"]} {n[1][\"title\"]} ({n[1].get(\"time\",\"\")}) -> phases/{n[0][\"stage\"]}/README.md' if n else 'all done')"
