# Standards and Conventions

Status: draft — YYYY-MM-DD

The project is in Spain. Spanish and European standards govern. Where the course wants a comparison to U.S. practice for instructional reasons, the comparison is noted, but the Spanish standard is the one the design must meet. This file names the body of regulation that applies; confirm editions, regional decrees, and current clauses against the official text before relying on them, and record what you confirmed in `02-site/zoning-and-code.md`.

## Project phases (LOE and CTE Anejo I)

Spanish practice under the Ley de Ordenación de la Edificación defines the design stages this package follows. Approximate AIA B101 equivalents are given for students who know that framework.

| Spanish stage | Content | Nearest AIA equivalent |
|---|---|---|
| Estudio previo | Brief, site, program, feasibility | Pre-Design |
| Anteproyecto | Concept, massing, outline plans and volumetry | Schematic Design |
| Proyecto básico | Plans, sections, elevations sufficient for the licencia de obra; CTE basic requirements justified | late SD / early DD |
| Proyecto de ejecución | Full construction documents, structural and installation projects, mediciones y presupuesto | DD and CD |

This package stops at proyecto básico level for the architecture, with installations at concept level. The deliverables are the floor plans and one rendered perspective, per `AGENTS.md`.

## Building regulation

- Código Técnico de la Edificación (CTE): DB-SE structural safety, DB-SI fire safety, DB-SUA safety of use and accessibility, DB-HS health (water supply, drainage, indoor air), DB-HR protection against noise, DB-HE energy saving including the nearly-zero-energy requirement for new buildings.
- Eurocodes EN 1990 to EN 1999 with the Spanish national annexes for structural design.
- RITE (Reglamento de Instalaciones Térmicas en los Edificios) for HVAC. REBT for low-voltage electrical installations.
- Accessibility: CTE DB-SUA 9 plus the Castilla y León regional accessibility law and its reglamento. Accessible room count and dispersion follow the stricter of the two.
- Hotel classification: the Castilla y León tourism regulation on hotel establishments sets minimum room and bathroom sizes and common-area requirements per category. Identify the current decree and the target category (number of estrellas) in `00-brief/project-brief.md`.
- Winery: food-industry hygiene regulation, and the Denominación de Origen rules if the parcel is within a DO. Parts of Soria province fall within DO Ribera del Duero; confirm the parcel.
- Spa and pool: the regional sanitary regulation on public swimming pools and spa water quality.
- Urbanismo: the municipal Plan General de Ordenación Urbana or Normas Urbanísticas for the parcel, plus the Castilla y León land law for rural land (suelo rústico). A resort on agricultural land will almost certainly need a use authorization on suelo rústico; record the finding in `02-site/zoning-and-code.md`.

## Drawing conventions

- Units: metres and millimetres. Areas in m². Superficie útil and superficie construida are measured per the tourism regulation and the municipal ordinance respectively; state which one each figure is.
- Scales per UNE-EN ISO 5455: 1:500 or 1:1000 for the site; 1:200 for general plans; 1:100 for floor plans, sections, and elevations; 1:50 for guestroom and core enlargements; 1:20 and 1:10 for details.
- Sheet sizes and title block per UNE-EN ISO 5457 and UNE-EN ISO 7200. Line conventions per UNE-EN ISO 128.
- Sheet numbering: Spain has no single national sheet-numbering standard. This project uses a discipline prefix and a type digit (A-1xx plans, A-2xx elevations, A-3xx sections, A-4xx enlargements, A-5xx details, A-6xx schedules; E structure, I installations, U urbanización). The scheme is defined in `05-architecture/drawing-list.md` and is a project convention, not a code requirement.
- North arrow, graphic scale, and level datum on every plan. Levels in metres relative to a stated datum.

## Cost and measurement

- Presupuesto de Ejecución Material (PEM) organised by capítulos following a recognised regional price base. Exchange in FIEBDC-3 (BC3) format if the course uses estimating software.
- Early-stage comparison uses cost per key and cost per m² construido; both are reported in `09-financials/development-budget.md`.
- Operating accounts follow USALI, which is international hotel practice and used by Spanish operators.

## Sustainability

- DB-HE compliance is mandatory and sets the energy baseline. Voluntary certification (BREEAM ES, LEED, VERDE) is a brief decision recorded in `00-brief/project-brief.md`.

## Rendered perspective

- One exterior perspective, eye level or slightly elevated, from a viewpoint that shows the building's relationship to the vineyard. Viewpoint, time of day, and season are design decisions recorded in `05-architecture/rendered-perspective.md`.
