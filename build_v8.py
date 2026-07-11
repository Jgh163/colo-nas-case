"""
Colo NAS Enclosure v8 — U-channel + custom drive sleds
ZimaBlade 7700 + 2x 3.5" HDD (on sleds) + PCIe IPMI via riser
7.5" × 7.5" × 2.5" — SendCutSend ready

Layout:
  Left half: 2x 3.5" HDD on custom sheet metal sleds, stacked vertically
  Right half: ZimaBlade 7700 on standoffs, PCIe IPMI flat above via riser

Pieces for SendCutSend:
  1. U-channel body (bottom + left/right walls, tabs, 2 bends)
  2. HDD divider wall (separates HDD bay from ZimaBlade bay, has sled guides)
  3. Front panel (60mm ZimaBlade fan intake + HDD vent)
  4. Rear panel (2x Ethernet, USB-C, DC bulkheads + 60mm exhaust fan)
  5. Top panel (ventilated, screws to walls via tabs)
  6-7. Drive sleds x2 (custom trays for 3.5" drives)
"""

import cadquery as cq
from cadquery import exporters
import os

IN = 25.4
MT = 1.2  # 18 ga

CX = 7.5 * IN   # 190.5
CY = 7.5 * IN   # 190.5
CZ = 2.5 * IN   # 63.5

# HDD
HW = 4.0 * IN    # 101.6
HD = 5.787 * IN  # 147.0
HH = 1.028 * IN  # 26.1
HS = 0.25 * IN   # screw inset from side
HF = 1.75 * IN   # front screw row
HR = 1.625 * IN  # rear screw row from rear = HD - HR

# ZimaBlade 7700
ZW = 80; ZD = 107; ZH = 23
PW = 70; PD = 120; PH = 15  # PCIe IPMI card
ZB_SH = 5  # ZimaBlade standoff height

# Layout positions
HDD_X = 2
HDD_Y = 12  # sled front tab flush with Y=0
GAP = 2  # gap between HDD area and divider wall
ZB_X = HDD_X + HW + GAP + MT  # ZimaBlade starts after HDD + divider wall
ZB_Y = CY - ZD - 8

# Internal wall heights
WALL_H = CZ - MT  # side wall height
DIV_H = CZ - MT   # divider wall height

# Sled dimensions
SLED_W = HW + 2        # sled = drive width + 1mm per side clearance
SLED_D = HD + 8        # sled deeper than drive (front tab + rear clearance)
SLED_MT = MT           # sled material thickness
SLED_FLANGE = 5        # guide flange height
SLED_FRONT_TAB = 12    # front handle tab length

# Layout positions
HDD_X = 2
HDD_Y = 12  # SLED_FRONT_TAB = 12, sled front tab flush with Y=0
GAP = 2  # gap between HDD area and divider wall

FAN_H = 60
FAN_SS = 50
FAN_SO = (FAN_H - FAN_SS) / 2

TAB_H = 15
TAB_PROJ = 8
TAB_LEN = 15

def atc(dx, dy, dz, cx, cy, cz=0):
    return cq.Workplane("XY").box(dx, dy, dz).translate((cx+dx/2, cy+dy/2, cz+dz/2))

# ===================== CASE BODY =====================
body = cq.Workplane("XY")

# Bottom
body = body.union(atc(CX, CY, MT, 0, 0, 0))

# Left wall (X=0..MT, full depth)
body = body.union(atc(MT, CY, WALL_H, 0, 0, MT))

# Right wall (X=CX-MT..CX, full depth)
body = body.union(atc(MT, CY, WALL_H, CX-MT, 0, MT))

# === INTERNAL TABS (for end plates) ===
TAB_Z = MT + (WALL_H - TAB_H) / 2
# Left wall tabs
body = body.union(atc(TAB_PROJ, TAB_LEN, TAB_H, MT, 0, TAB_Z))
body = body.union(atc(TAB_PROJ, TAB_LEN, TAB_H, MT, CY-TAB_LEN, TAB_Z))
# Right wall tabs
body = body.union(atc(TAB_PROJ, TAB_LEN, TAB_H, CX-MT-TAB_PROJ, 0, TAB_Z))
body = body.union(atc(TAB_PROJ, TAB_LEN, TAB_H, CX-MT-TAB_PROJ, CY-TAB_LEN, TAB_Z))

# Screw holes in tabs
for tx in [MT+TAB_PROJ/2, CX-MT-TAB_PROJ/2]:
    for ty in [TAB_LEN/2, CY-TAB_LEN/2]:
        for z_off in [3, TAB_H-3]:
            body = body.cut(atc(3.4, 3.4, TAB_PROJ+2, tx-1.7, ty-1.7, TAB_Z+z_off-1.7))

# === DIVIDER WALL between HDDs and ZimaBlade ===
# Wall at X = HDD_X + HW + GAP, spans from Y=0 to CY
div_x = HDD_X + HW + GAP
body = body.union(atc(MT, CY, DIV_H, div_x, 0, MT))

# === SLED GUIDE RAILS on left wall and divider ===
# Each sled needs guide channels.
# Bottom sled guide: thin shelf at Z=MT+2 (just above bottom panel)
# Top sled guide: thin shelf at Z=~HH+6 (above bottom HDD)
guide_w = 3  # guide rail width
g1_z = MT + 3                          # bottom sled guide Z
g2_z = MT + HH + 6                     # top sled guide Z (above HDD1)

# Guide rails on left wall (inner face)
for gz in [g1_z, g2_z]:
    body = body.union(atc(TAB_PROJ, CY, guide_w, MT, 0, gz))

# Guide rails on divider wall (left face, into HDD bay)
for gz in [g1_z, g2_z]:
    body = body.union(atc(TAB_PROJ, CY, guide_w, div_x - TAB_PROJ, 0, gz))

# === VENT SLOTS (side walls) ===
for vy in range(20, int(CY-20), 25):
    for vz in range(int(MT+20), int(CZ-10), 20):
        body = body.cut(atc(MT+1, 3, 3, -1, vy, vz))
        body = body.cut(atc(MT+1, 3, 3, CX, vy, vz))

# ZimaBlade mount holes
for sx, sy in [(5,5), (5,ZD-5), (ZW-5,5), (ZW-5,ZD-5)]:
    body = body.cut(atc(3.4, 3.4, MT+2, ZB_X+sx, ZB_Y+sy, -1))

# Sled access holes — pass-throughs for SATA/power cables at rear of HDD bay
cable_pass = atc(HW, MT+3, HH-2, HDD_X, CY-1, MT+3)
body = body.cut(cable_pass)


# ===================== FRONT PANEL =====================
front = atc(CX-2*MT, MT, CZ, MT, 0, 0)

# 60mm fan intake for ZimaBlade
fan_zb_x = ZB_X
fan_zb_z = (CZ - FAN_H) / 2
front = front.cut(atc(FAN_H, MT+2, FAN_H, fan_zb_x, MT-1, fan_zb_z))
for fx, fz in [(FAN_SO, FAN_SO), (FAN_SO+FAN_SS, FAN_SO),
               (FAN_SO, FAN_SO+FAN_SS), (FAN_SO+FAN_SS, FAN_SO+FAN_SS)]:
    front = front.cut(atc(4, MT+3, 4, fan_zb_x+fx+FAN_H/2-2, MT-1, fan_zb_z+fz+FAN_H/2-2))

# HDD sled access opening (left side, rectangular opening for sleds to pass through)
front = front.cut(atc(HW+4, MT+2, HH*2+10, HDD_X-2, MT-1, MT+1))

# HDD vent holes above/below sled opening
for vx in range(int(HDD_X+5), int(HDD_X+HW-5), 10):
    for vz_off in [3, CZ-8]:
        front = front.cut(atc(3, MT+3, 3, vx, MT-1, vz_off))

# Mount holes to tabs
for tx in [MT+TAB_PROJ/2, CX-MT-TAB_PROJ/2]:
    for z_off in [3, TAB_H-3]:
        front = front.cut(atc(3.4, 3.4, MT+2, tx-1.7, MT-1, TAB_Z+z_off-1.7))
body = body.union(front)


# ===================== REAR PANEL =====================
rear = atc(CX-2*MT, MT, CZ, MT, CY-MT, 0)

# 60mm exhaust fan (HDD area)
fan_ex_x = HDD_X + HW/2 - FAN_H/2
fan_ex_z = (CZ - FAN_H) / 2
rear = rear.cut(atc(FAN_H, MT+3, FAN_H, fan_ex_x, CY-1, fan_ex_z))
for fx, fz in [(FAN_SO, FAN_SO), (FAN_SO+FAN_SS, FAN_SO),
               (FAN_SO, FAN_SO+FAN_SS), (FAN_SO+FAN_SS, FAN_SO+FAN_SS)]:
    rear = rear.cut(atc(4, MT+4, 4, fan_ex_x+fx+FAN_H/2-2, CY-1, fan_ex_z+fz+FAN_H/2-2))

# Ethernet bulkheads × 2
for i, z_off in enumerate([-12, 12]):
    rear = rear.cut(atc(16, MT+3, 25, 35, CY-1, CZ/2+z_off))

# USB-C bulkhead
rear = rear.cut(atc(13, MT+3, 21, CX-85, CY-1, CZ/2-6))

# DC power jack
rear = rear.cut(atc(10, MT+3, 14, CX-45, CY-1, CZ/2+10))

# Mount holes
for tx in [MT+TAB_PROJ/2, CX-MT-TAB_PROJ/2]:
    for z_off in [3, TAB_H-3]:
        rear = rear.cut(atc(3.4, 3.4, MT+2, tx-1.7, CY-MT, TAB_Z+z_off-1.7))
body = body.union(rear)


# ===================== TOP PANEL =====================
top = atc(CX, CY, MT, 0, 0, CZ-MT)

# Top panel screw holes (into side wall tabs)
for tx in [6, CX-6]:
    for ty in [TAB_LEN/2, CY-TAB_LEN/2]:
        top = top.cut(atc(3.4, 3.4, MT+2, tx-1.7, ty-1.7, CZ-MT-1))

# Vent holes (ZimaBlade side)
for vx in range(int(ZB_X+10), int(CX-15), 20):
    for vy in range(int(ZB_Y+10), int(ZB_Y+ZD-10), 20):
        top = top.cut(atc(3, 3, MT+2, vx, vy, CZ-MT-1))

# Vent holes (HDD side)
for vx in range(int(HDD_X+10), int(HDD_X+HW-10), 25):
    for vy in range(int(HDD_Y+HH+10), int(HDD_Y+HD-10), 25):
        top = top.cut(atc(3, 3, MT+2, vx, vy, CZ-MT-1))

body = body.union(top)


# ===================== DRIVE SLEDS x2 =====================
def build_sled():
    """Drive sled: tray with flanges for one 3.5 HDD"""
    sled = cq.Workplane("XY")
    # Tray base — slightly larger than drive
    sled = sled.union(atc(SLED_W, SLED_D, SLED_MT, 0, 0, 0))
    
    # Side flanges (bend up)
    sled = sled.union(atc(SLED_MT, SLED_D, SLED_FLANGE, 0, 0, SLED_MT))
    sled = sled.union(atc(SLED_MT, SLED_D, SLED_FLANGE, SLED_W-SLED_MT, 0, SLED_MT))
    
    # Front tab (handle)
    sled = sled.union(atc(SLED_W, SLED_FRONT_TAB, SLED_MT, 0, -SLED_FRONT_TAB, 0))
    # Thumbscrew hole in front tab
    sled = sled.cut(atc(5, 5, SLED_MT+2, SLED_W/2-2.5, -SLED_FRONT_TAB, -1))
    
    # Drive mounting holes (6-32 clearance, standard positions)
    for y_off in [HF, HD-HR]:
        for sx in [-1, 1]:
            sx_off = HW/2 + sx * (HW/2 - HS)
            hole_x = 2 + sx_off  # 2mm margin from sled edge
            # But the sled is SLED_W wide and the drive is HW wide
            # Drive is offset by (SLED_W-HW)/2 on each side
            drive_off = (SLED_W - HW) / 2
            hx = drive_off + sx_off
            sled = sled.cut(atc(4, 4, SLED_MT+2, hx-2, y_off-2, -1))
    
    # Ventilation slots (between mounting holes)
    for vy in range(int(HF)+15, int(HD-HR)-15, 15):
        sled = sled.cut(atc(SLED_W-20, 3, SLED_MT+2, 10, float(vy), -1))
    
    # Rear cutout for SATA connector access
    sled = sled.cut(atc(HW/2, 5, SLED_MT+2, (SLED_W-HW/2)/2, SLED_D-5, -1))
    
    return sled

# Sled 1 (bottom slot): Z = g1_z (on top of guide rails)
sled1 = build_sled()
sled1 = sled1.translate((HDD_X, SLED_FRONT_TAB, g1_z))
body = body.union(sled1)

# Sled 2 (top slot): Z = g2_z
sled2 = build_sled()
sled2 = sled2.translate((HDD_X, SLED_FRONT_TAB, g2_z))
body = body.union(sled2)


# ===================== INTERNAL COMPONENTS =====================
# HDD1 on sled1
h1z = g1_z + SLED_MT
hdd1 = atc(HW, HD, HH, HDD_X, HDD_Y, h1z)
hdd1 = hdd1.union(atc(HW, 30, 2, HDD_X, HDD_Y+HD-30, h1z))
hdd1 = hdd1.union(atc(24, 2, 8, HDD_X+HW/2-12, HDD_Y+HD, h1z+HH/2-4))
body = body.union(hdd1)

# HDD2 on sled2
h2z = g2_z + SLED_MT
hdd2 = atc(HW, HD, HH, HDD_X, HDD_Y, h2z)
hdd2 = hdd2.union(atc(HW, 30, 2, HDD_X, HDD_Y+HD-30, h2z))
hdd2 = hdd2.union(atc(24, 2, 8, HDD_X+HW/2-12, HDD_Y+HD, h2z+HH/2-4))
body = body.union(hdd2)

# ZimaBlade
zb = atc(ZW, ZD, ZH, ZB_X, ZB_Y, MT+ZB_SH)
body = body.union(zb)

# IPMI on riser
ipmi = atc(PW, PD, PH, ZB_X+(ZW-PW)/2, ZB_Y+(ZD-PD)/2, MT+ZB_SH+ZH+5)
body = body.union(ipmi)


# ===================== CENTER & EXPORT =====================
body = body.translate((-CX/2, -CY/2, 0))

bb = body.val().BoundingBox()
print(f"BBox: {bb.xmax-bb.xmin:.1f} × {bb.ymax-bb.ymin:.1f} × {bb.zmax-bb.zmin:.1f} mm")
print(f"     = {(bb.xmax-bb.xmin)/IN:.2f} × {(bb.ymax-bb.ymin)/IN:.2f} × {(bb.zmax-bb.zmin)/IN:.2f} in")

outdir = "/tmp/colo-nas-case-2"
os.makedirs(outdir, exist_ok=True)

# Export STL and STEP from CadQuery
stl_path = os.path.join(outdir, "colo_nas_v8.stl")
exporters.export(body, stl_path)
print(f"STL: {os.path.getsize(stl_path)} bytes")

step_path = os.path.join(outdir, "colo_nas_v8.step")
exporters.export(body, step_path)
print(f"STEP: {os.path.getsize(step_path)} bytes")

# Convert STL to GLB
mesh = __import__('trimesh').load(stl_path)
glb_path = os.path.join(outdir, "colo_nas_v8.glb")
mesh.export(glb_path)
print(f"GLB: {os.path.getsize(glb_path)} bytes")

print("\nDONE — v8 with custom drive sleds, divider wall, guide rails, bulkheads, fans")
