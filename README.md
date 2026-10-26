# Vineyard Resort Hotel, Soria — Design Package

A structured workspace for taking a hotel from brief to a reviewable design package, used as a teaching instrument in a university architecture course. The project is a 150-key resort hotel with a small winery, conference facility, two restaurants, a bar, and a spa, set within a working vineyard in Soria province, Spain. The two final deliverables are the floor plans and one rendered exterior perspective.

Start here:

- `AGENTS.md` carries the owner's fixed requirements and the rules every working session must follow. Read it first, every session.
- `PHASE_PLAN.md` sequences the work and names what closes each phase.
- `STANDARDS.md` names the Spanish and European standards the design must meet and the drawing and cost conventions used.
- `Instructional-merit.md` explains why the package is structured this way as a teaching instrument, and where that structure needs the instructor's correction.

Folders are numbered in the order the work flows; each holds the documents that must exist before the next phase can start. Every file is a scaffold: section headings, the questions each section must answer, the files it reads from and feeds, and a `Status` line. Fill the sections in place rather than creating parallel documents, so one path always holds the current answer.

## How the folders fit together

| Folder | Component | Answers the question |
|---|---|---|
| `00-brief/` | Project brief, goals, constraints, stakeholders, glossary | What are we building, for whom, under what limits? |
| `01-market/` | Market study, competitive set, guest personas, positioning | Who will stay here, and why would they pick us? |
| `02-site/` | Site analysis, planning and regulatory summary, climate | What does the land allow and demand? |
| `03-program/` | Space program, area schedule, adjacency matrix, room mix | How many of what, how big, next to what? |
| `04-concept/` | Design narrative, massing options, precedents | What is the idea, and which massing carries it? |
| `05-architecture/` | Drawing list, plans, sections, facade, structure, CTE compliance, rendered perspective | How is the building arranged, held up, and shown? |
| `06-interiors/` | Guestroom types, public areas, FF&E, materials | What does a guest see, touch, and sleep in? |
| `07-systems/` | MEP, vertical transport, life safety, IT, sustainability | What makes the building run, and how efficiently? |
| `08-operations/` | Staffing, back-of-house flows, winery operations, service and brand standards | Can staff run this layout, including at harvest? |
| `09-financials/` | Development budget (PEM), pro forma (USALI), assumptions register | Does it pay back, on what assumptions? |
| `10-delivery/` | Decision log, risk register, review checklists, open questions | What did we decide, what could go wrong, what is unresolved? |
| `assets/` | `drawings/`, `renders/`, `references/` | Binary artefacts referenced from the documents above |
| `templates/` | Room type sheet, decision record | Copy, do not invent, when adding a new one |
| `proof-of-concept/` | One worked example of each final deliverable, with the scripts that generate them | What does a finished plan sheet and a finished perspective look like? Illustrative only; nothing in it is the project. |

## Necessary components

A hotel design is not complete until each of the following exists and they agree with each other. Dependencies run roughly downward; a change higher up must be propagated.

1. **Brief** (`00-brief/`). Owner objectives, target category, budget envelope, schedule, non-negotiables, and the fixed requirements carried from `AGENTS.md`.
2. **Market basis** (`01-market/`). Demand drivers for a wine-tourism resort, the competitive set, and the positioning gap. Drives room mix, conference and spa sizing, and the financial assumptions.
3. **Site and regulatory basis** (`02-site/`). Parcel planning classification and the suelo rústico authorization route, edificabilidad and height, access for guests and for harvest traffic, climate and orientation. Bounds the massing.
4. **Space program** (`03-program/`). The area schedule is the single source of truth for keys by type (summing to 150), restaurant and bar covers, conference capacity, spa scope, winery areas, and back of house. Architecture, interiors, operations, and financials all read from it.
5. **Concept and massing** (`04-concept/`). The organising idea and the massing chosen from alternatives tested against site and program.
6. **Architecture** (`05-architecture/`). Floor plans at every distinct level (the deliverable), sections and elevations, facade strategy, structural concept, CTE compliance in outline, and the rendered perspective brief (the other deliverable).
7. **Interiors** (`06-interiors/`). One sheet per guestroom type including accessible variants, public-area intent, FF&E schedule, materials palette.
8. **Building systems** (`07-systems/`). HVAC and plant strategy under RITE, water and drainage including winery effluent, electrical, lifts, fire protection under DB-SI, IT, and the DB-HE energy path.
9. **Operations model** (`08-operations/`). Staffing by department, back-of-house flows, winery operations and the harvest flow, service standards, brand or operator standards.
10. **Financials** (`09-financials/`). PEM by capítulos, USALI pro forma, assumptions register citing every input.
11. **Delivery records** (`10-delivery/`). Decision log with session notes, risk register, phase-gate checklists, open questions.

## Conventions

- One topic per file. The `Status` line states `draft`, `in review`, or `approved` and the date.
- Numbers live in exactly one place. The area schedule owns areas and key counts; the assumptions register owns financial inputs; `AGENTS.md` owns the fixed requirements. Everything else references the owning file by path.
- Decisions that change scope, cost, or program get a decision record in `10-delivery/decision-log.md` using `templates/decision-record.md`. Closed decisions are superseded, never edited.
- Metric units, Spanish and European standards, and the sheet scheme in `STANDARDS.md` throughout.
- Drawings and images go in `assets/` and are linked by relative path from the document that discusses them.
- A phase closes when its checklist in `10-delivery/review-checklists.md` passes and the instructor accepts it.
