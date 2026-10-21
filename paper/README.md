# Paper

Manuscript for **HardwareX** (Elsevier, open-source scientific hardware). PDF: [build/opengonio.pdf](build/opengonio.pdf).

| File | What |
|---|---|
| `opengonio.tex` | manuscript (HardwareX hardware-article sections, `elsarticle` class) |
| `references.bib` | generated from [REFERENCES.md](../REFERENCES.md) by `tools/refs_bib.py`; keys = reference IDs (`\parencite{R1}`) |
| `apa.csl` | APA 7th edition style for the wiki bibliography (CSL project, CC BY-SA 3.0) |
| `generated/` | specifications, design-files and bill-of-materials tables from the repo (`tools/paper_assets.py`) |
| `figures/` | assembly render and diagrams (`make cad`) |
| `build/` | output; only the PDF is committed |

**Build:** `make paper` (or `make all`). Needs `latexmk`, `biber`, `texlive-publishers`, `texlive-bibtex-extra`, `texlive-latex-extra`.

**Citations:** APA 7 (`biblatex-apa`). HardwareX uses numbered references; to switch, change `style=apa` to `style=numeric` before submission.

**Before submission:** check sections against the current HardwareX guide for authors; fill every red `[TBD]` (results after stages 06–09); archive the repo (Zenodo DOI) and replace the repository URL.
