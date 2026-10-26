# AGENTS.md — read first, every session

This repository is a hotel design package used as a teaching instrument in a university architecture course. Sessions are short and many; this file exists so that no session undoes another session's work or re-derives the owner's requirements. Read it before touching any file. Update the "Fixed requirements" section only when the owner (the course instructor) changes a requirement, never on your own initiative.

## Fixed requirements (owner-given, not design decisions)

These are the brief. They are elaborated in `00-brief/project-brief.md` but originate here, and a session may not alter them.

- Location: Soria province, Castilla y León, Spain. The site is a working vineyard.
- Type: resort hotel set within the vineyard.
- Keys: 150 guestrooms. The mix across types is a design decision and lives in `03-program/area-schedule.csv`; the total is not.
- Winery: a small working winery on the site, part of the program and of the guest experience.
- Conference facility.
- Two restaurants: one serving breakfast, one serving dinner.
- A bar.
- A spa.
- Final deliverables: floor plans of the building and one rendered perspective of the building. Everything else in the package exists to make those two deliverables defensible.

## Where the live state is

Do not quote numbers from memory. Read them from the file that owns them.

| Question | Owning file |
|---|---|
| What is fixed by the owner | this file, then `00-brief/project-brief.md` |
| Areas, key counts by type, totals | `03-program/area-schedule.csv` |
| Which massing option was chosen and why | `10-delivery/decision-log.md` |
| What has been decided at all | `10-delivery/decision-log.md` |
| What is unresolved | `10-delivery/open-questions.md` |
| Which phase we are in and what closes it | `PHASE_PLAN.md`, `10-delivery/review-checklists.md` |
| Which standards and codes govern | `STANDARDS.md` |
| Financial inputs | `09-financials/assumptions-register.md` |

`proof-of-concept/` holds an illustrative example of each final deliverable and the scripts that generate them. It is a reference for format and finish only: never read a number, a dimension, a material, or a viewpoint from it into the project, and never cite it as a decision. Revise it only by editing its generator scripts and regenerating.

## Where we are

Do not infer the current phase from file contents. Read the newest entry under "Session notes" at the bottom of `10-delivery/decision-log.md`; it states what the last session finished and what it was in the middle of. Then open `PHASE_PLAN.md` at that phase and take the next unproduced file or unchecked gate item in `10-delivery/review-checklists.md` as the task. Size the task to one session: one file or one checklist cluster, not a whole phase.

## Rules for a session

1. Before editing, read the `Status` line of the file and the latest entries in `10-delivery/decision-log.md`. A decision there is closed; supersede it with a new record if it must change. Do not edit it or silently design around it.
2. A number lives in exactly one file. If you need it elsewhere, reference the owning file by path.
3. Any change that alters scope, area, cost, or an approved item gets a decision record from `templates/decision-record.md` in the same session.
4. Anything you could not resolve goes in `10-delivery/open-questions.md` with an owner, not into a draft as an unstated assumption.
5. Standards are Spanish and European (CTE, Eurocodes, UNE). Do not introduce U.S. codes, imperial units, or U.S. sheet conventions. See `STANDARDS.md`.
6. Do not advance a phase gate. Gates are closed by the instructor; a session proposes closure by completing the checklist in `10-delivery/review-checklists.md`.
7. When you finish, update the `Status` line and date on every file you touched, and leave a one-paragraph session note at the bottom of `10-delivery/decision-log.md` under "Session notes" stating what changed and what you were in the middle of.

## Why the repository looks the way it does

`Instructional-merit.md` explains the pedagogical reasoning. `README.md` explains the folder structure. Neither needs to be re-read every session; this file does.
