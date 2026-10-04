# Licensing and OSHWA

| Part | Licence |
|---|---|
| Hardware (Onshape, STEP, 3MF, BOM, drawings) | CERN-OHL-S-2.0 |
| Software, firmware config, tools | GPL-3.0-or-later |
| Docs, figures, data | CC BY-SA 4.0 |

Texts in `LICENSES/` (from SPDX [R71]). **GPL vs MIT:** GPL keeps improved versions open (matches CERN-OHL-S); MIT allows closed reuse. Chosen: GPL.
Vendor CAD is linked from the BOM, never committed.

## OSHWA certification checklist [R72]

- [ ] Repo + Onshape document public
- [ ] Licences in `LICENSES/`, SPDX headers on files
- [ ] STEP + 3MF for every custom part; BOM CSV
- [ ] 8-section README for every module
- [ ] No vendor CAD redistributed; no third-party trademarks in the product name
- [ ] Apply at certification.oshwa.org, add UID to README and base engraving
