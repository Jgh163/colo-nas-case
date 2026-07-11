"""
Colo NAS Enclosure v6 — ZimaBlade 7700 + PCIe IPMI via riser
7.5" × 7.5" × 2.5" folded sheet metal
Layout: HDDs left, ZimaBlade+IPMI right
"""

import cadquery as cq
from cadquery import exporters
import os

IN = 25.4
MT = 1.2  # 18 ga

# Case
CX = 7.5 * IN   # 190.5
CY = 7.5 * IN   # 190.5
CZ = 2.5 * IN   # 63.5

# HDD (SFF-8301)
HW = 4.0 * IN     # 101.6
HD = 5.787 * IN   # 147.0
HH = 1.028 * IN   # 26.1
HS = 0.25 * IN    # screw inset
HF = 1.75 * IN
HR = 1.625 * IN

# ZimaBlade 7700
ZW = 80    # 80mm
ZD = 107   # 107mm
ZH = 23    # 23mm (board + tallest component)
# I/O ports are on one 107mm edge (rear):
# USB 3.0, GbE LAN, MiniDP, DC power, 2× SATA

# PCIe IPMI card (BliKVM v2 or similar, laid flat via riser)
PW = 70    # ~70mm (half-height PCIe card width when flat)
PD = 120   # ~120mm (card length)
PH = 15    # ~15mm including riser offset + card thickness

# Standoff height for ZimaBlade above bottom panel
ZB_SH = 5  # 5mm standoffs to clear bottom panel

# Layout:
# X=0 to X=HW+12: HDDs (with 12mm for mounting + clearance)
# X=HW+12+gap to X=CX-10: ZimaBlade (80mm wide)
# Y: HDDs at front (Y=8 to Y=HD+8=155)
# Y: ZimaBlade at back (Y=CY-ZD-10 to Y=CY-10)

HDD_X = 8             # HDDs start at X=8mm
HDD_Y = 8             # HDDs start at Y=8mm
ZB_X = CX - ZW - 10   # ZimaBlade X: right side with margin
ZB_Y = CY - ZD - 10   # ZimaBlade Y: back
IO_GAP = 8            # space for I/O connectors at rear

def atc(dx, dy, dz, cx, cy, cz=0):
    """Box at corner (cx,cy,cz) with dimensions dx,dy,dz"""
    return cq.Workplane("XY").box(dx, dy, dz).translate((cx+dx/2, cy+dy/2, cz+dz/2))


# ===================== CASE BODY =====================
case = cq.Workplane("XY")

# Bottom
case = case.union(atc(CX, CY, MT, 0, 0, 0))

# Front wall
case = case.union(atc(CX, MT, CZ-MT, 0, 0, MT))

# Rear wall
case = case.union(atc(CX, MT, CZ-MT, 0, CY-MT, MT))

# === CUTOUTS ===

# ZimaBlade I/O cutout (rear wall) — group of ports on the right side
# The ZimaBlade has: DC jack, USB 3.0, GbE, MiniDP, 2× SATA
# We'll make a single rectangular cutout for the I/O area
io_cut_x = ZB_X + 5
io_cut_w = ZW - 10
io_cut_h = 35  # enough for stacked connectors
io_cut_y = CY + 1
io_cut_z = (CZ - io_cut_h) / 2
case = case.cut(atc(io_cut_w, MT+2, io_cut_h, io_cut_x, io_cut_y, io_cut_z))

# Ventilation slots (front wall)
for vz in range(int(MT+15), int(CZ-15), 15):
    case = case.cut(atc(CX-40, MT+2, 2, 20, -1, vz))

# Ventilation holes (rear wall, left side near HDDs)
for vx in range(10, int(HDD_X + HW), 25):
    for vz in range(int(MT+15), int(CZ-15), 20):
        case = case.cut(atc(3, MT+2, 3, vx, CY, vz))

# === MOUNTING HOLES ===

# ZimaBlade mounting holes — 4× M3 on bottom panel
# ZimaBlade has 4 mounting holes, roughly at corners
for sx, sy in [(5,5), (5,ZD-5), (ZW-5,5), (ZW-5,ZD-5)]:
    hole = atc(3.4, 3.4, MT+2, ZB_X+sx, ZB_Y+sy, -1)
    case = case.cut(hole)


# ===================== TOP PANEL =====================
top = atc(CX, CY, MT, 0, 0, CZ-MT)

# HDD mounting holes — 6-32 countersunk (for HDD2, left side)
h2x = HDD_X
h2y = HDD_Y
hdd_screw_ys = [HF, HD-HR, 3.0*IN]
for sy in hdd_screw_ys:
    for side in [-1, 1]:
        sx = HW/2 + side * (HW/2 - HS)
        hole = atc(3.6, 3.6, MT+2, h2x+sx, h2y+sy, CZ-MT-1)
        top = top.cut(hole)

# Vent holes (right side, above ZimaBlade area)
for vx in range(int(ZB_X)+15, int(CX-15), 20):
    for vy in range(int(ZB_Y)+15, int(ZB_Y+ZD-15), 20):
        top = top.cut(atc(3, 3, MT+2, vx, vy, CZ-MT-1))

# Vent holes (left side, above HDDs, avoiding screw holes)
for vx in range(int(HDD_X)+35, int(HDD_X+HW-35), 25):
    for vy in range(int(HDD_Y)+35, int(HDD_Y+HD-35), 25):
        skip = False
        for sy in hdd_screw_ys:
            for side in [-1, 1]:
                sx = HW/2 + side * (HW/2 - HS)
                if abs(vx-(h2x+sx))<10 and abs(vy-(h2y+sy))<10:
                    skip = True
        if not skip:
            top = top.cut(atc(3, 3, MT+2, vx, vy, CZ-MT-1))

case = case.union(top)


# ===================== INTERNAL COMPONENTS =====================

# --- HDD1 (bottom, right-side up) ---
hdd1_z = MT + 2
hdd1 = atc(HW, HD, HH, HDD_X, HDD_Y, hdd1_z)
hdd1 = hdd1.union(atc(HW, 30, 2, HDD_X, HDD_Y+HD-30, hdd1_z))
hdd1 = hdd1.union(atc(24, 2, 8, HDD_X+HW/2-12, HDD_Y+HD, hdd1_z+HH/2-4))
hdd1 = hdd1.union(atc(16, 2, 8, HDD_X+HW/2+14, HDD_Y+HD, hdd1_z+HH/2-4))
case = case.union(hdd1)

# --- HDD2 (top, upside-down, suspended) ---
hdd2_z = CZ - MT - HH - 0.5
hdd2 = atc(HW, HD, HH, HDD_X, HDD_Y, hdd2_z)
hdd2 = hdd2.union(atc(HW, 30, 2, HDD_X, HDD_Y+HD-30, hdd2_z+HH-2))
hdd2 = hdd2.union(atc(24, 2, 8, HDD_X+HW/2-12, HDD_Y+HD, hdd2_z+HH/2-4))
hdd2 = hdd2.union(atc(16, 2, 8, HDD_X+HW/2+14, HDD_Y+HD, hdd2_z+HH/2-4))
case = case.union(hdd2)

# --- ZimaBlade (bottom, right side, I/O at rear) ---
zb_z = MT + ZB_SH
zb = atc(ZW, ZD, ZH, ZB_X, ZB_Y, zb_z)
# Simplify: add a box for the board with some detail
case = case.union(zb)

# --- PCIe IPMI (via riser, above ZimaBlade) ---
# IPMI card sits flat above the ZimaBlade
# Need to account for riser cable height (~5mm) + card thickness
ipmi_z = zb_z + ZH + 5  # 5mm riser gap
ipmi = atc(PW, PD, PH, ZB_X + (ZW-PW)/2, ZB_Y + (ZD-PD)/2, ipmi_z)
case = case.union(ipmi)


# ===================== CENTER AND EXPORT =====================
case = case.translate((-CX/2, -CY/2, 0))

bb = case.val().BoundingBox()
print(f"Bounding box:")
print(f"  X: {bb.xmin:.1f} to {bb.xmax:.1f} = {bb.xmax-bb.xmin:.1f}mm ({((bb.xmax-bb.xmin)/IN):.2f}\")")
print(f"  Y: {bb.ymin:.1f} to {bb.ymax:.1f} = {bb.ymax-bb.ymin:.1f}mm ({((bb.ymax-bb.ymin)/IN):.2f}\")")
print(f"  Z: {bb.zmin:.1f} to {bb.zmax:.1f} = {bb.zmax-bb.zmin:.1f}mm ({((bb.zmax-bb.zmin)/IN):.2f}\")")

outdir = "/tmp/colo-nas-case-2"
os.makedirs(outdir, exist_ok=True)

stl_path = os.path.join(outdir, "colo_nas_v6.stl")
exporters.export(case, stl_path)
print(f"\nSTL: {stl_path} ({os.path.getsize(stl_path)} bytes)")

step_path = os.path.join(outdir, "colo_nas_v6.step")
exporters.export(case, step_path)
print(f"STEP: {step_path} ({os.path.getsize(step_path)} bytes)")

# GLB
mesh = __import__('trimesh').load(stl_path)
mesh.export(os.path.join(outdir, "colo_nas_v6.glb"))
print(f"GLB: {os.path.getsize(os.path.join(outdir, 'colo_nas_v6.glb'))} bytes")

print("\nDONE")
