"""
Colo NAS v9 — Exploded View Generator
Spreads all components along Z axis for assembly visualization
Reuses exact dimensions from v9
"""

import cadquery as cq
from cadquery import exporters
import os, sys

IN = 25.4
MM = 1.22

CX = 7.5*IN; CY = 7.5*IN; CZ = 2.5*IN

HW = 4.0*IN; HD = 5.787*IN; HH = 1.028*IN
HS = 0.25*IN; HF = 1.75*IN; HR = 1.625*IN

ZW = 80; ZD = 107; ZH = 23
JW = 43; JD = 60; JH = 31

HDD_X = 2; HDD_Y = 12; GAP = 2
DIV_X = HDD_X + HW + GAP
ZB_X = DIV_X + MM
ZB_Y = CY - ZD - 8

WALL_H = CZ - MM
SLED_W = HW + 2; SLED_D = HD + 8; SLED_FT = 12; SLED_FL = 5
G1_Z = MM + 3; G2_Z = MM + HH + 6

TAB_H = 15; TAB_P = 8; TAB_L = 15
TAB_Z = MM + (WALL_H - TAB_H) / 2

def atc(dx, dy, dz, cx=0, cy=0, cz=0):
    return cq.Workplane("XY").box(dx, dy, dz).translate((cx+dx/2, cy+dy/2, cz+dz/2))

# Explosion spacing
GAP = 15  # gap between each layer

assy = cq.Workplane("XY")
z = -60  # start Z

# 1. U-channel body (bottom + walls + tabs)
def add_uchannel():
    global z
    b = atc(CX, CY, MM, 0, 0, z)
    b = b.union(atc(MM, CY, WALL_H, 0, 0, z+MM))
    b = b.union(atc(MM, CY, WALL_H, CX-MM, 0, z+MM))
    for tx in [MM, CX-MM-TAB_P]:
        for ty in [0, CY-TAB_L]:
            b = b.union(atc(TAB_P, TAB_L, TAB_H, tx, ty, z+TAB_Z))
    z += WALL_H + GAP
    return b

assy = assy.union(add_uchannel())

# 2. Divider wall
def add_divider():
    global z
    d = atc(MM, CY, WALL_H, DIV_X, 0, z)
    for gz in [G1_Z, G2_Z]:
        d = d.union(atc(TAB_P, CY, 3, DIV_X-TAB_P, 0, z+gz-G1_Z+MM+3))
    z += WALL_H + GAP
    return d

assy = assy.union(add_divider())

# 3. Front panel
def add_front():
    global z
    fp = atc(CX-2*MM, MM, CZ, MM, 0, z)
    z += CZ + GAP
    return fp

assy = assy.union(add_front())

# 4. Rear panel
def add_rear():
    global z
    rp = atc(CX-2*MM, MM, CZ, MM, CY-MM, z)
    z += CZ + GAP
    return rp

assy = assy.union(add_rear())

# 5. Top panel
def add_top():
    global z
    tp = atc(CX, CY, MM, 0, 0, z)
    z += MM + GAP
    return tp

assy = assy.union(add_top())

# 6. Sled 1 + HDD1
def add_sled1():
    global z
    s = atc(SLED_W, SLED_D, MM, HDD_X, SLED_FT, z)
    s = s.union(atc(MM, SLED_D, SLED_FL, HDD_X, SLED_FT, z+MM))
    s = s.union(atc(MM, SLED_D, SLED_FL, HDD_X+SLED_W-MM, SLED_FT, z+MM))
    s = s.union(atc(SLED_W, SLED_FT, MM, HDD_X, 0, z))
    s = s.union(atc(HW, HD, HH, HDD_X, HDD_Y, z+MM))
    z += HH + MM + GAP + 5
    return s

assy = assy.union(add_sled1())

# 7. Sled 2 + HDD2
def add_sled2():
    global z
    s = atc(SLED_W, SLED_D, MM, HDD_X, SLED_FT, z)
    s = s.union(atc(MM, SLED_D, SLED_FL, HDD_X, SLED_FT, z+MM))
    s = s.union(atc(MM, SLED_D, SLED_FL, HDD_X+SLED_W-MM, SLED_FT, z+MM))
    s = s.union(atc(SLED_W, SLED_FT, MM, HDD_X, 0, z))
    s = s.union(atc(HW, HD, HH, HDD_X, HDD_Y, z+MM))
    z += HH + MM + GAP + 5
    return s

assy = assy.union(add_sled2())

# 8. ZimaBlade
def add_zima():
    global z
    b = atc(ZW, ZD, ZH, ZB_X, ZB_Y, z)
    z += ZH + GAP
    return b

assy = assy.union(add_zima())

# 9. JetKVM
def add_jet():
    global z
    jk_x = ZB_X + (ZW - JW) / 2
    jk_y = CY - ZD - JD - 15
    j = atc(JW, JD, JH, jk_x, jk_y, z)
    z += JH + GAP
    return j

assy = assy.union(add_jet())

# Center and export
assy = assy.translate((-CX/2, -CY/2, 0))

bb = assy.val().BoundingBox()
print(f"BBox: {bb.xmax-bb.xmin:.0f} × {bb.ymax-bb.ymin:.0f} × {bb.zmax-bb.zmin:.0f} mm")

outdir = "/tmp/colo-nas-case-2"
os.makedirs(outdir, exist_ok=True)

stl = os.path.join(outdir, "colo_nas_v9_exploded.stl")
exporters.export(assy, stl)
print(f"STL: {os.path.getsize(stl)} bytes")

step = os.path.join(outdir, "colo_nas_v9_exploded.step")
exporters.export(assy, step)
print(f"STEP: {os.path.getsize(step)} bytes")

mesh = __import__('trimesh').load(stl)
glb = os.path.join(outdir, "colo_nas_v9_exploded.glb")
mesh.export(glb)
print(f"GLB: {os.path.getsize(glb)} bytes")

print("\nDONE — exploded view")
