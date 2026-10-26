# Proof-of-concept exterior perspectives, built procedurally from the same example scheme as the plan sheet.
# Pinhole camera, painter's algorithm, Lambert shading, ground shadows, PIL post-process.
#
# Usage:  python make_render.py <output path without extension> [view]
#         python make_render.py <output path without extension> scene
# where view is a key of VIEWS below (default R-01). Each view sets camera, sun, season, sky and caption;
# the scheme itself is shared, so a change to the building changes every view. "scene" writes no image:
# it exports the same geometry, the view table and the season table as <output>.js for the fly-around
# page (proof-of-concept/portfolio.html), so the stills and the interactive model never drift apart.
import sys, math, random, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance

OUT = sys.argv[1]
VIEW = sys.argv[2] if len(sys.argv) > 2 else "R-01"
W, H = 3840, 2160

# ---------- views ----------
# sun_az is measured in plan maths convention: degrees anticlockwise from +x (east), so 243 is WSW and 340 is ESE.
# season: "harvest" (late September), "spring" (mid May, shoots to ~0.9 m), "winter" (dormant, pruned cordons)
VIEWS = {
    "R-01": dict(
        eye=(92.0, -74.0, 6.5), tgt=(40.0, 16.0, 3.5), hfov=58,              # drone at ~6 m, SE of the patio, over the vines
        sun_az=243, sun_el=16, sun_col=(1.00, 0.86, 0.66), sky_amb=(0.62, 0.72, 0.86),
        sky_top=(0.36, 0.52, 0.78), sky_hor=(0.93, 0.86, 0.74), glow=(0.22, 0.14, 0.02),
        soil_far=(0.72, 0.60, 0.44), soil_near=(0.50, 0.40, 0.29), fog_col=(0.80, 0.84, 0.90), fog_k=420.0,
        season="harvest", emissive=False, grade=(1.08, 1.06, 1.03, 0.97), seed=7,
        caption="R-01  ·  Vista exterior desde el viñedo, hacia el patio y la galería  ·  vendimia, 18:45",
    ),
    "R-02": dict(
        eye=(52.0, -14.0, 1.65), tgt=(36.0, 24.0, 5.0), hfov=66,              # eye level, in the vines south of the terrace wall, looking north across the patio to the gallery
        sun_az=340, sun_el=38, sun_col=(1.00, 0.95, 0.84), sky_amb=(0.66, 0.76, 0.90),
        sky_top=(0.30, 0.50, 0.82), sky_hor=(0.86, 0.90, 0.94), glow=(0.16, 0.14, 0.08),
        soil_far=(0.70, 0.62, 0.50), soil_near=(0.58, 0.50, 0.40), fog_col=(0.84, 0.88, 0.94), fog_k=600.0,
        season="spring", emissive=False, grade=(1.04, 1.05, 1.00, 1.00), seed=11,
        caption="R-02  ·  Patio entre spa y congresos, hacia la galería y las plantas de habitaciones  ·  mayo, 9:30",
    ),
    "R-03": dict(
        eye=(-20.0, -110.0, 42.0), tgt=(48.0, 24.0, 2.0), hfov=60,             # oblique aerial from the SW, ~50 m up
        sun_az=238, sun_el=4, sun_col=(1.00, 0.62, 0.36), sky_amb=(0.50, 0.56, 0.74),
        sky_top=(0.16, 0.22, 0.42), sky_hor=(0.96, 0.66, 0.44), glow=(0.30, 0.14, 0.00),
        soil_far=(0.52, 0.46, 0.42), soil_near=(0.40, 0.35, 0.32), fog_col=(0.72, 0.60, 0.60), fog_k=1300.0,
        season="winter", emissive=True, grade=(1.10, 1.08, 1.05, 0.96), seed=5,
        caption="R-03  ·  Vista aérea oblicua desde el suroeste: conjunto en el viñedo  ·  enero, 17:40, ocaso",
    ),
}
RECORD = VIEW == "scene"
if RECORD:
    VIEW = "R-01"
elif VIEW not in VIEWS:
    sys.exit("unknown view %s; choose from %s" % (VIEW, ", ".join(VIEWS)))
V = VIEWS[VIEW]
SCENE = {"boxes": [], "paving": [], "trees": [], "people": [], "vines": [], "views": VIEWS}
random.seed(V["seed"]); np.random.seed(V["seed"])

# ---------- camera ----------
EYE = np.array(V["eye"], float)
TGT = np.array(V["tgt"], float)
UP = np.array([0, 0, 1.0])
fwd = TGT - EYE; fwd /= np.linalg.norm(fwd)
right = np.cross(fwd, UP); right /= np.linalg.norm(right)
up = np.cross(right, fwd)
HFOV = math.radians(V["hfov"])
FX = (W / 2) / math.tan(HFOV / 2)
NEAR = 0.6

def project(p):
    d = np.asarray(p, float) - EYE
    zc = d @ fwd
    return (W / 2 + FX * (d @ right) / zc, H / 2 - FX * (d @ up) / zc, zc)

# ---------- light ----------
az, el = math.radians(V["sun_az"]), math.radians(V["sun_el"])
SUN = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
SUNCOL = np.array(V["sun_col"])
SKYCOL = np.array(V["sky_amb"])
SUNSTR = 0.95 if V["sun_el"] > 8 else 0.70          # near the horizon the direct component is weaker
EMISSIVE = V["emissive"]
LAMP = (0.98, 0.80, 0.52)                            # warm interior light seen through glass at dusk

def shade(base, n):
    base = np.array(base)
    diff = max(n @ SUN, 0.0)
    amb = 0.36 + 0.14 * max(n[2], 0)
    c = base * (amb * SKYCOL * 1.15 + SUNSTR * diff * SUNCOL)
    return np.clip(c, 0, 1)

def fog(c, depth):
    f = 1 - math.exp(-depth / V["fog_k"])
    return np.clip(np.array(c) * (1 - f) + np.array(V["fog_col"]) * f, 0, 1)

polys = []   # (depth, order, screen_pts, color, edgecolor, lw, alpha)

def add_poly(pts3, color, ec=None, lw=0.0, alpha=1.0, order=1, lit=True, normal=None):
    pts3 = [np.asarray(p, float) for p in pts3]
    if any(((p - EYE) @ fwd) < NEAR for p in pts3):
        return
    if normal is None:
        n = np.cross(pts3[1] - pts3[0], pts3[2] - pts3[0]); nn = np.linalg.norm(n)
        if nn < 1e-9: return
        n /= nn
        if (pts3[0] - EYE) @ n > 0: n = -n
    else:
        n = normal
    scr = [project(p) for p in pts3]
    depth = float(np.mean([s[2] for s in scr]))
    xs = [s[0] for s in scr]; ys = [s[1] for s in scr]
    if max(xs) < -200 or min(xs) > W + 200 or max(ys) < -200 or min(ys) > H + 200:
        return
    col = shade(color, n) if lit else np.array(color)
    col = fog(col, depth)
    polys.append((depth, order, list(zip(xs, ys)), col, ec, lw, alpha))

def box(x0, y0, z0, x1, y1, z1, color, roofcolor=None, ec=None, lw=0.0, order=1, lit=True, kind="solid"):
    rc = roofcolor if roofcolor is not None else color
    if RECORD:
        SCENE["boxes"].append([round(x0, 3), round(y0, 3), round(z0, 3), round(x1, 3), round(y1, 3), round(z1, 3),
                               [round(c, 3) for c in color], [round(c, 3) for c in rc], kind])
        return
    faces = [
        ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], color),   # south
        ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], color),   # east
        ([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], color),   # north
        ([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], color),   # west
        ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], rc),      # top
    ]
    for pts, c in faces:
        n = np.cross(np.array(pts[1]) - np.array(pts[0]), np.array(pts[2]) - np.array(pts[0])); n /= np.linalg.norm(n)
        ctr = np.mean(np.array(pts, float), axis=0)
        if (EYE - ctr) @ n <= 0: continue          # back-face cull
        add_poly(pts, c, ec=ec, lw=lw, order=order, normal=n, lit=lit)

def glass(x0, y0, z0, x1, y1, z1):
    """glazed band: cool reflective by day, warm and self-lit at dusk."""
    if RECORD:
        box(x0, y0, z0, x1, y1, z1, GLASS, roofcolor=ROOF, kind="glass")
    elif EMISSIVE:
        box(x0, y0, z0, x1, y1, z1, LAMP, roofcolor=LAMP, lit=False)
    else:
        box(x0, y0, z0, x1, y1, z1, GLASS, roofcolor=ROOF)

def shadow(x0, y0, z0, x1, y1, z1, alpha=0.42):
    """ground shadow of a box: hull of its 8 corners projected along the sun direction onto z=0."""
    if SUN[2] < 0.03 or RECORD:
        return
    pts = []
    for x in (x0, x1):
        for y in (y0, y1):
            for z in (z0, z1):
                t = z / SUN[2]
                pts.append((x - SUN[0] * t, y - SUN[1] * t, 0.0))
    pts = np.array(pts)[:, :2]
    P = sorted(map(tuple, pts))
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower = []
    for p in P:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0: lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(P):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0: upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    add_poly([(x, y, 0.001) for x, y in hull], (0.28, 0.24, 0.30), alpha=alpha, order=0, lit=False)

# ---------- ground & far landscape (drawn first, 2D) ----------
fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")

hx, hy, _ = project(EYE + np.array([fwd[0], fwd[1], 0]) * 5000)
hy = float(np.clip(hy, 1, H - 1))
sky = np.zeros((H, W, 3))
for r in range(H):
    if r < hy:
        u = r / max(hy, 1)
        c = np.array(V["sky_top"]) * (1 - u) ** 1.2 + np.array(V["sky_hor"]) * (1 - (1 - u) ** 1.2)
    else:
        u = (r - hy) / max(H - hy, 1)
        c = np.array(V["soil_far"]) * (1 - u) + np.array(V["soil_near"]) * u
    sky[r, :, :] = c
sx, sy, sz = project(EYE + SUN * 3000) if (SUN @ fwd) > -0.2 else (-W, hy, 1)
yy, xx = np.mgrid[0:H, 0:W]
glow = np.exp(-(((xx - sx) / (0.55 * W)) ** 2 + ((yy - sy) / (0.35 * H)) ** 2))
sky += glow[..., None] * np.array(V["glow"])
ax.imshow(np.clip(sky, 0, 1), extent=[0, W, H, 0], zorder=0, interpolation="bilinear")

def hills(seed, base_y, amp, colour, zorder):
    rs = np.random.RandomState(seed)
    xs = np.linspace(-100, W + 100, 400)
    ys = base_y - amp * (0.6 * np.sin(xs / 700 + rs.rand() * 6) + 0.4 * np.sin(xs / 230 + rs.rand() * 6) + 0.25 * np.sin(xs / 90 + rs.rand() * 6)) - amp * 0.4
    pts = list(zip(xs, ys)) + [(W + 100, H + 10), (-100, H + 10)]
    ax.add_patch(Polygon(pts, closed=True, fc=colour, ec="none", zorder=zorder))
hc = [fog(c, 3000) for c in ((0.60, 0.62, 0.70), (0.52, 0.54, 0.58), (0.48, 0.48, 0.44))]
hills(3, hy + 4, 90, hc[0], 1)
hills(5, hy + 14, 55, hc[1], 2)
hills(9, hy + 30, 28, hc[2], 3)

# ---------- building (from the example plan: public band y24-38, gallery y20-24, spa x0-30 y0-20, conference x50-98 y0-20) ----------
STONE = (0.78, 0.70, 0.56)          # local limestone, warm
STONE_D = (0.66, 0.58, 0.46)
TIMBER = (0.52, 0.36, 0.22)
ROOF = (0.30, 0.28, 0.26)
GLASS = (0.30, 0.40, 0.44)
DARK = (0.16, 0.15, 0.14)
PAVE = (0.84, 0.80, 0.72)

# public band: two storeys over the ground floor public rooms (guest floors above), stone
box(0, 24, 0, 72, 38, 4.6, STONE, ROOF); shadow(0, 24, 0, 72, 38, 4.6)
box(14, 24, 4.6, 72, 38, 11.0, STONE_D, ROOF); shadow(14, 24, 4.6, 72, 38, 11.0)
box(12, 22.4, 10.6, 74, 39, 11.2, TIMBER, ROOF)
# guest-floor windows on the south face (behind the fins) and the lobby's east face onto the porch
for fx_ in np.arange(15.0, 71.0, 4.0):
    glass(fx_, 23.95, 5.4, fx_ + 2.4, 24.05, 7.6); glass(fx_, 23.95, 8.2, fx_ + 2.4, 24.05, 10.2)
glass(71.9, 25, 0.3, 72.1, 37, 4.0)
# BOH band behind (lower)
box(0, 38, 0, 72, 50, 4.2, STONE_D, ROOF)
# gallery: glazed, with a timber roof slab and thin posts
glass(0, 20, 0.0, 86, 24, 3.9)
box(-1, 19.2, 3.9, 87, 24.6, 4.6, TIMBER, ROOF); shadow(-1, 19.2, 3.9, 87, 24.6, 4.6)
for px in np.arange(1.5, 86, 3.0):
    box(px - 0.12, 19.6, 0, px + 0.12, 19.84, 3.9, DARK)
# spa wing: low stone volume, pool hall glazed to the south
box(0, 0, 0, 30, 20, 4.2, STONE, ROOF); shadow(0, 0, 0, 30, 20, 4.2)
glass(12, -0.3, 0.3, 30, 0.1, 3.4)
box(-0.8, -1.5, 4.2, 30.8, 20.8, 4.8, TIMBER, ROOF)
# conference wing: meeting rooms + prefunction (4.8 m), congress hall taller (8.5 m), stone
box(50, 0, 0, 74, 20, 4.8, STONE, ROOF); shadow(50, 0, 0, 74, 20, 4.8)
box(74, 0, 0, 98, 20, 8.5, STONE, ROOF); shadow(74, 0, 0, 98, 20, 8.5)
box(73.4, -0.8, 8.5, 98.8, 20.8, 9.1, TIMBER, ROOF)
box(49.4, -0.8, 4.8, 74.6, 20.8, 5.4, TIMBER, ROOF)
glass(50.2, -0.25, 0.3, 97.8, 0.05, 3.6)                       # glazed foyer band under the fins
glass(97.9, 2, 0.3, 98.1, 18, 7.0)                              # congress hall east face (per the plan's glazing)
for fx_ in np.arange(74.8, 98, 1.5):
    box(fx_, -0.9, 0.4, fx_ + 0.14, 0.0, 8.2, TIMBER)
for fx_ in np.arange(50.6, 74, 1.5):
    box(fx_, -0.9, 0.4, fx_ + 0.14, 0.0, 4.5, TIMBER)
for fx_ in np.arange(14.5, 72, 1.2):
    box(fx_, 23.3, 5.0, fx_ + 0.14, 24.0, 10.4, TIMBER)
# tasting room pavilion east of the lobby, glazed to the east, and the winery hall behind
box(86, 24, 0, 98, 38, 5.0, STONE_D, ROOF); shadow(86, 24, 0, 98, 38, 5.0)
glass(97.9, 26, 0.3, 98.1, 36, 4.2)
box(86, 42, 0, 100, 52, 7.0, STONE_D, ROOF); shadow(86, 42, 0, 100, 52, 7.0)
box(85.4, 41.4, 7.0, 100.6, 52.6, 7.5, TIMBER, ROOF)
# porch: timber canopy on paired posts between the lobby's east face and the tasting pavilion, open to the court at its north end
box(76, 24, 4.4, 86, 40.6, 5.0, TIMBER, ROOF); shadow(76, 24, 4.4, 86, 40.6, 5.0, alpha=0.30)
for cx in (78, 84):
    for cy in (24.5, 39.5):
        box(cx - 0.2, cy - 0.2, 0, cx + 0.2, cy + 0.2, 4.4, DARK)
# guestroom wing A to the west, two storeys, set among the vines
box(-46, 12, 0, 0, 32, 7.4, STONE, ROOF); shadow(-46, 12, 0, 0, 32, 7.4)
box(-47, 11.2, 7.4, 1, 32.8, 8.0, TIMBER, ROOF)
for fx_ in np.arange(-45.5, -0.5, 1.2):
    box(fx_, 11.3, 0.4, fx_ + 0.14, 12.0, 7.0, TIMBER)
for fx_ in np.arange(-45.0, -1.0, 4.0):
    glass(fx_, 11.95, 0.6, fx_ + 2.4, 12.05, 2.8); glass(fx_, 11.95, 4.2, fx_ + 2.4, 12.05, 6.4)
# paving: patio, porch, arrival court, service yard, and the gravel drive from the east
def pave(quad, col):
    if RECORD:
        SCENE["paving"].append([[list(q) for q in quad], list(col)]); return
    add_poly([(x, y, 0.02) for x, y in quad], col, order=0)
pave([(30, 0), (50, 0), (50, 20), (30, 20)], PAVE)
pave([(76, 24), (86, 24), (86, 40), (76, 40)], (0.80, 0.77, 0.70))          # porch
pave([(72, 40), (86, 40), (86, 50), (72, 50)], (0.78, 0.75, 0.68))          # drop-off court
pave([(86, 38), (104, 38), (104, 42), (86, 42)], (0.74, 0.70, 0.62))        # arrival lane between tasting room and winery hall
pave([(-6, 40), (0, 40), (0, 50), (-6, 50)], (0.70, 0.68, 0.64))
pave([(104, 36), (260, 34), (260, 44), (104, 46)], (0.70, 0.66, 0.58))      # gravel drive from the east
# low dry-stone wall on the north side of the drive
box(104, 46.5, 0, 160, 47, 0.9, (0.62, 0.56, 0.46)); shadow(104, 46.5, 0, 160, 47, 0.9, alpha=0.3)
for by in (6.0, 12.0):
    box(33, by, 0, 47, by + 0.6, 0.45, STONE_D); shadow(33, by, 0, 47, by + 0.6, 0.45, alpha=0.35)
# low dry-stone terrace wall at the edge of the vines (y = -1.5), a Soria vernacular element
box(-50, -1.9, 0, 104, -1.3, 0.55, (0.62, 0.56, 0.46)); shadow(-50, -1.9, 0, 104, -1.3, 0.55, alpha=0.3)

# ---------- vineyard rows: N-S rows at 2.5 m, segmented; canopy by season ----------
SEASONS = {   # canopy height, half-width, canopy base, colour A, colour B, mix
    "harvest": dict(h=1.32, w=0.30, z0=0.35, a=[0.30, 0.43, 0.19], b=[0.60, 0.55, 0.20], mix=0.45),
    "spring":  dict(h=0.92, w=0.22, z0=0.45, a=[0.42, 0.58, 0.24], b=[0.52, 0.64, 0.30], mix=0.30),
    "winter":  dict(h=0.72, w=0.10, z0=0.50, a=[0.34, 0.26, 0.20], b=[0.44, 0.36, 0.28], mix=0.40),  # pruned cordons, no leaf
}
SCENE["seasons"] = SEASONS
SEASON = V["season"]; SP = SEASONS[SEASON]
ROW_H, ROW_W, CANOPY_Z0 = SP["h"], SP["w"], SP["z0"]
COL_A, COL_B, MIX = np.array(SP["a"]), np.array(SP["b"]), SP["mix"]
SEG = 3.0
def vine_block(y_from, y_to, x_from=-70, x_to=130):
    for rx in np.arange(x_from, x_to, 2.5):
        row_t = random.random()
        wdt = ROW_W + 0.06 * random.random()
        row_h = ROW_H + 0.12 * random.random()
        if RECORD:   # export continuous runs of this row, with its tint parameter
            run = None
            for ry in list(np.arange(y_from, y_to, SEG)) + [None]:
                skip = ry is None or (102 < rx and 32 < ry < 48)        # the drive
                if skip and run is not None:
                    SCENE["vines"].append([round(float(rx), 2), round(float(run[0]), 2), round(float(run[1]), 2), round(row_t, 3)]); run = None
                elif not skip:
                    run = [ry, min(ry + SEG, y_to)] if run is None else [run[0], min(ry + SEG, y_to)]
            continue
        for ry in np.arange(y_from, y_to, SEG):
            if 102 < rx and 32 < ry < 48: continue             # the drive
            d = np.array([rx, ry, 0]) - EYE
            if d @ fwd < 1.0: continue
            depth = d @ fwd
            if depth > 340: break
            t = 0.7 * row_t + 0.3 * random.random()
            c = tuple(COL_A * (1 - MIX * t) + COL_B * (MIX * t))
            x0, x1 = rx - wdt, rx + wdt
            y1 = min(ry + SEG, y_to)
            if depth < 140:
                shadow(x0, ry, CANOPY_Z0, x1, y1, row_h, alpha=0.26)
            box(x0, ry, CANOPY_Z0, x1, y1, row_h, c, roofcolor=tuple(np.clip(np.array(c) * 1.12, 0, 1)))
            if depth < 90:
                for ty in np.arange(ry + 0.5, y1, 1.2):
                    box(rx - 0.03, ty, 0, rx + 0.03, ty + 0.06, CANOPY_Z0 + 0.05, (0.30, 0.22, 0.14))   # trunks at 1,2 m
        box(rx - 0.06, y_to - 0.1, 0, rx + 0.06, y_to + 0.02, 1.9, (0.36, 0.30, 0.22))   # end post
vine_block(-160, -3.2)            # south of the terrace wall
vine_block(56, 220)               # north of the service band, beyond the winery
vine_block(-160, 220, 132, 260)   # east of the site, both sides of the drive (the drive itself is skipped)

# ---------- holm oaks (Quercus ilex) as billboard canopies ----------
def tree(x, y, r, hgt):
    if RECORD:
        SCENE["trees"].append([x, y, r, hgt]); return
    ctr = np.array([x, y, hgt]); d = ctr - EYE
    if d @ fwd < NEAR: return
    sx_, sy_, z = project(ctr)
    scale = FX / z
    nrm = np.array([-0.5, -0.5, 0.7]) / np.linalg.norm([-0.5, -0.5, 0.7])
    col = fog(shade((0.26, 0.34, 0.18), nrm), z)
    polys.append((z, 1, ("ellipse", sx_, sy_, 2 * r * scale, 1.5 * r * scale), col, None, 0, 1.0))
    lit = fog(shade((0.34, 0.42, 0.22), SUN), z)
    polys.append((z - 0.01, 1, ("ellipse", sx_ - 0.35 * r * scale, sy_ - 0.2 * r * scale, 1.3 * r * scale, 1.0 * r * scale), lit, None, 0, 0.85))
    polys.append((z + 0.01, 1, [(sx_ - 0.08 * r * scale, sy_ + 0.6 * r * scale), (sx_ + 0.08 * r * scale, sy_ + 0.6 * r * scale),
                                 (sx_ + 0.08 * r * scale, sy_ + (hgt) * scale), (sx_ - 0.08 * r * scale, sy_ + (hgt) * scale)],
                  fog((0.22, 0.17, 0.12), z), None, 0, 1.0))
    shadow(x - r, y - r * 0.7, hgt - r * 0.6, x + r, y + r * 0.7, hgt + r * 0.4, alpha=0.32)
for (tx, ty, tr, th) in [(40, 10, 3.8, 5.0), (36, 15, 3.0, 4.2), (102, 14, 4.5, 5.5), (108, -6, 5.0, 6.0),
                         (-56, 20, 4.2, 5.2), (-62, 5, 3.6, 4.6), (120, 30, 6.0, 7.0), (-30, 40, 5.0, 6.0),
                         (112, 52, 4.0, 5.0), (150, 50, 5.5, 6.5), (160, 10, 4.8, 5.8)]:
    tree(tx, ty, tr, th)

# ---------- people (1.7 m) ----------
def person(x, y, col=(0.20, 0.20, 0.24)):
    if RECORD:
        SCENE["people"].append([x, y, list(col)]); return
    base = np.array([x, y, 0]); d = base - EYE
    if d @ fwd < NEAR: return
    sx_, sy_, z = project(base); scale = FX / z
    hgt = 1.70 * scale; wdt = 0.42 * scale
    body = [(sx_ - wdt / 2, sy_), (sx_ + wdt / 2, sy_), (sx_ + wdt / 2.6, sy_ - hgt * 0.84), (sx_ - wdt / 2.6, sy_ - hgt * 0.84)]
    polys.append((z, 1, body, fog(col, z), None, 0, 1.0))
    polys.append((z, 1, ("ellipse", sx_, sy_ - hgt * 0.91, 0.24 * scale, 0.26 * scale), fog(col, z), None, 0, 1.0))
    shadow(x - 0.2, y - 0.1, 0.0, x + 0.2, y + 0.1, 1.7, alpha=0.3)
person(44, 4, (0.72, 0.66, 0.58)); person(45.2, 3.6, (0.24, 0.24, 0.30)); person(60, -2.4, (0.30, 0.28, 0.34))
person(70.2, -14, (0.62, 0.52, 0.42))
person(80, 41, (0.26, 0.26, 0.32)); person(81.1, 41.6, (0.70, 0.62, 0.52)); person(90, 40.5, (0.34, 0.30, 0.30))
# a car under the porch and one in the court, as two boxes (body and cabin), scaled 4.6 × 1.8 × 1.45 m
def car(x, y, col, along_x=True):
    L, Wd = (4.6, 1.8) if along_x else (1.8, 4.6)
    box(x, y, 0.2, x + L, y + Wd, 0.85, col, roofcolor=col); shadow(x, y, 0.2, x + L, y + Wd, 0.85, alpha=0.4)
    if along_x: box(x + 1.2, y + 0.15, 0.85, x + 3.6, y + Wd - 0.15, 1.45, DARK, roofcolor=col)
    else: box(x + 0.15, y + 1.2, 0.85, x + Wd - 0.15, y + 3.6, 1.45, DARK, roofcolor=col)
car(74.5, 43, (0.78, 0.78, 0.76), along_x=False); car(110, 39, (0.22, 0.24, 0.28))

# ---------- scene export ----------
if RECORD:
    plt.close(fig)
    with open(OUT + ".js", "w", encoding="utf-8") as f:
        f.write("// Generated by proof-of-concept/generators/make_render.py (scene mode). Do not edit by hand.\n")
        f.write("window.SCENE = " + json.dumps(SCENE, separators=(",", ":")) + ";\n")
    print("scene", {k: len(v) for k, v in SCENE.items() if isinstance(v, list)}, "->", OUT + ".js")
    sys.exit(0)

# ---------- draw ----------
polys.sort(key=lambda p: (-p[0], p[1]))
for depth, order, pts, col, ec, lw, alpha in polys:
    if isinstance(pts, tuple) and pts[0] == "ellipse":
        _, cx, cy, w_, h_ = pts
        ax.add_patch(Ellipse((cx, cy), w_, h_, fc=col, ec="none", alpha=alpha, zorder=10))
    else:
        ax.add_patch(Polygon(pts, closed=True, fc=col, ec=ec if ec else "none", lw=lw, alpha=alpha, zorder=10))

tmp = OUT + "_raw.png"
fig.savefig(tmp, dpi=200)
plt.close(fig)

# ---------- post-process ----------
im = Image.open(tmp).convert("RGB")
blur = im.filter(ImageFilter.GaussianBlur(2.2))
mask = Image.linear_gradient("L").resize((W, H)).point(lambda v: int(max(0, 170 - v * 1.2)))
im = Image.composite(blur, im, mask)
sat, con, rg, bg = V["grade"]
im = ImageEnhance.Color(im).enhance(sat)
im = ImageEnhance.Contrast(im).enhance(con)
r, g, b = im.split()
r = r.point(lambda v: min(255, int(v * rg + 3))); b = b.point(lambda v: min(255, int(v * bg)))
im = Image.merge("RGB", (r, g, b))
if EMISSIVE:   # bloom around the lit glazing
    lum = im.convert("L").point(lambda v: max(0, v - 185) * 3)
    bloom = Image.composite(im, Image.new("RGB", (W, H), (0, 0, 0)), lum).filter(ImageFilter.GaussianBlur(18))
    im = Image.fromarray(np.clip(np.asarray(im).astype(int) + (np.asarray(bloom).astype(int) * 0.55).astype(int), 0, 255).astype(np.uint8))
vig = Image.new("L", (W, H), 0); dv = ImageDraw.Draw(vig)
dv.ellipse((-W * 0.25, -H * 0.45, W * 1.25, H * 1.45), fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(420))
im = Image.composite(im, ImageEnhance.Brightness(im).enhance(0.72), vig)
noise = np.random.normal(0, 4.5, (H, W, 1)).repeat(3, axis=2)
arr = np.clip(np.asarray(im).astype(float) + noise, 0, 255).astype(np.uint8)
im = Image.fromarray(arr)
# caption band (small, bottom-right) so the image cannot be mistaken for project work
draw = ImageDraw.Draw(im)
try:
    f1 = ImageFont.truetype("arial.ttf", 34); f2 = ImageFont.truetype("arial.ttf", 26)
except Exception:
    f1 = f2 = ImageFont.load_default()
t1 = V["caption"]
t2 = "PRUEBA DE CONCEPTO — ejemplo ilustrativo del entregable; no es el proyecto."
w1 = draw.textlength(t1, font=f1); w2 = draw.textlength(t2, font=f2)
pad = 28
bx0 = W - max(w1, w2) - 2 * pad - 40; by0 = H - 130
draw.rectangle((bx0, by0, W - 40, H - 40), fill=(20, 18, 16))
draw.text((bx0 + pad, by0 + 16), t1, font=f1, fill=(236, 230, 220))
draw.text((bx0 + pad, by0 + 60), t2, font=f2, fill=(226, 120, 100))
im.save(OUT + ".png", optimize=True)
im.convert("RGB").save(OUT + ".jpg", quality=90)
import os; os.remove(tmp)
print(VIEW, "polys", len(polys), "sun", SUN.round(2), "horizon_y", round(hy))
