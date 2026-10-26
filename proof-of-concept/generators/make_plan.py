# Proof-of-concept floor plan sheet. A0 landscape, 1:100, metric, UNE-EN ISO 5457 / 7200 layout.
# Illustrative example only; geometry is invented and resolves nothing in the project record.
import sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Arc, Circle, FancyArrow
from matplotlib.lines import Line2D

OUT = sys.argv[1]
plt.rcParams["font.family"] = "Arial"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"

# ---------- sheet geometry (mm) ----------
SHEET_W, SHEET_H = 1189.0, 841.0          # A0 landscape
M_LEFT, M_OTHER = 20.0, 10.0              # ISO 5457 binding margin + other margins
SCALE = 100.0                             # 1:100 -> 1 m = 10 mm
TB_H = 56.0                               # title block strip height (mm)
fig = plt.figure(figsize=(SHEET_W / 25.4, SHEET_H / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, SHEET_W); ax.set_ylim(0, SHEET_H); ax.set_aspect("equal"); ax.axis("off")

INK = "#111111"; GREY = "#777777"; LIGHT = "#bbbbbb"; RED = "#b3261e"; BLUE = "#2b5f8e"

def mm(x_m, y_m):
    """metres in plan coords -> sheet mm. Drawing origin chosen so the plan sits above the title block."""
    return ORG_X + x_m * 1000.0 / SCALE, ORG_Y + y_m * 1000.0 / SCALE

# plan extents (m): x -10..104, y 0..52 -> 1140 x 520 mm
ORG_X = 160.0
ORG_Y = 200.0

# ---------- frame, margins, centring marks ----------
ax.add_patch(Rectangle((M_LEFT, M_OTHER), SHEET_W - M_LEFT - M_OTHER, SHEET_H - 2 * M_OTHER,
                       fill=False, lw=1.6, ec=INK))
for (x, y, dx, dy) in [(SHEET_W / 2, 0, 0, M_OTHER), (SHEET_W / 2, SHEET_H, 0, -M_OTHER),
                       (0, SHEET_H / 2, M_LEFT, 0), (SHEET_W, SHEET_H / 2, -M_OTHER, 0)]:
    ax.plot([x, x + dx], [y, y + dy], color=INK, lw=1.2)

# ---------- helpers ----------
def wall(x0, y0, x1, y1, t=0.15):
    """filled wall between two points (axis-aligned), thickness t in metres, centred on the line."""
    if abs(y1 - y0) < 1e-9:
        xa, xb = sorted([x0, x1]); X, Y = mm(xa - t / 2, y0 - t / 2)
        w = (xb - xa + t) * 10; h = t * 10
    else:
        ya, yb = sorted([y0, y1]); X, Y = mm(x0 - t / 2, ya - t / 2)
        w = t * 10; h = (yb - ya + t) * 10
    ax.add_patch(Rectangle((X, Y), w, h, fc=INK, ec=INK, lw=0, zorder=5))

def rect_walls(x0, y0, x1, y1, t=0.15):
    wall(x0, y0, x1, y0, t); wall(x0, y1, x1, y1, t); wall(x0, y0, x0, y1, t); wall(x1, y0, x1, y1, t)

def glazing(x0, y0, x1, y1):
    """curtain wall / fenestration: two thin lines, mullions every 1.5 m."""
    X0, Y0 = mm(x0, y0); X1, Y1 = mm(x1, y1)
    horiz = abs(y1 - y0) < 1e-9
    off = 1.2
    if horiz:
        ax.plot([X0, X1], [Y0 - off, Y1 - off], color=INK, lw=0.6, zorder=6)
        ax.plot([X0, X1], [Y0 + off, Y1 + off], color=INK, lw=0.6, zorder=6)
        n = int(abs(x1 - x0) / 1.5)
        for i in range(n + 1):
            xm = X0 + (X1 - X0) * i / max(n, 1)
            ax.plot([xm, xm], [Y0 - off, Y0 + off], color=INK, lw=0.6, zorder=6)
    else:
        ax.plot([X0 - off, X1 - off], [Y0, Y1], color=INK, lw=0.6, zorder=6)
        ax.plot([X0 + off, X1 + off], [Y0, Y1], color=INK, lw=0.6, zorder=6)
        n = int(abs(y1 - y0) / 1.5)
        for i in range(n + 1):
            ym = Y0 + (Y1 - Y0) * i / max(n, 1)
            ax.plot([X0 - off, X0 + off], [ym, ym], color=INK, lw=0.6, zorder=6)

def door(x, y, side, w=1.0, hinge="left", double=False):
    """door in a wall. side: 'h' wall runs horizontally at y (door spans x..x+w), opens to +y;
    'v' wall runs vertically at x (door spans y..y+w), opens to +x. Negative w flips the swing side."""
    sgn = 1 if w > 0 else -1; w = abs(w)
    X, Y = mm(x, y)
    if side == "h":
        ax.add_patch(Rectangle((X, Y - 2.2), w * 10, 4.4, fc="white", ec="none", zorder=7))
        leaves = [(X, 1), (X + w * 10, -1)] if double else [(X, 1)]
        for hx, d in leaves:
            L = (w / (2 if double else 1)) * 10
            ax.plot([hx, hx], [Y, Y + sgn * L], color=INK, lw=0.7, zorder=8)
            ax.add_patch(Arc((hx, Y), 2 * L, 2 * L, theta1=(0 if d > 0 else 90) if sgn > 0 else (270 if d > 0 else 180),
                             theta2=(90 if d > 0 else 180) if sgn > 0 else (360 if d > 0 else 270),
                             lw=0.4, color=GREY, zorder=8))
    else:
        ax.add_patch(Rectangle((X - 2.2, Y), 4.4, w * 10, fc="white", ec="none", zorder=7))
        leaves = [(Y, 1), (Y + w * 10, -1)] if double else [(Y, 1)]
        for hy, d in leaves:
            L = (w / (2 if double else 1)) * 10
            ax.plot([X, X + sgn * L], [hy, hy], color=INK, lw=0.7, zorder=8)
            if sgn > 0:
                t1, t2 = (0, 90) if d > 0 else (270, 360)
            else:
                t1, t2 = (90, 180) if d > 0 else (180, 270)
            ax.add_patch(Arc((X, hy), 2 * L, 2 * L, theta1=t1, theta2=t2, lw=0.4, color=GREY, zorder=8))

def label(x0, y0, x1, y1, name, area=None, size=7.0, dy=0.0, code=None):
    cx, cy = mm((x0 + x1) / 2, (y0 + y1) / 2 + dy)
    a = (x1 - x0) * (y1 - y0) if area is None else area
    txt = name if code is None else f"{code}  {name}"
    ax.text(cx, cy + 2.2, txt, ha="center", va="bottom", fontsize=size, color=INK, zorder=9)
    ax.text(cx, cy - 1.2, f"{a:.1f} m²".replace(".", ","), ha="center", va="top", fontsize=size - 1.2,
            color=GREY, zorder=9)
    return a

def hatch_exterior(x0, y0, x1, y1, kind="paving"):
    X, Y = mm(x0, y0)
    hatch = {"paving": "....", "vines": "||", "lawn": None}[kind]
    ax.add_patch(Rectangle((X, Y), (x1 - x0) * 10, (y1 - y0) * 10, fc="none", ec=LIGHT, lw=0.4,
                           hatch=hatch, zorder=1))

def dashed_rect(x0, y0, x1, y1, color=GREY, lw=0.8):
    X, Y = mm(x0, y0)
    ax.add_patch(Rectangle((X, Y), (x1 - x0) * 10, (y1 - y0) * 10, fc="none", ec=color, lw=lw, ls=(0, (6, 3)), zorder=4))

def column(x, y, s=0.4):
    X, Y = mm(x - s / 2, y - s / 2)
    ax.add_patch(Rectangle((X, Y), s * 10, s * 10, fc=INK, ec=INK, zorder=6))

def break_line(x, y0, y1):
    X0, Y0 = mm(x, y0); X1, Y1 = mm(x, y1)
    ys = np.linspace(Y0, Y1, 40); xs = X0 + 2.0 * np.sign(np.sin(np.arange(40) * math.pi))
    xs = X0 + np.where(np.arange(40) % 2 == 0, 0, 2.5)
    ax.plot(xs, ys, color=INK, lw=0.8, zorder=12)
    ax.add_patch(Rectangle((X0 - 12, Y0), 12, Y1 - Y0, fc="white", ec="none", zorder=11))

# ---------- rooms (metres) ----------
# zone bands: BOH y 40-50 (service corridor 38-40), public band y 24-38, gallery y 20-24,
# spa wing x 0-30 y 0-20, conference wing x 50-98 y 0-20, tasting room x 86-98 y 24-38.
rooms = []
def R(code, name, x0, y0, x1, y1, zone):
    rooms.append((code, name, x0, y0, x1, y1, zone))

# back of house (north band)
R("B.01", "Recepción de mercancías", 0, 40, 8, 50, "boh")
R("B.02", "Basuras y reciclaje", 8, 40, 13, 50, "boh")
R("B.03", "Almacén general", 13, 40, 20, 50, "boh")
R("B.04", "Lavandería y lencería", 20, 40, 32, 50, "boh")
R("B.05", "Vestuarios de personal", 32, 40, 40, 50, "boh")
R("B.06", "Comedor de personal", 40, 40, 46, 50, "boh")
R("B.07", "Administración", 46, 40, 56, 50, "boh")
R("B.08", "Mantenimiento", 56, 40, 62, 50, "boh")
R("B.09", "Sala de instalaciones", 62, 40, 72, 50, "boh")
R("B.10", "Pasillo de servicio", 0, 38, 72, 40, "boh")
# public band
R("C.01", "Cocina principal", 0, 24, 14, 38, "fnb")
R("C.02", "Restaurante de desayunos", 14, 24, 30, 38, "fnb")
R("C.03", "Restaurante de cenas", 30, 24, 46, 38, "fnb")
R("C.04", "Bar", 46, 24, 54, 38, "fnb")
R("A.01", "Vestíbulo y recepción", 54, 24, 72, 38, "arrival")
R("A.02", "Cortavientos", 72, 28, 76, 34, "arrival")
R("A.04", "Aseos públicos", 72, 34, 76, 38, "arrival")
R("A.05", "Equipajes", 72, 24, 76, 28, "arrival")
R("W.01", "Sala de catas y tienda", 86, 24, 98, 38, "winery")
R("A.03", "Galería (acceso a la viña)", 0, 20, 86, 24, "arrival")
# spa wing
R("S.01", "Recepción del spa", 0, 12, 8, 20, "spa")
R("S.02", "Vestuarios", 8, 12, 16, 20, "spa")
R("S.03", "Fitness", 16, 12, 30, 20, "spa")
R("S.04", "Cabina 1", 0, 6, 3, 12, "spa"); R("S.05", "Cabina 2", 3, 6, 6, 12, "spa")
R("S.06", "Cabina 3", 6, 6, 9, 12, "spa"); R("S.07", "Cabina 4", 9, 6, 12, 12, "spa")
R("S.08", "Sala de relajación", 0, 0, 12, 6, "spa")
R("S.09", "Circuito termal y piscina", 12, 0, 30, 12, "spa")
# conference wing
R("M.01", "Sala de reuniones 1", 50, 8, 56, 20, "conf")
R("M.02", "Sala de reuniones 2", 56, 8, 62, 20, "conf")
R("M.03", "Prefunción", 62, 4, 74, 20, "conf")
R("M.04", "Almacén y AV", 62, 0, 74, 4, "conf")
R("M.05", "Sala de congresos", 74, 0, 98, 20, "conf")
R("M.06", "Aseos", 50, 4, 62, 8, "conf")

# room floors (white) then walls
for code, name, x0, y0, x1, y1, zone in rooms:
    X, Y = mm(x0, y0)
    ax.add_patch(Rectangle((X, Y), (x1 - x0) * 10, (y1 - y0) * 10, fc="white", ec="none", zorder=2))
for code, name, x0, y0, x1, y1, zone in rooms:
    rect_walls(x0, y0, x1, y1, 0.15)

# exterior envelope at 300 mm
for (x0, y0, x1, y1) in [(0, 38, 72, 50), (0, 24, 72, 38), (72, 24, 76, 38), (86, 24, 98, 38),
                         (0, 20, 86, 24), (0, 0, 30, 20), (50, 0, 98, 20)]:
    rect_walls(x0, y0, x1, y1, 0.30)

# glazing: gallery south face, spa pool south, congress hall east, tasting room east, restaurants north? (no: BOH)
glazing(30, 20, 50, 20)          # gallery onto patio
glazing(12, 0, 30, 0)            # pool to vines
glazing(98, 0, 98, 20)           # congress hall east wall
glazing(98, 24, 98, 38)          # tasting room east wall to the vines
glazing(76, 24, 76, 38)          # lobby/porch face
glazing(86, 20, 86, 24)          # gallery east end

# doors (illustrative; swings into room unless noted)
door(60, 38, "h", 1.6, double=True)      # lobby <-> service corridor (back)
door(76, 29.5, "v", 3.0, double=True)    # entrance doors porch -> cortavientos
door(72, 29.5, "v", 3.0, double=True)    # cortavientos -> lobby
door(54, 29, "v", 1.8, double=True)      # lobby <-> bar
door(46, 29, "v", 1.8, double=True)      # bar <-> dinner restaurant
door(30, 29, "v", 1.8, double=True)      # dinner <-> breakfast
door(14, 30, "v", 1.4, double=True)      # kitchen -> breakfast
door(14, 36, "v", -1.4)                  # kitchen -> breakfast service
for xx in [7, 21, 37, 49, 62]:
    door(xx, 38, "h", -1.2)              # public rooms <-> service corridor
for xx in [4, 10, 16, 26, 36, 43, 51, 59, 67]:
    door(xx, 40, "h", 1.0)               # BOH rooms off service corridor
door(0, 44, "v", 2.4, double=True)       # receiving dock door
door(0, 20.5, "v", 1.4)                  # gallery west end to guestroom wing
for xx in [20, 37, 49, 60, 69, 80]:
    door(xx, 24, "h", 1.8, double=True)  # public rooms <-> gallery
door(4, 20, "h", -1.8, double=True)      # spa reception from gallery
door(55, 20, "h", -1.2); door(61, 20, "h", -1.2)   # meeting rooms from gallery
door(66, 20, "h", -1.8, double=True)     # prefunción from gallery
door(74, 8, "v", 1.8, double=True); door(74, 14, "v", 1.8, double=True)   # prefunción -> hall
door(84, 24, "h", -1.8, double=True)     # gallery end -> tasting room via porch? (tasting from porch)
door(86, 30, "v", 1.8, double=True)      # porch -> tasting room (the tasting room is also entered from the arrival lane side via the porch)
door(8, 15, "v", 1.0); door(16, 15, "v", 1.0)       # spa reception -> vestuarios -> fitness
for xx in [1, 4, 7, 10]:
    door(xx, 12, "h", -0.9)              # cabins from a spa corridor (implied in reception strip)
door(12, 6, "v", 1.2)                    # vestuarios -> pool
door(13, 12, "h", -1.2)                  # pool from vestuarios
door(5, 6, "h", -1.2)                    # relaxation room
door(68, 4, "h", 1.2)                    # AV store
door(32, 38, "h", -1.2)                  # dinner restaurant pass from service corridor

# ---------- exterior elements ----------
# porch east of the lobby: covered walk between the lobby face (x 76) and the tasting room (x 86),
# open to the drop-off court at its north end; dashed roof outline, columns at the two long edges
dashed_rect(76, 24, 86, 40, color=GREY, lw=0.9)
for cx in [78, 84]:
    for cy in [24.5, 39.5]:
        column(cx, cy, 0.4)
hatch_exterior(76, 24, 86, 40, "paving")
# drop-off court north of the porch, and the one-way arrival lane from the east between the tasting room and the winery hall
hatch_exterior(72, 40, 86, 50, "paving")
hatch_exterior(86, 38, 104, 42, "paving")
# patio between spa and conference wings
hatch_exterior(30, 8, 50, 20, "paving")
hatch_exterior(30, 0, 50, 8, "vines")
# winery production hall, separate volume, shown in outline only
dashed_rect(86, 42, 100, 52, color=INK, lw=1.0)
Xc, Yc = mm(93, 47)
ax.text(Xc, Yc + 4, "Nave de elaboración y bodega", ha="center", fontsize=7.5, color=INK, zorder=9)
ax.text(Xc, Yc - 1, "cota −4,50 m bajo rasante; ver A-104", ha="center", fontsize=6, color=GREY, zorder=9)
Xc, Yc = mm(93, 43.5)
ax.text(Xc, Yc, "acceso de vendimia desde el norte (ver U-101)", ha="center", fontsize=5.5, color=GREY, zorder=9)
# service yard
hatch_exterior(-6, 40, 0, 50, "paving")
Xc, Yc = mm(-3, 45)
ax.text(Xc, Yc, "Patio de\nservicio", ha="center", va="center", fontsize=6, color=GREY, zorder=9)

# guestroom wing stub (continues west; see A-102)
rooms_wing = []
for i, x0 in enumerate([-8, -4]):
    for (y0, y1, tag) in [(24, 32, "N"), (12, 20, "S")]:
        X, Y = mm(x0, y0)
        ax.add_patch(Rectangle((X, Y), 40, (y1 - y0) * 10, fc="white", ec="none", zorder=2))
        rect_walls(x0, y0, x0 + 4, y1, 0.15)
        if tag == "N":
            door(x0 + 1.4, y0, "h", -0.9)
        else:
            door(x0 + 1.4, y1, "h", 0.9)
        cx, cy = mm(x0 + 2, (y0 + y1) / 2)
        ax.text(cx, cy + 1.5, "Hab.", ha="center", fontsize=6, zorder=9)
        ax.text(cx, cy - 1.5, "tipo", ha="center", va="top", fontsize=6, zorder=9)
X, Y = mm(-8, 20); ax.add_patch(Rectangle((X, Y), 80, 40, fc="white", ec="none", zorder=2))
rect_walls(-8, 12, 0, 32, 0.30)
wall(-8, 20, 0, 20, 0.15); wall(-8, 24, 0, 24, 0.15)
break_line(-8, 11.5, 32.5)
Xc, Yc = mm(-4, 22)
ax.text(Xc, Yc, "Ala A — continúa,\nver A-102", ha="center", va="center", fontsize=6.5,
        color=INK, zorder=9, rotation=0)

# vineyard rows to the south and east (site context, not part of the building)
for yv in np.arange(-5.5, -1, 2.0):
    X0, Y0 = mm(-8, yv); X1, Y1 = mm(100, yv)
    ax.plot([X0, X1], [Y0, Y1], color="#8aa86d", lw=1.4, zorder=1, alpha=0.9)
Xc, Yc = mm(40, -3.5)
ax.text(Xc, Yc, "VIÑEDO  (hileras existentes, marco 2,50 m; ver U-101)", ha="center", va="center",
        fontsize=7, color="#5f7a44", zorder=9, bbox=dict(fc="white", ec="none", pad=1.5))

# ---------- labels ----------
total_util = 0.0
zone_tot = {}
for code, name, x0, y0, x1, y1, zone in rooms:
    size = 7.5 if (x1 - x0) >= 8 and (y1 - y0) >= 8 else (6.2 if (x1 - x0) >= 4 else 5.2)
    rot = 0
    if (x1 - x0) < 3.5:
        cx, cy = mm((x0 + x1) / 2, (y0 + y1) / 2)
        ax.text(cx, cy, f"{code} {name}\n{(x1-x0)*(y1-y0):.1f} m²".replace(".", ","), ha="center", va="center",
                fontsize=5, rotation=90, zorder=9)
        a = (x1 - x0) * (y1 - y0)
    elif code == "A.03":
        a = (x1 - x0) * (y1 - y0)
        cx, cy = mm(40, 22)
        ax.text(cx, cy, f"{code}  {name}   {a:.1f} m²".replace(".", ","), ha="center", va="center", fontsize=7, zorder=9)
    elif code == "B.10":
        a = (x1 - x0) * (y1 - y0)
        cx, cy = mm(36, 39)
        ax.text(cx, cy, f"{code}  {name}   {a:.1f} m²".replace(".", ","), ha="center", va="center", fontsize=6, zorder=9)
    else:
        a = label(x0, y0, x1, y1, name, size=size, code=code)
    total_util += a
    zone_tot[zone] = zone_tot.get(zone, 0) + a
# wing rooms (6 x 32 m2) counted separately as "shown for context"

# reception desk, bar counter, pool outline, hall seating as light furniture
def furn_rect(x0, y0, x1, y1, lw=0.5, ls="-"):
    X, Y = mm(x0, y0)
    ax.add_patch(Rectangle((X, Y), (x1 - x0) * 10, (y1 - y0) * 10, fc="none", ec=GREY, lw=lw, ls=ls, zorder=6))
furn_rect(66, 30, 70, 31.2)          # reception desk
furn_rect(47, 33, 53, 34.2)          # bar counter
furn_rect(14, 1.5, 28, 9)            # pool
Xc, Yc = mm(21, 5.2); ax.text(Xc, Yc, "piscina 14 × 7,5 m", ha="center", fontsize=5.5, color=GREY, zorder=9)
for i in range(9):                   # congress hall rows (theatre layout, indicative)
    furn_rect(77.5, 3 + i * 1.6, 95.5, 3.5 + i * 1.6, lw=0.3)
furn_rect(94, 3, 97.5, 17, lw=0.3, ls="--")   # stage zone

# ---------- cores: stairs and lifts ----------
def stair(x0, y0, x1, y1, n=12, vertical=True):
    X, Y = mm(x0, y0)
    ax.add_patch(Rectangle((X, Y), (x1 - x0) * 10, (y1 - y0) * 10, fc="white", ec=INK, lw=0.7, zorder=6))
    for i in range(1, n):
        if vertical:
            yy = Y + (y1 - y0) * 10 * i / n; ax.plot([X, X + (x1 - x0) * 10], [yy, yy], color=INK, lw=0.4, zorder=7)
        else:
            xx = X + (x1 - x0) * 10 * i / n; ax.plot([xx, xx], [Y, Y + (y1 - y0) * 10], color=INK, lw=0.4, zorder=7)
    # direction arrow
    cx, cy = mm((x0 + x1) / 2, (y0 + y1) / 2)
    ax.annotate("", xy=(cx, cy + (y1 - y0) * 4) if vertical else (cx + (x1 - x0) * 4, cy),
                xytext=(cx, cy - (y1 - y0) * 4) if vertical else (cx - (x1 - x0) * 4, cy),
                arrowprops=dict(arrowstyle="->", lw=0.6, color=INK), zorder=8)

def lift(x0, y0, x1, y1):
    X, Y = mm(x0, y0)
    ax.add_patch(Rectangle((X, Y), (x1 - x0) * 10, (y1 - y0) * 10, fc="white", ec=INK, lw=0.7, zorder=6))
    ax.plot([X, X + (x1 - x0) * 10], [Y, Y + (y1 - y0) * 10], color=INK, lw=0.4, zorder=7)
    ax.plot([X, X + (x1 - x0) * 10], [Y + (y1 - y0) * 10, Y], color=INK, lw=0.4, zorder=7)

stair(55, 34.5, 58, 37.5, n=10, vertical=False); lift(58, 35.5, 60, 37.5); lift(60, 35.5, 62, 37.5)
Xc, Yc = mm(58.5, 33.5); ax.text(Xc, Yc, "núcleo 1: escalera protegida + 2 ascensores (ver A-402)", fontsize=5, color=GREY, ha="center", zorder=9)
stair(89, 25, 92, 28, n=10, vertical=False)
Xc, Yc = mm(90.5, 24.6); ax.text(Xc, Yc, "escalera a bodega −4,50", fontsize=5, color=GREY, ha="center", va="top", zorder=9)
stair(33, 40.5, 36, 43.5, n=10, vertical=False)   # service stair
Xc, Yc = mm(34.5, 44); ax.text(Xc, Yc, "escalera de servicio", fontsize=5, color=GREY, ha="center", zorder=9)

# ---------- structural grid ----------
gx = [(-8, "A"), (0, "B"), (14, "C"), (30, "D"), (46, "E"), (54, "F"), (62, "G"), (72, "H"), (76, "J"), (86, "K"), (98, "L")]
gy = [(0, "1"), (8, "2"), (12, "3"), (20, "4"), (24, "5"), (38, "6"), (40, "7"), (50, "8")]
for x, t in gx:
    X0, Y0 = mm(x, -7); X1, Y1 = mm(x, 55)
    ax.plot([X0, X1], [Y0, Y1], color=BLUE, lw=0.35, ls=(0, (8, 4)), zorder=3, alpha=0.8)
    ax.add_patch(Circle((X1, Y1 + 6), 4.2, fc="white", ec=BLUE, lw=0.7, zorder=10))
    ax.text(X1, Y1 + 6, t, ha="center", va="center", fontsize=6.5, color=BLUE, zorder=11)
for y, t in gy:
    X0, Y0 = mm(-10, y); X1, Y1 = mm(101, y)
    ax.plot([X0, X1], [Y0, Y1], color=BLUE, lw=0.35, ls=(0, (8, 4)), zorder=3, alpha=0.8)
    ax.add_patch(Circle((X0 - 5, Y0), 4.2, fc="white", ec=BLUE, lw=0.7, zorder=10))
    ax.text(X0 - 5, Y0, t, ha="center", va="center", fontsize=6.5, color=BLUE, zorder=11)

# ---------- section marks ----------
def section_mark(x0, y0, x1, y1, tag):
    X0, Y0 = mm(x0, y0); X1, Y1 = mm(x1, y1)
    ax.plot([X0, X1], [Y0, Y1], color=INK, lw=1.0, ls=(0, (12, 4, 2, 4)), zorder=10)
    for (X, Y, dxy) in [(X0, Y0, -1), (X1, Y1, 1)]:
        ax.add_patch(Circle((X, Y), 5, fc="white", ec=INK, lw=0.8, zorder=10))
        ax.text(X, Y, tag, ha="center", va="center", fontsize=6.5, weight="bold", zorder=11)
        if abs(x1 - x0) > abs(y1 - y0):
            ax.annotate("", xy=(X, Y - 12), xytext=(X, Y - 5), arrowprops=dict(arrowstyle="-|>", lw=0.8, color=INK), zorder=10)
        else:
            ax.annotate("", xy=(X - 12, Y), xytext=(X - 5, Y), arrowprops=dict(arrowstyle="-|>", lw=0.8, color=INK), zorder=10)
section_mark(63, -6, 63, 53, "A")       # through lobby & conference (A-301)
section_mark(-11, 31, 101.5, 31, "B")      # longitudinal through public band
Xc, Yc = mm(63, 54.5); ax.text(Xc + 8, Yc, "A-301", fontsize=5.5, color=INK, zorder=11)
Xc, Yc = mm(100.5, 31); ax.text(Xc, Yc + 7, "A-301", fontsize=5.5, color=INK, zorder=11)

# entrance arrow
Xc, Yc = mm(104, 40)
ax.annotate("", xy=(Xc - 110, Yc), xytext=(Xc, Yc), arrowprops=dict(arrowstyle="-|>", lw=1.6, color=INK), zorder=10)
ax.text(Xc - 55, Yc - 4, "ACCESO PRINCIPAL (llegada desde el este, ver U-101)", fontsize=6.5, ha="center", va="top", zorder=10, bbox=dict(fc="white", ec="none", pad=1))

# level datum
Xc, Yc = mm(63, 27)
ax.plot([Xc - 5, Xc + 5], [Yc, Yc], color=INK, lw=0.8, zorder=10)
ax.add_patch(Polygon([[Xc - 2.5, Yc], [Xc + 2.5, Yc], [Xc, Yc - 3.5]], fc="none", ec=INK, lw=0.8, zorder=10))
ax.text(Xc + 6, Yc + 0.5, "±0,00  (= cota absoluta de proyecto, ver U-101)", fontsize=6, va="bottom", zorder=10)
Xc, Yc = mm(21, 5.2)
ax.text(Xc, Yc - 5, "pavimento −0,02 / lámina de agua −0,30", fontsize=5, color=GREY, ha="center", zorder=10)

# ---------- north arrow & graphic scale ----------
nx, ny = SHEET_W - M_OTHER - 55, SHEET_H - M_OTHER - 55
ax.add_patch(Circle((nx, ny), 22, fc="white", ec=INK, lw=0.8, zorder=10))
ax.add_patch(Polygon([[nx, ny + 18], [nx - 6, ny - 10], [nx, ny - 4]], fc=INK, ec=INK, zorder=11))
ax.add_patch(Polygon([[nx, ny + 18], [nx + 6, ny - 10], [nx, ny - 4]], fc="white", ec=INK, lw=0.8, zorder=11))
ax.text(nx, ny + 26, "N", ha="center", va="bottom", fontsize=11, weight="bold", zorder=11)
ax.text(nx, ny - 30, "norte geográfico\n(desviación según U-101)", ha="center", va="top", fontsize=5.5, color=GREY, zorder=11)

sx, sy = M_LEFT + 20, M_OTHER + TB_H + 22
ax.text(sx, sy + 9, "ESCALA GRÁFICA 1:100", fontsize=7, weight="bold", zorder=10)
for i in range(10):
    ax.add_patch(Rectangle((sx + i * 10, sy), 10, 3, fc=INK if i % 2 == 0 else "white", ec=INK, lw=0.6, zorder=10))
for i in [0, 2, 4, 6, 8, 10]:
    ax.text(sx + i * 10, sy - 1.5, f"{i}", ha="center", va="top", fontsize=6, zorder=10)
ax.text(sx + 104, sy - 1.5, "m", ha="left", va="top", fontsize=6, zorder=10)

# ---------- legend ----------
lx, ly = M_LEFT + 150, M_OTHER + TB_H + 36
ax.text(lx, ly, "LEYENDA", fontsize=7, weight="bold", zorder=10)
items = [
    ("muro de fachada / sectorización, e = 300 mm", "wall30"),
    ("tabiquería interior, e = 150 mm", "wall15"),
    ("carpintería acristalada (muro cortina), montantes c/ 1,50 m", "glass"),
    ("puerta, con sentido de apertura", "door"),
    ("volumen fuera de este plano (trazo), ver plano indicado", "dash"),
    ("eje estructural y referencia de pilar", "grid"),
    ("pavimento exterior / hileras de viña existentes", "ext"),
]
for i, (txt, kind) in enumerate(items):
    yy = ly - 7 - i * 5.2
    if kind == "wall30": ax.add_patch(Rectangle((lx, yy - 1.2), 14, 2.4, fc=INK, zorder=10))
    if kind == "wall15": ax.add_patch(Rectangle((lx, yy - 0.6), 14, 1.2, fc=INK, zorder=10))
    if kind == "glass":
        ax.plot([lx, lx + 14], [yy - 1, yy - 1], color=INK, lw=0.6, zorder=10); ax.plot([lx, lx + 14], [yy + 1, yy + 1], color=INK, lw=0.6, zorder=10)
    if kind == "door":
        ax.plot([lx, lx], [yy - 1.5, yy + 3], color=INK, lw=0.7, zorder=10)
        ax.add_patch(Arc((lx, yy - 1.5), 9, 9, theta1=0, theta2=90, lw=0.4, color=GREY, zorder=10))
    if kind == "dash": ax.plot([lx, lx + 14], [yy, yy], color=GREY, lw=0.9, ls=(0, (6, 3)), zorder=10)
    if kind == "grid":
        ax.plot([lx, lx + 10], [yy, yy], color=BLUE, lw=0.35, ls=(0, (8, 4)), zorder=10)
        ax.add_patch(Circle((lx + 12, yy), 2.2, fc="white", ec=BLUE, lw=0.6, zorder=10))
    if kind == "ext":
        ax.add_patch(Rectangle((lx, yy - 1.5), 6, 3, fc="none", ec=LIGHT, hatch="....", lw=0.3, zorder=10))
        ax.plot([lx + 8, lx + 14], [yy, yy], color="#8aa86d", lw=1.4, zorder=10)
    ax.text(lx + 18, yy, txt, fontsize=5.8, va="center", zorder=10)

# ---------- area table (superficies útiles of this sheet) ----------
tx, ty = M_LEFT + 420, M_OTHER + TB_H + 36
ax.text(tx, ty, "SUPERFICIES ÚTILES DE ESTE PLANO (planta baja, m²; medición sobre el dibujo)", fontsize=7, weight="bold", zorder=10)
order = [("arrival", "Llegada y galería"), ("fnb", "Restauración (dos restaurantes, bar, cocina)"), ("conf", "Congresos"),
         ("spa", "Spa"), ("winery", "Bodega, parte visitable"), ("boh", "Zonas de servicio")]
for i, (z, t) in enumerate(order):
    yy = ty - 7 - i * 5.0
    ax.text(tx, yy, t, fontsize=5.8, va="center", zorder=10)
    ax.text(tx + 170, yy, f"{zone_tot[z]:.1f}".replace(".", ","), fontsize=5.8, va="center", ha="right", zorder=10)
yy = ty - 7 - 6 * 5.0
ax.plot([tx, tx + 172], [yy + 2.5, yy + 2.5], color=INK, lw=0.5, zorder=10)
ax.text(tx, yy, "Total superficie útil, planta baja (sin ala de habitaciones)", fontsize=5.8, weight="bold", va="center", zorder=10)
ax.text(tx + 170, yy, f"{total_util:.1f}".replace(".", ","), fontsize=5.8, weight="bold", va="center", ha="right", zorder=10)
ax.text(tx, yy - 6, "Superficie construida y cuadro completo por niveles: A-601. Esta tabla no sustituye a 03-program/area-schedule.csv.",
        fontsize=5, color=GREY, va="center", zorder=10)

# ---------- general notes ----------
nx0, ny0 = M_LEFT + 640, M_OTHER + TB_H + 36
ax.text(nx0, ny0, "NOTAS GENERALES", fontsize=7, weight="bold", zorder=10)
notes = [
    "1. Cotas en metros; espesores en milímetros. Nivel ±0,00 referido a la cota absoluta fijada en U-101.",
    "2. Superficies útiles medidas según el reglamento turístico de Castilla y León; construidas según ordenanza municipal (ver STANDARDS.md).",
    "3. Sectores de incendio, recorridos de evacuación y ocupación según CTE DB-SI: plano A-002. Itinerarios accesibles DB-SUA 9: A-002.",
    "4. Planta tipo de habitaciones: A-102. Planta de bodega (−4,50): A-104. Secciones A-A y B-B: A-301. Alzados: A-201.",
    "5. Este plano forma parte de proof-of-concept/ y es un EJEMPLO de formato y nivel de acabado. No representa el proyecto.",
]
for i, t in enumerate(notes):
    ax.text(nx0, ny0 - 7 - i * 5.2, t, fontsize=5.6, va="center", zorder=10, color=RED if i == 4 else INK)

# ---------- title block (ISO 7200 fields) ----------
tb_x0, tb_y0 = M_LEFT, M_OTHER
tb_w = SHEET_W - M_LEFT - M_OTHER
ax.add_patch(Rectangle((tb_x0, tb_y0), tb_w, TB_H, fill=False, lw=1.2, ec=INK, zorder=10))
ax.plot([tb_x0, tb_x0 + tb_w], [tb_y0 + TB_H, tb_y0 + TB_H], color=INK, lw=1.2, zorder=10)
cols = [0, 260, 520, 700, 860, 980, 1060, tb_w]
for c in cols[1:-1]:
    ax.plot([tb_x0 + c, tb_x0 + c], [tb_y0, tb_y0 + TB_H], color=INK, lw=0.8, zorder=10)
def field(cx, cy, w, title, value, vs=8.5, ts=5.0, bold=False):
    ax.text(tb_x0 + cx + 3, tb_y0 + cy + 2, title, fontsize=ts, color=GREY, va="bottom", zorder=11)
    ax.text(tb_x0 + cx + 3, tb_y0 + cy + 10, value, fontsize=vs, va="bottom", weight="bold" if bold else "normal", zorder=11)
# col 1: owner / project
ax.plot([tb_x0, tb_x0 + 260], [tb_y0 + 28, tb_y0 + 28], color=INK, lw=0.5, zorder=10)
field(0, 28, 260, "Propietario / cliente", "Curso de Proyectos — Universidad (ejemplo docente)", vs=7.5)
field(0, 0, 260, "Proyecto", "Hotel resort en viñedo, 150 llaves\nProvincia de Soria, Castilla y León", vs=7.5)
# col 2: sheet title
field(260, 0, 260, "Título del plano", "PLANTA BAJA\nSuperficies útiles, ejes y referencias", vs=12, bold=True)
# col 3: phase / status
ax.plot([tb_x0 + 520, tb_x0 + 700], [tb_y0 + 28, tb_y0 + 28], color=INK, lw=0.5, zorder=10)
field(520, 28, 180, "Fase (LOE / CTE Anejo I)", "Proyecto básico", vs=7.5)
field(520, 0, 180, "Estado del documento", "EJEMPLO — PRUEBA DE CONCEPTO", vs=7.5, bold=True)
ax.text(tb_x0 + 523, tb_y0 + 10, "EJEMPLO — PRUEBA DE CONCEPTO", fontsize=7.5, weight="bold", color=RED, zorder=12,
        bbox=dict(fc="white", ec="none", pad=0.5))
# col 4: drawn/checked/approved
for i, (t, v) in enumerate([("Dibujado", "sesión PoC"), ("Comprobado", "—"), ("Aprobado", "—")]):
    yy = TB_H - 18 - i * 18
    ax.plot([tb_x0 + 700, tb_x0 + 860], [tb_y0 + yy, tb_y0 + yy], color=INK, lw=0.5, zorder=10) if i < 2 else None
    ax.text(tb_x0 + 703, tb_y0 + yy + 2, t, fontsize=5, color=GREY, zorder=11)
    ax.text(tb_x0 + 703, tb_y0 + yy + 8.5, v, fontsize=7, zorder=11)
# col 5: scale / format / date
ax.plot([tb_x0 + 860, tb_x0 + 980], [tb_y0 + 28, tb_y0 + 28], color=INK, lw=0.5, zorder=10)
field(860, 28, 120, "Escala (UNE-EN ISO 5455)", "1:100", vs=10, bold=True)
field(860, 0, 120, "Formato / fecha", "A0  ·  2026-10-24", vs=7.5)
# col 6: revision
ax.plot([tb_x0 + 980, tb_x0 + 1060], [tb_y0 + 28, tb_y0 + 28], color=INK, lw=0.5, zorder=10)
field(980, 28, 80, "Revisión", "P01", vs=10, bold=True)
field(980, 0, 80, "Unidades", "m / mm", vs=7.5)
# col 7: sheet number
field(1060, 0, tb_w - 1060, "Nº de plano", "A-101", vs=22, bold=True)
ax.text(tb_x0 + 1063, tb_y0 + TB_H - 6, "ejemplo", fontsize=6, color=RED, va="top", zorder=11)

# corner stamp (top-left) so no one mistakes the sheet
sx0, sy0 = M_LEFT + 8, SHEET_H - M_OTHER - 8
ax.add_patch(Rectangle((sx0, sy0 - 34), 250, 34, fc="white", ec=RED, lw=1.4, zorder=20))
ax.text(sx0 + 6, sy0 - 8, "PRUEBA DE CONCEPTO · PROOF OF CONCEPT", fontsize=9.5, weight="bold", color=RED, va="top", zorder=21)
ax.text(sx0 + 6, sy0 - 19, "Ejemplo del formato y nivel de acabado exigido al entregable A-101.\nGeometría inventada; no resuelve ninguna cuestión del registro de decisiones.",
        fontsize=5.8, color=RED, va="top", zorder=21)

# sheet caption top centre
ax.text(SHEET_W / 2, SHEET_H - M_OTHER - 16, "PLANTA BAJA  ·  cota ±0,00  ·  escala 1:100", ha="center", fontsize=13, weight="bold", zorder=20)

fig.savefig(OUT + ".pdf", format="pdf")
fig.savefig(OUT + ".png", dpi=110)
fig.savefig(OUT + ".svg", format="svg")
print("rooms", len(rooms), "total util", round(total_util, 1), {k: round(v, 1) for k, v in zone_tot.items()})
