# Decision Log

Status: living document

One entry per decision that changes scope, cost, program, or a previously approved item. Use `templates/decision-record.md`. Newest first. Never edit a closed decision; supersede it with a new one that references it.

| ID | Date | Decision | Phase | Supersedes | Record |
|---|---|---|---|---|---|
| D-001 | | | | | link to section below |

---

(decision records follow)

---

## Session notes

One paragraph per working session, newest first: date, what changed, what was in progress when the session ended. Required by `AGENTS.md`.

**2026-10-24 — Session 3 (proof of concept, continued).** Owner asked for two more example renders showing different things, prompts for external generators, and a one-page portfolio site with a fly-around consistent with the stills. `proof-of-concept/generators/make_render.py` now holds a view table and a season table and renders any of R-01 (viewpoint unchanged), R-02 (eye level from the vines across the patio, May morning) and R-03 (oblique aerial from the south-west, January dusk, interiors lit); in scene mode it exports the same geometry and tables to `proof-of-concept/scene.js`. `proof-of-concept/portfolio.html` loads that file into a Three.js model with the three stills' cameras as presets, a season toggle, orbit, fly and pan, and shows the stills and the plan sheet below. `render-prompts.md` carries the image-to-image prompts and `generators/stamp_caption.py` stamps externally generated outputs. While placing an arrival camera, found that the example plan's east end collides (porch over W.01 and the arrival court); fixed in the same session on the owner's instruction: the porch is now x 76–86 × y 24–40 between the lobby face and W.01, open to a drop-off court at x 72–86 × y 40–50, reached by a one-way lane from the east at y 38–42 between W.01 and the winery hall, whose outline moved to x 86–100; the render script, `scene.js` and the page carry the same geometry. Nothing was written into any owning file; no decision taken; no gate touched. Phase 0 is still the next task, beginning with `00-brief/project-brief.md`.

**2026-10-24 — Session 2 (proof of concept).** Owner asked for a folder showing what the two final deliverables look like when finished. Added `proof-of-concept/` with an example A0 ground-floor sheet at 1:100 (PDF, PNG, SVG; ISO 5457/7200 layout, Spanish labels, computed superficies útiles, grid, section marks, datum, legend, general notes) and an example exterior perspective at 3840 × 2160 (elevated viewpoint from the vine rows, harvest-season evening light, captioned), plus the two Python generators in `proof-of-concept/generators/` so the examples are revised by editing the scripts and regenerating. Its README and a pointer in `AGENTS.md` and `README.md` state that the folder is illustrative only. No design decision was taken; the example scheme is invented and nothing from it was written into any owning file. Phase 0 is still the next task, beginning with `00-brief/project-brief.md`.

**2026-10-24 — Session 1 (scaffold).** Created the full folder tree, README, AGENTS.md, STANDARDS.md, PHASE_PLAN.md, Instructional-merit.md, and a scaffold for every file. Owner fixed requirements recorded in AGENTS.md (Soria vineyard resort, 150 keys, winery, conference, breakfast and dinner restaurants, bar, spa; deliverables are floor plans and one rendered perspective). Standards layer set to Spanish and European practice (CTE, Eurocodes, LOE stages, metric). No design decisions have been made; no gate is closed. Open questions Q-01 to Q-05 seeded. Next: Phase 0 per PHASE_PLAN.md, beginning with the unfilled sections of `00-brief/project-brief.md`, then Gate 0 checklist.
