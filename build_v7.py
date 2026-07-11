"""
Colo NAS Enclosure v7 — U-channel with tabbed end plates
ZimaBlade 7700 + 2x 3.5" HDD + PCIe IPMI via riser
7.5" × 7.5" × 2.5" — SendCutSend ready flat pattern

Layout: HDDs left, ZimaBlade+IPMI right
Ports: 2x Ethernet bulkhead + USB-C bulkhead on rear panel
Fans: 60mm intake over ZimaBlade, 60mm exhaust over HDDs

Pieces for SendCutSend:
  1. U-channel body (bottom + left wall + right wall, 2 bends)
  2. Front panel (with fan holes)
  3. Rear panel (with bulkhead holes + fan hole)
  4. Top panel (with countersunk HDD holes)
  5. (Optional) Drive sleds if hot-swap desired
"""

import cadquery as cq
from cadquery import exporters
import os

IN = 25.4
MT = 1.2  # 18 ga

# Case external
CX = 7.5 * IN   # 190.5
CY = 7.5 * IN   # 190.5
CZ = 2.5 * IN   # 63.5

# HDD
HW = 4.0 * IN     # 101.6
HD = 5.787 * IN   # 147.0
HH = 1.028 * IN   # 26.1
HS = 0.25 * IN
HF = 1.75 * IN
HR = 1.625 * IN

# ZimaBlade 7700
ZW = 80
ZD = 107
ZH = 23

# PCIe IPMI (via riser)
PW = 70
PD = 120
PH = 15

# Standoffs
ZB_SH = 5  # ZimaBlade standoff height

# Fan sizes
FAN_H = 60  # 60mm fan for both intake and exhaust
FAN_IO_D = 60  # fan hole outer diameter for guard
FAN_SCREW_SPACING = 50  # 60mm fan mounting hole spacing

# Layout positions
HDD_X = 8
HDD_Y = 8
ZB_X = CX - ZW - 10   # right side, ZimaBlade
ZB_Y = CY - ZD - 10   # back
GAP = 3  # gap between HDD area and ZimaBlade area

# Wall height (internal) = CZ - MT
WALL_H = CZ - MT  # 62.3mm

# Tab dimensions
TAB_W = 12   # tab width
TAB_H = 15   # tab height (engagement with end plate)
TAB_D = 8    # tab depth (protrusion from wall edge)

def atc(dx, dy, dz, cx, cy, cz=0):
    return cq.Workplane("XY").box(dx, dy, dz).translate((cx+dx/2, cy+dy/2, cz+dz/2))


# ===================== 1. U-CHANNEL BODY =====================
body = cq.Workplane("XY")

# Bottom panel
body = body.union(atc(CX, CY, MT, 0, 0, 0))

# Left wall (X=0, inside face at X=MT)
body = body.union(atc(MT, CY, WALL_H, 0, 0, MT))

# Right wall (X=CX-MT, inside face at X=CX-2*MT)
body = body.union(atc(MT, CY, WALL_H, CX-MT, 0, MT))

# === INTERNAL TABS on inside of walls (front and back) ===
# Tab dimensions
TAB_PROJ = 8     # how far tab projects from wall inward
TAB_LEN  = 15    # tab length along Y
TAB_ZPOS = MT + (WALL_H - TAB_H) / 2  # center of tab in Z

# Front-left tab (inside of left wall, Y=0 area)
body = body.union(atc(TAB_PROJ, TAB_LEN, TAB_H, MT, 0, TAB_ZPOS))

# Rear-left tab (inside of left wall, Y=CY-TAB_LEN)
body = body.union(atc(TAB_PROJ, TAB_LEN, TAB_H, MT, CY-TAB_LEN, TAB_ZPOS))

# Front-right tab (inside of right wall, Y=0 area)
body = body.union(atc(TAB_PROJ, TAB_LEN, TAB_H, CX-MT-TAB_PROJ, 0, TAB_ZPOS))

# Rear-right tab (inside of right wall, Y=CY-TAB_LEN)
body = body.union(atc(TAB_PROJ, TAB_LEN, TAB_H, CX-MT-TAB_PROJ, CY-TAB_LEN, TAB_ZPOS))

# M3 screw holes in tabs
for tab_x in [MT + TAB_PROJ/2, CX - MT - TAB_PROJ/2]:
    for tab_y in [TAB_LEN/2, CY - TAB_LEN/2]:
        for z_off in [3, TAB_H - 3]:
            hole = atc(3.4, 3.4, TAB_PROJ+2, tab_x - 1.7, tab_y - 1.7, TAB_ZPOS + z_off - 1.7)
            body = body.cut(hole)

# === VENT SLOTS (side walls) ===
for vy in range(20, int(CY-20), 25):
    for vz in range(int(MT+20), int(CZ-10), 20):
        body = body.cut(atc(MT+1, 3, 3, -1, vy, vz))
        body = body.cut(atc(MT+1, 3, 3, CX, vy, vz))

# === ZimaBlade mounting holes (bottom panel) ===
for sx, sy in [(5,5), (5,ZD-5), (ZW-5,5), (ZW-5,ZD-5)]:
    hole = atc(3.4, 3.4, MT+2, ZB_X+sx, ZB_Y+sy, -1)
    body = body.cut(hole)

# === Standoff holes for HDD mounts (bottom panel, left side) ===
for hx in [HDD_X + 10, HDD_X + HW - 10]:
    for hy in [HDD_Y + 10, HDD_Y + HD - 10]:
        hole = atc(3.4, 3.4, MT+2, hx, hy, -1)
        body = body.cut(hole)


# ===================== 2. FRONT PANEL =====================
# Fits between side walls: X from MT to CX-MT, flush at Y=0
front = atc(CX - 2*MT, MT, CZ, MT, 0, 0)

# 60mm fan intake for ZimaBlade area (right side of front panel)
fan_zb_x = ZB_X  # align with ZimaBlade area
fan_zb_z = (CZ - FAN_H) / 2
front = front.cut(atc(FAN_H, MT+2, FAN_H, fan_zb_x, MT-1, fan_zb_z))

# Fan screw holes
fan_scr_off = (FAN_H - FAN_SCREW_SPACING) / 2
for fx, fz in [(fan_scr_off, fan_scr_off),
               (fan_scr_off + FAN_SCREW_SPACING, fan_scr_off),
               (fan_scr_off, fan_scr_off + FAN_SCREW_SPACING),
               (fan_scr_off + FAN_SCREW_SPACING, fan_scr_off + FAN_SCREW_SPACING)]:
    screw = atc(4, MT+3, 4, fan_zb_x + fx + FAN_H/2 - 2, MT-1, fan_zb_z + fz + FAN_H/2 - 2)
    front = front.cut(screw)

# HDD vent area (left side)
for vx in range(int(HDD_X+15), int(HDD_X+HW-15), 15):
    for vz in range(int(15), int(CZ-15), 15):
        front = front.cut(atc(5, MT+3, 5, vx, MT-1, vz))

# M3 screw holes to tabs (front panel, Y=-MT, aligns with tabs at Y=0)
for wall_side in [MT + TAB_PROJ/2, CX - MT - TAB_PROJ/2]:
    for z_off in [3, TAB_H - 3]:
        hole = atc(3.4, 3.4, MT+2, wall_side - 1.7, MT-1, TAB_ZPOS + z_off - 1.7)
        front = front.cut(hole)

body = body.union(front)


# ===================== 3. REAR PANEL =====================
# Fits between side walls: X from MT to CX-MT, at Y=CY-MT
rear = atc(CX - 2*MT, MT, CZ, MT, CY, 0)

# Ethernet 1
eth_x = 35
eth_z = CZ/2 - 12
rear = rear.cut(atc(16, MT+3, 25, eth_x, CY-1, eth_z))

# Ethernet 2
eth2_x = 35
eth2_z = CZ/2 + 12
rear = rear.cut(atc(16, MT+3, 25, eth2_x, CY-1, eth2_z))

# USB-C bulkhead
usbc_x = CX - 85
usbc_z = CZ/2 - 6
rear = rear.cut(atc(13, MT+3, 21, usbc_x, CY-1, usbc_z))

# DC power jack
dc_x = CX - 45
dc_z = CZ/2 + 10
rear = rear.cut(atc(10, MT+3, 14, dc_x, CY-1, dc_z))

# 60mm exhaust fan (left side, HDD area)
fan_ex_x = HDD_X + (HW / 2) - (FAN_H / 2)
fan_ex_z = (CZ - FAN_H) / 2
rear = rear.cut(atc(FAN_H, MT+3, FAN_H, fan_ex_x, CY-1, fan_ex_z))

# Fan screw holes
for fx, fz in [(fan_scr_off, fan_scr_off),
               (fan_scr_off + FAN_SCREW_SPACING, fan_scr_off),
               (fan_scr_off, fan_scr_off + FAN_SCREW_SPACING),
               (fan_scr_off + FAN_SCREW_SPACING, fan_scr_off + FAN_SCREW_SPACING)]:
    screw = atc(4, MT+4, 4, fan_ex_x + fx + FAN_H/2 - 2, CY-1, fan_ex_z + fz + FAN_H/2 - 2)
    rear = rear.cut(screw)

# M3 screw holes to tabs (rear panel, Y=CY-MT, aligns with tabs at Y=CY-TAB_LEN)
for wall_side in [MT + TAB_PROJ/2, CX - MT - TAB_PROJ/2]:
    for z_off in [3, TAB_H - 3]:
        hole = atc(3.4, 3.4, MT+2, wall_side - 1.7, CY-MT, TAB_ZPOS + z_off - 1.7)
        rear = rear.cut(hole)

body = body.union(rear)


# ===================== 4. TOP PANEL =====================
top = atc(CX, CY, MT, 0, 0, CZ-MT)

# HDD mounting holes (left side, for HDD2 suspended from top)
h2x = HDD_X
h2y = HDD_Y
hdd_screw_ys = [HF, HD-HR, 3.0*IN]
for sy in hdd_screw_ys:
    for side in [-1, 1]:
        sx = HW/2 + side * (HW/2 - HS)
        hole = atc(3.6, 3.6, MT+2, h2x+sx, h2y+sy, CZ-MT-1)
        top = top.cut(hole)

# Vent holes (right side, above ZimaBlade/IPMI)
for vx in range(int(ZB_X+15), int(CX-15), 20):
    for vy in range(int(ZB_Y+15), int(ZB_Y+ZD-15), 20):
        top = top.cut(atc(3, 3, MT+2, vx, vy, CZ-MT-1))

# Vent holes (left side, avoiding HDD screws)
for vx in range(int(HDD_X+35), int(HDD_X+HW-35), 25):
    for vy in range(int(HDD_Y+35), int(HDD_Y+HD-35), 25):
        skip = False
        for sy in hdd_screw_ys:
            for side in [-1, 1]:
                sx = HW/2 + side * (HW/2 - HS)
                if abs(vx-(h2x+sx)) < 10 and abs(vy-(h2y+sy)) < 10:
                    skip = True
        if not skip:
            top = top.cut(atc(3, 3, MT+2, vx, vy, CZ-MT-1))

body = body.union(top)


# ===================== INTERNAL COMPONENTS =====================
# (cosmetic, for 3D visualization)
# HDD1 bottom
hdd1_z = MT + 2
hdd1 = atc(HW, HD, HH, HDD_X, HDD_Y, hdd1_z)
hdd1 = hdd1.union(atc(HW, 30, 2, HDD_X, HDD_Y+HD-30, hdd1_z))
hdd1 = hdd1.union(atc(24, 2, 8, HDD_X+HW/2-12, HDD_Y+HD, hdd1_z+HH/2-4))
body = body.union(hdd1)

# HDD2 top
hdd2_z = CZ - MT - HH - 0.5
hdd2 = atc(HW, HD, HH, HDD_X, HDD_Y, hdd2_z)
hdd2 = hdd2.union(atc(HW, 30, 2, HDD_X, HDD_Y+HD-30, hdd2_z+HH-2))
hdd2 = hdd2.union(atc(24, 2, 8, HDD_X+HW/2-12, HDD_Y+HD, hdd2_z+HH/2-4))
body = body.union(hdd2)

# ZimaBlade
zb_z = MT + ZB_SH
zb = atc(ZW, ZD, ZH, ZB_X, ZB_Y, zb_z)
body = body.union(zb)

# IPMI card on riser
ipmi_z = zb_z + ZH + 5
ipmi = atc(PW, PD, PH, ZB_X + (ZW-PW)/2, ZB_Y + (ZD-PD)/2, ipmi_z)
body = body.union(ipmi)


# ===================== CENTER AND EXPORT =====================
body = body.translate((-CX/2, -CY/2, 0))

bb = body.val().BoundingBox()
print(f"Bounding box: {bb.xmax-bb.xmin:.1f} × {bb.ymax-bb.ymin:.1f} × {bb.zmax-bb.zmin:.1f} mm")
print(f"  = {(bb.xmax-bb.xmin)/IN:.2f} × {(bb.ymax-bb.ymin)/IN:.2f} × {(bb.zmax-bb.zmin)/IN:.2f} in")

# Check fans fit
print(f"\nZimaBlade fan: X={fan_zb_x+ZB_X:.0f} Z={fan_zb_z:.0f} (60mm)")
print(f"Exhaust fan: X={fan_ex_x+HDD_X:.0f} Z={fan_ex_z:.0f} (60mm)")

outdir = "/tmp/colo-nas-case-2"
os.makedirs(outdir, exist_ok=True)

# STL
stl_path = os.path.join(outdir, "colo_nas_v7.stl")
exporters.export(body, stl_path)
fs = os.path.getsize(stl_path)
print(f"\nSTL: {stl_path} ({fs} bytes)")

# STEP
step_path = os.path.join(outdir, "colo_nas_v7.step")
exporters.export(body, step_path)
print(f"STEP: {step_path} ({os.path.getsize(step_path)} bytes)")

# GLB
mesh = __import__('trimesh').load(stl_path)
mesh.export(os.path.join(outdir, "colo_nas_v7.glb"))
print(f"GLB: {os.path.getsize(os.path.join(outdir, 'colo_nas_v7.glb'))} bytes")

print("\nDONE — v7 U-channel with tabbed end plates, 60mm fans, Ethernet/USB-C bulkheads")
