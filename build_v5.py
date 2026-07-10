"""
Colo NAS Enclosure v5 — CadQuery parametric model
7.5" × 7.5" × 2.5" folded sheet metal box
Mini ITX + 2x 3.5" HDD + 1U CPU cooler
"""

import cadquery as cq
from cadquery import exporters
import os, math

IN = 25.4
MT = 1.2  # metal thickness (18 ga)

# Case: width(X) × depth(Y) × height(Z)
CX = 7.5 * IN   # 190.5
CY = 7.5 * IN   # 190.5
CZ = 2.5 * IN   # 63.5

# HDD (SFF-8301)
HW = 4.0 * IN     # 101.6
HD = 5.787 * IN   # 147.0
HH = 1.028 * IN   # 26.1
HS = 0.25 * IN    # screw inset from side
HF = 1.75 * IN    # front screw row
HR = 1.625 * IN   # rear screw row from rear

# Motherboard (Mini ITX)
MW = 6.7 * IN     # 170
MD = 6.7 * IN     # 170
MH = 1.6
SH = 10.0          # standoff height
MB_X = 10.0        # MB position in case coords
MB_Y = CY - MD - 10.0  # I/O at rear wall
INSET = 6.35       # standoff inset from board edge

# --- Functions ---

def at_origin(dx, dy, dz):
    """Box centered at origin"""
    return cq.Workplane("XY").box(dx, dy, dz)

def at_corner(dx, dy, dz, cx, cy, cz=0):
    """Box whose MIN corner is at (cx, cy, cz)"""
    return at_origin(dx, dy, dz).translate((cx + dx/2, cy + dy/2, cz + dz/2))


# =====================
# CASE BODY
# =====================

# Start with bottom panel (Y=0 = front, Y=CY = rear)
case = at_corner(CX, CY, MT, 0, 0, 0)

# Front wall (Y=0, goes up from MT)
case = case.union(at_corner(CX, MT, CZ - MT, 0, 0, MT))

# Rear wall (Y=CY-MT, goes up from MT)
case = case.union(at_corner(CX, MT, CZ - MT, 0, CY - MT, MT))

# === CUTOUTS ===

# I/O shield — 158.75×44mm centered in rear wall
io_w = 158.75
io_h = 44
io_x = (CX - io_w) / 2
io_y = CY + 1      # punch through rear wall
io_z = (CZ - io_h) / 2
case = case.cut(at_corner(io_w, MT + 2, io_h, io_x, io_y, io_z))

# 60mm fan cutout — rear wall, right side
fan_x = CX - 75
fan_y = CY + 1
fan_z = (CZ - 60) / 2
case = case.cut(at_corner(60, MT + 2, 60, fan_x, fan_y, fan_z))

# Fan screw holes
for fx, fz in [(5, 5), (55, 5), (5, 55), (55, 55)]:
    screw = (at_origin(4, MT + 2, 4)
             .translate((fan_x + fx + 2, fan_y + 1, fan_z + fz + 2)))
    case = case.cut(screw)

# Vent slots — front wall
for vz in range(int(MT + 15), int(CZ - 15), 15):
    case = case.cut(at_corner(CX - 40, MT + 2, 2, 20, -1, vz))

# Standoff mounting holes — 4× M3 clearance in bottom panel
for sx, sy in [(INSET, INSET), (INSET, MD - INSET),
               (MW - INSET, INSET), (MW - INSET, MD - INSET)]:
    hole = (at_origin(3.4, 3.4, MT + 2)
            .translate((MB_X + sx + 1.7, MB_Y + sy + 1.7, -1)))
    case = case.cut(hole)


# =====================
# TOP PANEL
# =====================

top = at_corner(CX, CY, MT, 0, 0, CZ - MT)

# HDD mounting holes — 6-32 countersunk, through top panel
# HDD2 position: (h2x, h2y) from case corner
h2x = 10
h2y = 10

hdd_screw_ys = [HF, HD - HR, 3.0 * IN]  # A6, A7, A13
for sy in hdd_screw_ys:
    for side in [-1, 1]:
        sx = HW / 2 + side * (HW / 2 - HS)
        hole = (at_origin(3.6, 3.6, MT + 2)
                .translate((h2x + sx + 1.8, h2y + sy + 1.8, CZ - MT - 1)))
        top = top.cut(hole)

# Vent holes
for vx in range(25, int(CX - 25), 30):
    for vy in range(25, int(CY - 25), 30):
        skip = False
        for sy in hdd_screw_ys:
            for side in [-1, 1]:
                sx = HW / 2 + side * (HW / 2 - HS)
                if abs(vx - (h2x + sx)) < 12 and abs(vy - (h2y + sy)) < 12:
                    skip = True
        if not skip:
            top = top.cut(
                at_origin(3, 3, MT + 2)
                .translate((vx + 1.5, vy + 1.5, CZ - MT - 1))
            )

case = case.union(top)


# =====================
# INTERNAL COMPONENTS (cosmetic)
# =====================

# --- HDD1 — bottom, back-right, right-side up ---
h1x = CX - HW - 10
h1y = CY - HD - 8
hdd1_z = MT + 2

hdd1 = at_corner(HW, HD, HH, h1x, h1y, hdd1_z)

# PCB on bottom
hdd1 = hdd1.union(at_corner(HW, 30, 2, h1x, h1y + HD - 30, hdd1_z))

# SATA connectors at rear
hdd1 = hdd1.union(at_corner(24, 2, 8, h1x + HW / 2 - 12, h1y + HD, hdd1_z + HH / 2 - 4))
hdd1 = hdd1.union(at_corner(16, 2, 8, h1x + HW / 2 + 14, h1y + HD, hdd1_z + HH / 2 - 4))

case = case.union(hdd1)

# --- HDD2 — top, front-left, upside-down ---
h2x = 10
h2y = 8
hdd2_z = CZ - MT - HH - 0.5  # bottom of HDD

hdd2 = at_corner(HW, HD, HH, h2x, h2y, hdd2_z)

# PCB on top (it's upside down)
hdd2 = hdd2.union(at_corner(HW, 30, 2, h2x, h2y + HD - 30, hdd2_z + HH - 2))

# SATA connectors at rear
hdd2 = hdd2.union(at_corner(24, 2, 8, h2x + HW / 2 - 12, h2y + HD, hdd2_z + HH / 2 - 4))
hdd2 = hdd2.union(at_corner(16, 2, 8, h2x + HW / 2 + 14, h2y + HD, hdd2_z + HH / 2 - 4))

case = case.union(hdd2)

# --- Standoffs ---
for sx, sy in [(INSET, INSET), (INSET, MD - INSET),
               (MW - INSET, INSET), (MW - INSET, MD - INSET)]:
    so = (cq.Workplane("XY")
          .circle(3.5).circle(1.75).extrude(SH)
          .translate((MB_X + sx, MB_Y + sy, MT)))
    case = case.union(so)

# --- Motherboard ---
mb_z = MT + SH
mb = at_corner(MW, MD, MH, MB_X, MB_Y, mb_z)

# CPU socket
mb = mb.union(at_corner(40, 40, 2, MB_X + 60, MB_Y + MD - 85, mb_z + MH))

# 1U cooler
mb = mb.union(at_corner(36, 36, 13, MB_X + 62, MB_Y + MD - 83, mb_z + MH + 2))

# RAM
mb = mb.union(at_corner(55, 8, 6, MB_X + 110, MB_Y + MD - 12, mb_z + MH + 3))

# I/O shield (along rear edge of board)
io_off = (MW - io_w) / 2
mb = mb.union(at_corner(io_w, 2, 44, MB_X + io_off, MB_Y + MD, mb_z + MH))

case = case.union(mb)


# =====================
# CENTER AND EXPORT
# =====================

case = case.translate((-CX / 2, -CY / 2, 0))

bb = case.val().BoundingBox()
print(f"Bounding box:")
print(f"  X: {bb.xmin:.1f} to {bb.xmax:.1f} = {bb.xmax - bb.xmin:.1f}mm ({((bb.xmax - bb.xmin) / IN):.2f}\")")
print(f"  Y: {bb.ymin:.1f} to {bb.ymax:.1f} = {bb.ymax - bb.ymin:.1f}mm ({((bb.ymax - bb.ymin) / IN):.2f}\")")
print(f"  Z: {bb.zmin:.1f} to {bb.zmax:.1f} = {bb.zmax - bb.zmin:.1f}mm ({((bb.zmax - bb.zmin) / IN):.2f}\")")

outdir = "/tmp/colo-nas-case-2"
os.makedirs(outdir, exist_ok=True)

stl_path = os.path.join(outdir, "colo_nas_v5.stl")
exporters.export(case, stl_path)
print(f"\nSTL: {stl_path} ({os.path.getsize(stl_path)} bytes)")

step_path = os.path.join(outdir, "colo_nas_v5.step")
exporters.export(case, step_path)
print(f"STEP: {step_path} ({os.path.getsize(step_path)} bytes)")

print("DONE")
