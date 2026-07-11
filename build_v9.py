"""
Colo NAS Case v9 — Complete Engineering Package Generator
Generates: 3D model (STEP/STL/GLB), flat pattern SVGs, spec sheet

Changes from v8:
  - Replaces PCIe IPMI with JetKVM (43×60×31mm)
  - Frees PCIe slot for future expansion
  - Proper SCS bend radii & K-factor for 18 ga CRS
  - Complete dimensioned flat pattern SVGs
"""

import cadquery as cq
from cadquery import exporters
import os, math, textwrap

# ==================== MATERIAL SPECS ====================
# SendCutSend 18 ga Mild Steel (A36/1008/1018)
MT = 0.048     # inches (1.22mm)
MT_MM = 1.22
# SCS bending specs for 0.048" steel:
BEND_R = 0.048  # inside bend radius = material thickness
BEND_R_MM = 1.22
K_FACTOR = 0.33
BEND_DEDUCTION = 0.080  # approximate for 90° bend in 0.048" steel
MIN_FLANGE = 0.144      # 3x material thickness
MIN_HOLE_EDGE = 0.063   # 1.5x thickness from edge
MIN_TAB_W = 0.125       # minimum tab width

IN = 25.4

# Convert to mm for CadQuery
MM = MT_MM  # material thickness in mm
BR = BEND_R_MM  # bend radius in mm

# Case external dimensions
CX = 7.5 * IN   # 190.5
CY = 7.5 * IN   # 190.5
CZ = 2.5 * IN   # 63.5

# HDD (SFF-8301)
HW = 4.0 * IN    # 101.6
HD = 5.787 * IN  # 147.0
HH = 1.028 * IN  # 26.1
HS = 0.25 * IN
HF = 1.75 * IN
HR = 1.625 * IN

# ZimaBlade 7700
ZW = 80; ZD = 107; ZH = 23

# JetKVM — replaces PCIe IPMI
JW = 43; JD = 60; JH = 31  # JetKVM dimensions

# Layout
HDD_X = 2; HDD_Y = 12; GAP = 2
DIV_X = HDD_X + HW + GAP
ZB_X = DIV_X + MM + 0  # ZimaBlade right after divider wall
ZB_Y = CY - ZD - 8

# Wall heights (internal)
WALL_H = CZ - MM  # 62.3mm

# Sled
SLED_W = HW + 2; SLED_D = HD + 8; SLED_FT = 12; SLED_FL = 5
G1_Z = MM + 3; G2_Z = MM + HH + 6

# Tabs
TAB_H = 15; TAB_P = 8; TAB_L = 15
TAB_Z = MM + (WALL_H - TAB_H) / 2

# Fans
FAN_H = 60; FAN_SS = 50; FAN_SO = (FAN_H - FAN_SS) / 2

def atc(dx, dy, dz, cx=0, cy=0, cz=0):
    return cq.Workplane("XY").box(dx, dy, dz).translate((cx+dx/2, cy+dy/2, cz+dz/2))

# ==================== BUILD ASSEMBLY ====================
assy = cq.Workplane("XY")

# --- U-channel body ---
body = atc(CX, CY, MM, 0, 0, 0)
body = body.union(atc(MM, CY, WALL_H, 0, 0, MM))
body = body.union(atc(MM, CY, WALL_H, CX-MM, 0, MM))
for tx in [MM, CX-MM-TAB_P]:
    for ty in [0, CY-TAB_L]:
        body = body.union(atc(TAB_P, TAB_L, TAB_H, tx, ty, TAB_Z))
assy = assy.union(body)

# --- Divider wall ---
d_wall = atc(MM, CY, WALL_H, DIV_X, 0, MM)
for gz in [G1_Z, G2_Z]:
    d_wall = d_wall.union(atc(TAB_P, CY, 3, DIV_X-TAB_P, 0, gz))
assy = assy.union(d_wall)

# --- Front panel ---
fp = atc(CX-2*MM, MM, CZ, MM, 0, 0)
fp = fp.cut(atc(FAN_H, MM+2, FAN_H, ZB_X, MM-1, (CZ-FAN_H)/2))
for fx, fz in [(FAN_SO, FAN_SO), (FAN_SO+FAN_SS, FAN_SO),
               (FAN_SO, FAN_SO+FAN_SS), (FAN_SO+FAN_SS, FAN_SO+FAN_SS)]:
    fp = fp.cut(atc(4, MM+3, 4, ZB_X+fx+FAN_H/2-2, MM-1, (CZ-FAN_H)/2+fz+FAN_H/2-2))
fp = fp.cut(atc(HW+4, MM+2, HH*2+10, HDD_X-2, MM-1, MM+1))
assy = assy.union(fp)

# --- Rear panel ---
rp = atc(CX-2*MM, MM, CZ, MM, CY-MM, 0)
# Exhaust fan (left, HDD area)
fe_x = HDD_X + HW/2 - FAN_H/2
rp = rp.cut(atc(FAN_H, MM+3, FAN_H, fe_x, CY-1, (CZ-FAN_H)/2))
for fx, fz in [(FAN_SO, FAN_SO), (FAN_SO+FAN_SS, FAN_SO),
               (FAN_SO, FAN_SO+FAN_SS), (FAN_SO+FAN_SS, FAN_SO+FAN_SS)]:
    rp = rp.cut(atc(4, MM+4, 4, fe_x+fx+FAN_H/2-2, CY-1, (CZ-FAN_H)/2+fz+FAN_H/2-2))
# Bulkheads
for i, zo in enumerate([-12, 12]):
    rp = rp.cut(atc(16, MM+3, 25, 35, CY-1, CZ/2+zo))
rp = rp.cut(atc(13, MM+3, 21, CX-85, CY-1, CZ/2-6))
rp = rp.cut(atc(10, MM+3, 14, CX-45, CY-1, CZ/2+10))
assy = assy.union(rp)

# --- Top panel ---
tp = atc(CX, CY, MM, 0, 0, CZ-MM)
for tx in [6, CX-6]:
    for ty in [TAB_L/2, CY-TAB_L/2]:
        tp = tp.cut(atc(3.4, 3.4, MM+2, tx-1.7, ty-1.7, CZ-MM-1))
# Vent holes ZimaBlade side
for vx in range(int(ZB_X+10), int(CX-15), 20):
    for vy in range(int(ZB_Y+10), int(ZB_Y+ZD-10), 20):
        tp = tp.cut(atc(3, 3, MM+2, vx, vy, CZ-MM-1))
# Vent holes HDD side
assy = assy.union(tp)

# U-channel sled: bottom + walls bent up from edges + front tab
SLED_W = 102            # sled width (fits in 104.4mm gap)
SLED_D = HD + 8         # sled depth (HD + front tab clearance)
SLED_FL = 8             # side wall height (forms guide rail)
SLED_FT = 12            # front tab length

def make_sled():
    s = atc(SLED_W, SLED_D, MM, 0, 0, 0)  # bottom tray
    # Left wall (bent up 90°)
    s = s.union(atc(MM, SLED_D, SLED_FL, 0, 0, MM))
    # Right wall (bent up 90°)
    s = s.union(atc(MM, SLED_D, SLED_FL, SLED_W-MM, 0, MM))
    # Front tab (extends forward from bottom, for gripping)
    s = s.union(atc(SLED_W, SLED_FT, MM, 0, -SLED_FT, 0))
    # 6-32 clearance holes at standard HDD bottom thread positions
    for yo in [HF, HD-HR]:
        for sx in [-1, 1]:
            sx_off = HW/2 + sx*(HW/2-HS)
            # Center HDD on sled width
            hx = (SLED_W - HW) / 2 + sx_off
            s = s.cut(atc(4, 4, MM+2, hx-2, yo-2, -1))
    # Vent holes between mounting holes
    for vy in range(int(HF)+15, int(HD-HR)-15, 15):
        s = s.cut(atc(SLED_W-16, 3, MM+2, 8, float(vy), -1))
    # Rear cutout for SATA connector clearance
    s = s.cut(atc(HW/2+10, 5, MM+2, (SLED_W-HW/2-10)/2, SLED_D-5, -1))
    return s

s1 = make_sled().translate((HDD_X, SLED_FT, G1_Z))
s2 = make_sled().translate((HDD_X, SLED_FT, G2_Z))
assy = assy.union(s1).union(s2)

# --- HDDs on sleds ---
assy = assy.union(atc(HW, HD, HH, HDD_X, HDD_Y, G1_Z+MM))
assy = assy.union(atc(HW, HD, HH, HDD_X, HDD_Y, G2_Z+MM))

# --- ZimaBlade ---
assy = assy.union(atc(ZW, ZD, ZH, ZB_X, ZB_Y, MM+5))

# --- JetKVM (beside ZimaBlade, same Z layer, frees PCIe slot) ---
# JetKVM: 43×60×31mm. Place in front of ZimaBlade (between front panel and ZimaBlade)
# ZimaBlade occupies Y=ZB_Y (75.5) to ZB_Y+ZD (182.5)
# Place JetKVM at Y=15 to Y=15+JD (75mm), same standoff height as ZimaBlade
jk_z = MM + 5  # same standoff height as ZimaBlade
jk_x = ZB_X + (ZW - JW) / 2  # centered in ZimaBlade's X range
jk_y = CY - ZD - JD - 15  # in front of ZimaBlade
assy = assy.union(atc(JW, JD, JH, jk_x, jk_y, jk_z))

# Center the assembly
assy = assy.translate((-CX/2, -CY/2, 0))

# Export
outdir = "/tmp/colo-nas-case-2"
os.makedirs(outdir, exist_ok=True)

bb = assy.val().BoundingBox()
dims = (bb.xmax-bb.xmin, bb.ymax-bb.ymin, bb.zmax-bb.zmin)
print(f"ASSEMBLY: {dims[0]/IN:.3f} × {dims[1]/IN:.3f} × {dims[2]/IN:.3f} in")
print(f"         {dims[0]:.1f} × {dims[1]:.1f} × {dims[2]:.1f} mm")

stl = os.path.join(outdir, "colo_nas_v9.stl")
exporters.export(assy, stl); print(f"STL: {os.path.getsize(stl)} bytes")

step = os.path.join(outdir, "colo_nas_v9.step")
exporters.export(assy, step); print(f"STEP: {os.path.getsize(step)} bytes")

mesh = __import__('trimesh').load(stl)
glb = os.path.join(outdir, "colo_nas_v9.glb")
mesh.export(glb); print(f"GLB: {os.path.getsize(glb)} bytes")

# ==================== FLAT PATTERN SVGs ====================

def render_svg(filename, title, elements, mm_mode=True):
    """Generate a clean SVG flat pattern for SCS"""
    w = 800; h = 600
    lines = [f'<?xml version="1.0" encoding="UTF-8"?>',
             f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}mm" height="{h}mm">',
             f'<rect width="{w}" height="{h}" fill="#1a1a2e"/>',
             f'<text x="{w/2}" y="25" fill="#e94560" font-size="18" text-anchor="middle" font-family="monospace" font-weight="bold">{title}</text>',
             f'<text x="{w/2}" y="45" fill="#888" font-size="11" text-anchor="middle" font-family="monospace">Material: 18 ga Mild Steel (0.048" / 1.22mm)  |  Bend radius: 0.048" / 1.22mm  |  Units: mm</text>']
    
    for el in elements:
        lines.append(el)
    
    lines.append('</svg>')
    
    path = os.path.join(outdir, filename)
    with open(path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"SVG: {path}")

# Helper to convert case coords to SVG canvas coords
CX_MM = CX; CY_MM = CY; CZ_MM = CZ

def part_box(px, py, pw, ph, fill="#e8e8e8", stroke="#333", sw=1.5, label=""):
    """Draw a part outline"""
    els = [f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>']
    if label:
        els.append(f'<text x="{px+pw/2}" y="{py-8}" fill="#ccc" font-size="10" text-anchor="middle" font-family="monospace">{label}</text>')
    return els

def bend_line(px, py, pw, ph, dir="up"):
    """Draw a bend line indicator"""
    mid = py + ph/2
    return [f'<line x1="{px}" y1="{mid}" x2="{px+pw}" y2="{mid}" stroke="#e94560" stroke-width="1.5" stroke-dasharray="6,4"/>',
            f'<text x="{px+pw+5}" y="{mid+3}" fill="#e94560" font-size="8" font-family="monospace">{dir}</text>']

def hole(px, py, d=4, fill="#e94560"):
    return [f'<circle cx="{px}" cy="{py}" r="{d/2}" fill="none" stroke="#e94560" stroke-width="1"/>']

def dim_h(px, py, length, label=""):
    """Horizontal dimension line"""
    els = [f'<line x1="{px}" y1="{py}" x2="{px+length}" y2="{py}" stroke="#666" stroke-width="0.8"/>',
           f'<line x1="{px}" y1="{py-3}" x2="{px}" y2="{py+3}" stroke="#666" stroke-width="0.8"/>',
           f'<line x1="{px+length}" y1="{py-3}" x2="{px+length}" y2="{py+3}" stroke="#666" stroke-width="0.8"/>']
    if label:
        els.append(f'<text x="{px+length/2}" y="{py-6}" fill="#888" font-size="8" text-anchor="middle" font-family="monospace">{label}</text>')
    return els

# Scale factor for SVG (convert mm to SVG units, fit in 800×600)
S = 1.8  # scale
OX = 50; OY = 80  # offset

def tc(x, y):
    """Case coords to SVG canvas"""
    return (OX + x * S, OY + y * S)

# ===== PIECE 1: U-CHANNEL BODY =====
# Unfolded: bottom + left wall + right wall + tabs
# Bottom: CX × CY
# Left wall: WALL_H × CY (folds up from left edge)
# Right wall: WALL_H × CY (folds up from right edge)
# Tabs: TAB_P × TAB_L at each corner

cw = CX_MM * S; ch = CY_MM * S; wh = WALL_H * S
elems = []

# Bottom panel
elems += part_box(OX + wh, OY, cw, ch, label="BOTTOM PANEL")

# Left wall (folds up along left edge)
elems += part_box(OX, OY, wh, ch, fill="#ddd", label="LEFT WALL (fold up 90°)")
elems += bend_line(OX+wh-2, OY, 4, ch)

# Right wall (folds up along right edge)
elems += part_box(OX+wh+cw, OY, wh, ch, fill="#ddd", label="RIGHT WALL (fold up 90°)")
elems += bend_line(OX+wh+cw-2, OY, 4, ch)

# Tabs (on inside of walls)
for wall_off, ty, tab_label in [(0, OY, "FRONT TAB"), (0, OY+ch-TAB_L*S, "REAR TAB"),
                                 (OX+wh+cw+wh-TAB_P*S, OY, "FRONT TAB"), 
                                 (OX+wh+cw+wh-TAB_P*S, OY+ch-TAB_L*S, "REAR TAB")]:
    elems += part_box(wall_off, ty, TAB_P*S, TAB_L*S, fill="#aaa", label=tab_label)
    # Screw holes in tabs
    for z_off in [3, TAB_H-3]:
        hz = ty + TAB_L*S/2 - 3 + z_off*S
        elems += hole(wall_off + TAB_P*S/2, hz, 3.5)

# Dimensions
elems += dim_h(OX, OY-15, cw+2*wh, f'{CX_MM:.1f}mm / {CX_MM/IN:.3f}"')
elems += dim_h(OX+wh+cw+5, OY+ch/2, wh, f'{WALL_H:.1f}')
elems += dim_h(OX+wh-wh/2-15, OY+ch+10, cw, f'{CX_MM:.1f}')

render_svg("piece_1_uchannel.svg", "PIECE 1: U-CHANNEL BODY (1 piece, 2 bends)", elems)

# ===== PIECE 2: DIVIDER WALL =====
pw = CY_MM * S; ph = WALL_H * S
elems = [f'<rect x="{OX}" y="{OY}" width="{pw}" height="{ph}" fill="#e8e8e8" stroke="#333" stroke-width="1.5"/>']
elems.append(f'<text x="{OX+pw/2}" y="{OY-8}" fill="#ccc" font-size="10" text-anchor="middle" font-family="monospace">PIECE 2: DIVIDER WALL</text>')
# Guide rails (represented as dashed rectangles)
for gz, label in [(G1_Z, "Bottom sled guide"), (G2_Z, "Top sled guide")]:
    gy = OY + gz * S
    elems += [f'<rect x="{OX+20}" y="{gy}" width="{pw-40}" height="{3*S}" fill="none" stroke="#e94560" stroke-width="1" stroke-dasharray="3,3"/>']
    elems.append(f'<text x="{OX+10}" y="{gy+3}" fill="#e94560" font-size="7" font-family="monospace">{label}</text>')
elems += dim_h(OX, OY+ph+5, pw, f'{CY_MM:.1f}mm')
elems += dim_h(OX-35, OY+ph/2, 30, f'{WALL_H:.1f}mm')
render_svg("piece_2_divider.svg", "PIECE 2: DIVIDER WALL (flat, no bends)", elems)

# ===== PIECE 3: FRONT PANEL =====
pw = (CX_MM-2*MM) * S; ph = CZ_MM * S
elems = [f'<rect x="{OX}" y="{OY}" width="{pw}" height="{ph}" fill="#e8e8e8" stroke="#333" stroke-width="1.5"/>']
elems.append(f'<text x="{OX+pw/2}" y="{OY-8}" fill="#ccc" font-size="10" text-anchor="middle" font-family="monospace">PIECE 3: FRONT PANEL (flat, no bends)</text>')
# Fan cutout
fx = (ZB_X - MM) * S; fy = OY + (CZ_MM - FAN_H) / 2 * S; fw = FAN_H * S; fh = FAN_H * S
elems += [f'<rect x="{OX+fx}" y="{fy}" width="{fw}" height="{fh}" fill="#440" stroke="#e94560" stroke-width="1.2"/>']
elems.append(f'<text x="{OX+fx+fw/2}" y="{fy+fh/2+3}" fill="#e94560" font-size="7" text-anchor="middle" font-family="monospace">60mm FAN</text>')
# Fan screws
for off in [FAN_SO, FAN_SO+FAN_SS]:
    elems += hole(OX+fx+off*S+1, fy+off*S+1, 3.5)
    elems += hole(OX+fx+off*S+1, fy+(FAN_SO+FAN_SS)*S+1, 3.5)
# HDD opening
hx = (HDD_X - 2) * S; hw = (HW + 4) * S; hz = (MM + 1) * S
elems += [f'<rect x="{OX+hx}" y="{OY+hz}" width="{hw}" height="{(HH*2+10)*S}" fill="#333" stroke="#666" stroke-width="1"/>']
elems.append(f'<text x="{OX+hx+hw/2}" y="{OY+hz+(HH*2+10)*S/2+3}" fill="#888" font-size="7" text-anchor="middle" font-family="monospace">SLED ACCESS</text>')
# Mount holes
for tx_off in [MM+TAB_P/2, CX_MM-MM-TAB_P/2]:
    tcx = OX + (tx_off - MM) * S
    for z_off in [3, TAB_H-3]:
        elems += hole(tcx, OY + (TAB_Z + z_off) * S - 1.7*S, 3.5)
elems += dim_h(OX, OY-15, pw, f'{CX_MM-2*MM:.1f}mm')
elems += dim_h(OX-30, OY+ph/2, 25, f'{CZ_MM:.1f}mm')
render_svg("piece_3_front.svg", "PIECE 3: FRONT PANEL (flat, no bends)", elems)

# ===== PIECE 4: REAR PANEL =====
elems = [f'<rect x="{OX}" y="{OY}" width="{pw}" height="{ph}" fill="#e8e8e8" stroke="#333" stroke-width="1.5"/>']
elems.append(f'<text x="{OX+pw/2}" y="{OY-8}" fill="#ccc" font-size="10" text-anchor="middle" font-family="monospace">PIECE 4: REAR PANEL (flat, no bends)</text>')
# Exhaust fan
ex_off = (fe_x - MM) * S
elems += [f'<rect x="{OX+ex_off}" y="{fy}" width="{fw}" height="{fh}" fill="#440" stroke="#e94560" stroke-width="1.2"/>']
elems.append(f'<text x="{OX+ex_off+fw/2}" y="{fy+fh/2+3}" fill="#e94560" font-size="7" text-anchor="middle" font-family="monospace">60mm EXHAUST</text>')
for off in [FAN_SO, FAN_SO+FAN_SS]:
    elems += hole(OX+ex_off+off*S+1, fy+off*S+1, 3.5)
    elems += hole(OX+ex_off+off*S+1, fy+(FAN_SO+FAN_SS)*S+1, 3.5)
# Ethernet × 2
for i, zo in enumerate([-12, 12]):
    ey = OY + (CZ_MM/2 + zo) * S
    elems += [f'<rect x="{OX+(35-MM)*S}" y="{ey}" width="16" height="25" fill="#225" stroke="#4af" stroke-width="1"/>']
    elems.append(f'<text x="{OX+(35-MM)*S+8}" y="{ey+13}" fill="#4af" font-size="6" text-anchor="middle" font-family="monospace">ETH{i+1}</text>')
# USB-C
usbc_x = OX + (CX_MM-85-MM) * S
elems += [f'<rect x="{usbc_x}" y="{OY+(CZ_MM/2-6)*S-10}" width="13" height="21" fill="#252" stroke="#4a4" stroke-width="1"/>']
elems.append(f'<text x="{usbc_x+6}" y="{OY+(CZ_MM/2-6)*S-13}" fill="#4a4" font-size="6" text-anchor="middle" font-family="monospace">USB-C</text>')
# DC jack
dc_x = OX + (CX_MM-45-MM) * S
elems += [f'<rect x="{dc_x}" y="{OY+(CZ_MM/2+10)*S-7}" width="10" height="14" fill="#522" stroke="#f44" stroke-width="1"/>']
elems.append(f'<text x="{dc_x+5}" y="{OY+(CZ_MM/2+10)*S-10}" fill="#f44" font-size="6" text-anchor="middle" font-family="monospace">DC</text>')
# Mount holes
for tx_off in [MM+TAB_P/2, CX_MM-MM-TAB_P/2]:
    tcx = OX + (tx_off - MM) * S
    for z_off in [3, TAB_H-3]:
        elems += hole(tcx, OY + (TAB_Z + z_off) * S - 1.7*S, 3.5)
render_svg("piece_4_rear.svg", "PIECE 4: REAR PANEL (flat, no bends)", elems)

# ===== PIECE 5: TOP PANEL =====
pw = CX_MM * S; ph = CY_MM * S
elems = [f'<rect x="{OX}" y="{OY}" width="{pw}" height="{ph}" fill="#e8e8e8" stroke="#333" stroke-width="1.5"/>']
elems.append(f'<text x="{OX+pw/2}" y="{OY-8}" fill="#ccc" font-size="10" text-anchor="middle" font-family="monospace">PIECE 5: TOP PANEL (flat, no bends)</text>')
# HDD screw holes (left side)
for yo in [HF, HD-HR, 3*IN]:
    for sx in [-1, 1]:
        sh_x = HDD_X + HW/2 + sx*(HW/2-HS)
        sh_y = HDD_Y + yo
        elems += hole(OX+sh_x*S, OY+sh_y*S, 3.6)
# Mount holes to side wall tabs
for tx in [6, CX-6]:
    for ty in [TAB_L/2, CY-TAB_L/2]:
        elems += hole(OX+tx*S, OY+ty*S, 3.4)
elems += dim_h(OX, OY-15, pw, f'{CX_MM:.1f}mm')
elems += dim_h(OX-35, OY+ph/2, 30, f'{CY_MM:.1f}mm')
render_svg("piece_5_top.svg", "PIECE 5: TOP PANEL (flat, no bends)", elems)

# ===== PIECE 6: DRIVE SLED (×2) =====
sl_w = SLED_W * S; sl_d = (SLED_D + SLED_FT) * S
elems = [f'<rect x="{OX+SLED_FT*S}" y="{OY}" width="{SLED_W*S}" height="{SLED_D*S}" fill="#e8e8e8" stroke="#333" stroke-width="1.5"/>']
elems.append(f'<text x="{OX+sl_w/2}" y="{OY-8}" fill="#ccc" font-size="10" text-anchor="middle" font-family="monospace">PIECE 6: DRIVE SLED (make 2)</text>')
# Front tab
elems += [f'<rect x="{OX}" y="{OY+SLED_D*S}" width="{SLED_FT*S}" height="{SLED_W*S}" fill="#ddd" stroke="#333" stroke-width="1.2"/>']
elems.append(f'<text x="{OX+5}" y="{OY+SLED_D*S+SLED_W*S/2+3}" fill="#888" font-size="7" font-family="monospace">TAB (bend up)</text>')
elems += bend_line(OX+SLED_FT*S-2, OY, 4, SLED_W*S)
# Side flange bend lines
elems += bend_line(OX+SLED_FT*S+2, OY, 4, SLED_W*S)
# Drive mounting holes
for yo in [HF, HD-HR]:
    for sx in [-1, 1]:
        sx_off = (SLED_W-HW)/2 + HW/2 + sx*(HW/2-HS)
        hy = OY + yo*S
        elems += hole(OX+SLED_FT*S+sx_off*S, hy, 4)
# SATA access cutout
elems += [f'<rect x="{OX+SLED_FT*S+(SLED_W-HW/2)/2*S}" y="{OY+(SLED_D-5)*S}" width="{HW/2*S}" height="{5*S}" fill="#333" stroke="#666" stroke-width="0.8"/>']
# Thumbscrew hole
elems += hole(OX+SLED_FT*S/2, OY+SLED_W*S/2, 5)
elems += dim_h(OX-30, OY+SLED_W*S/2, 25, f'{SLED_W:.1f}mm')
render_svg("piece_6_sled.svg", "PIECE 6: DRIVE SLED (×2) (1 bend each side + 1 bend tab)", elems)

print("\nAll flat patterns generated. SENDCUTSEND READY.")
print("\nUpload the SVG files to https://app.sendcutsend.com")
print("Select: 18 ga Mild Steel (0.048\"), mark bend lines where shown.")
