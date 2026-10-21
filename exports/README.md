# Exports: open and edit with other software

Generated copies; the sources stay the truth. Rebuilt by `make export` (and on GitHub after every push to the sources).

| File | Open with | Edit the source instead |
|---|---|---|
| [paper/opengonio.docx](paper/opengonio.docx) | Word, Google Docs, LibreOffice: comments, track changes | `paper/opengonio.tex` |
| [paper/opengonio-overleaf.zip](paper/opengonio-overleaf.zip) | Overleaf: *New Project → Upload Project*; pdfLaTeX, biber runs itself | copy changes back to `paper/` |
| [../paper/build/opengonio.pdf](../paper/build/opengonio.pdf) | any PDF reader | `paper/opengonio.tex` |
| [references/opengonio.ris](references/opengonio.ris) · [.json](references/opengonio.json) · [.bib](references/opengonio.bib) | Zotero, Mendeley, EndNote (RIS); Zotero, pandoc (CSL-JSON); JabRef, any LaTeX (BibTeX) | `REFERENCES.md` |
| [bom/opengonio-bom.xlsx](bom/opengonio-bom.xlsx) | Excel, Google Sheets, LibreOffice Calc: pictures, buy and STEP/STL links, live totals vs. the cap | `PARTS.md` (decisions), `phases/*/bom.csv` |
| [bom/opengonio-bom.csv](bom/opengonio-bom.csv) | any spreadsheet or script | same |
| [wiki/opengonio-wiki.pdf](wiki/opengonio-wiki.pdf) · [.docx](wiki/opengonio-wiki.docx) | PDF reader; Word, Google Docs | `wiki/src/*.md` |
| [cad/opengonio_assembly.glb](cad/opengonio_assembly.glb) | Blender (*File → Import → glTF*), Windows 3D Viewer, three.js, online glTF viewers; parts named by BOM ID, metres | `tools/cad/*.py` |

CAD masters: STEP (Onshape, FreeCAD, Fusion 360, SolidWorks; PrusaSlicer, OrcaSlicer and Bambu Studio also import STEP) in `cad/` and `phases/*/3d/`; STL for every slicer.
