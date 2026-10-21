---
version: 1
slug: "software-src-opengonio-app-static-index-html"
primary_target: "software/src/opengonio/app/static/index.html"
related_targets: []
---

# Surface brief: OpenGonio control app (software/src/opengonio/app/static/index.html)

Scope: the stage-14 laptop app, Operate mode. Served by `opengonio app` in the browser and in a desktop window around the same page. Runs on the simulated machine (`--sim MATERIAL`) or on the real SKR Pico + camera (untested on hardware: say so).
Users: the builder at the machine, in a dim room next to the dark box, for sessions of minutes to an hour. Jobs, most frequent first: see where the light and sample are; jog/home axes; switch the lamp; run a plan (mirror sweep, in-plane, isotropic) and watch it; read the curve; stop at once.
Question the screen answers first: "Where is the light, where is the sample, and what does the camera see right now?"
States: not connected, connecting, homing, idle, moving, running a plan, finished, alarm/error, blocked colour bank.

## Direction contract

THESIS: The instrument as an exhibit in a dark room: the live pose diagram (lamp arc, tilted sample, fixed camera, θi/θr) is the lit object; controls sit beside it like a catalogue label. Refuses the dashboard template (KPI tiles, sidebar pill nav, gradient charts).
OWN-WORLD: Same velvet ground, bone ink, tungsten light as the only accent (the lamp in the diagram, the lamp switch when on, the primary action). Scale-bar patches carry status: green ready, red stop/error, blue simulated. Gloock only for the product name and the screen's one figure; Hanken Grotesk for everything else, tabular figures for angles.
STORY: Connect (or start the simulator) → home → jog and light → run a plan → read the curve → open the run folder.
FIRST VIEWPORT: Top bar (mark, name, machine scope, theme, always-visible Stop). Left 8 columns: pose diagram at full height with the angles as text; under it the camera frame and its counts. Right 4 columns: axes with values and jog, Home all, lamp. Run panel and results below the fold on desktop only after the first rows show.
FORM: Operate expression of the raking-light world. seed:d6f72d94f29f2eb3
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
