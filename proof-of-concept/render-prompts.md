# Render prompts — for generators specialised in architectural imagery

Status: example — 2026-10-24

These prompts describe the **example scheme** in `proof-of-concept/`, not the project. They exist so that the procedural stills (`R-01` to `R-03`) can be pushed to a photographic level of finish in a tool built for that, while staying on the same geometry, viewpoints, seasons and hours. Anything produced from them goes in this folder with the name pattern `R-0n-perspectiva-ejemplo-<tool>.png`, is stamped with the caption band using `generators/stamp_caption.py` so it cannot be mistaken for project work, and is never copied into `assets/renders/`.

The procedural still is the input, not just the reference: every tool below works best image-to-image, with the still (or the model view from `portfolio.html`, screenshotted at the same preset) as the structure guide. Text-only generation will invent a different building; do not use it for anything that claims to show the scheme.

## Shared description of the scheme (paste before each view prompt)

> Resort hotel set inside a working vineyard on the high plateau of Soria province, Castilla y León, at about 1,000 m altitude. Low, long volumes in warm local limestone with dark, thin flat roofs; deep timber fascias; a single-storey fully glazed gallery with slender dark posts running along the south edge of the main block, opening onto the vines; vertical timber brise-soleil fins at 1,2 m centres on the two guest floors above the gallery and on the south face of the conference hall. A low spa wing to the west and a conference wing to the east frame a paved patio with two holm oaks and low stone benches. A taller winery hall sits behind, to the north-east. A low dry-stone terrace wall separates the paving from the vine rows. Vine rows run north–south at 2,5 m spacing, trellised on wire with timber end posts; the land is nearly flat with the Sistema Ibérico foothills low on the northern horizon. No signage, no logos, no text in the image.

## R-01 — from the vines, harvest evening

> Camera about 6 m above the vine canopy, 90 m south-east of the patio, 28 mm lens, looking north-west across the rows towards the patio and the glazed gallery. Late September, vendimia: dense vine canopy turning from green to yellow, a few pickers' crates at a row end. Sun very low in the west-south-west, warm, long shadows striping the rows; the timber fins throw thin parallel shadows across the limestone. Clear sky, pale warm horizon, cool zenith. Two guests on the patio, one picker in the rows, scale 1:1 with the building. Photographic architectural visualisation, physically based materials, soft global illumination, slight haze in the far field, no HDR glow, no lens flare, 16:9.

## R-02 — the patio from the vines, May morning

> Eye level, 1,65 m, standing in the vine rows just south of the terrace wall, 28 mm lens, looking north across the patio to the gallery, the timber fins and the two guest floors behind. Mid May: shoots about 90 cm high, fresh bright green, bare soil between rows, the wall's limestone catching the sun. Morning sun from the east-south-east, about 38° high, lighting the spa wing's east face and the south faces; the conference wing's west face in open shade. Two guests crossing the patio under the holm oak. Crisp, cool sky, clean dry air. Photographic architectural visualisation, physically based materials, no HDR glow, 16:9.

## R-03 — oblique aerial, January dusk

> Drone view from the south-west, about 42 m up and 120 m out, 26 mm lens, looking north-east over the whole complex: guestroom wing on the left among the rows, spa wing, patio, gallery and main block in the centre, conference hall on the right, winery hall behind. Mid January: vines pruned to cordons, no leaf, bare dark rows reading as pure geometry on pale winter soil; no snow. Sun just set in the south-west, sky grading from ember orange at the horizon to deep blue, long soft dusk; interior lights on behind the gallery glazing and the guest-floor windows, warm, not blown out. Thin ground mist in the far field. Photographic architectural visualisation, blue hour, physically based lighting, 16:9.

## Negative or "avoid" list (for tools that take one)

> pitched roofs, red clay tiles, white render, arches, wine barrels in the foreground, mountains behind the building, palm trees, swimming pool in view, cars in view, people larger than the doors, text, watermark, signage, lens flare, oversaturated sunset, fisheye distortion.

## Tool-specific notes

- **Image-to-image diffusion (SDXL / Flux with ControlNet depth or canny, Veras, LookX, PromeAI):** feed the procedural still; set structure strength high (depth or canny conditioning weight 0,8 to 1,0; "geometry preservation" or "creativity" at the stricter end) so massing, fin rhythm and row spacing survive; let the tool re-material and relight. Denoise around 0,45 to 0,6 keeps the composition.
- **Midjourney (image prompt plus `--iw 2`, `--ar 16:9`, `--style raw`):** use the still as the image prompt and the view text as the prompt; raise `--iw` if the building drifts. Expect it to add topography; reject outputs where the ground is not flat.
- **Enscape / D5 / Twinmotion AI enhancers, Krea or Magnific upscalers:** these keep geometry by construction; use the model view from `portfolio.html` at the matching preset and the shared description as the style prompt. Upscalers: keep "resemblance" high and "creativity" low.
- **Any tool:** check the output against the plan sheet. Fins at 1,2 m centres, gallery posts at 3,0 m, rows at 2,5 m, two guest floors, one gallery storey. If a count is wrong the image is not of the scheme, however good it looks.
