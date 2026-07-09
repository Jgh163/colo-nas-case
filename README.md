# Colo NAS Case — Folded Sheet Metal Enclosure

**External:** 8" × 3" × 8" (203 × 76 × 203 mm)  
**Material:** 18 ga (1.2mm) steel or aluminum  
**Layout:** Staggered L — 2× 3.5" HDD + Mini ITX

## 🔲 Interactive 3D Model

**[▶ View Interactive 3D Model](https://github.com/Jgh163/colo-nas-case/blob/main/colo_nas_3d.glb)**

> Drag to rotate · Scroll to zoom

## Components

| What | Where |
|---|---|
| **Mini ITX board** | Mounted on 10mm standoffs above both drives |
| **HDD 1** | Front-left (0–4"W × 0–5.8"D) |
| **HDD 2** | Back-right (4–8"W × 2.2–8"D) |
| **CPU cooler** | 1U active heatsink (13mm / 0.5") — must be in rear half of board |
| **PSU** | PicoPSU + external 12V brick (not in case) |
| **KVM** | JetKVM or NanoKVM via HDMI+USB |

## Height Budget

```
1.03" — 2× 3.5" drives on bottom
0.40" — Standoffs  
0.06" — PCB
0.50" — 1U CPU cooler
────────────────
1.99" — Total used
1.01" — Clearance (ventilation gap)
```

## Fabrication

The flat pattern SVG is in [`colo_nas_flat.svg`](./colo_nas_flat.svg) — send to any laser cutting / sheet metal shop.

**Pieces to cut:**
1. **U-channel body** — bottom + 2 side walls (one continuous piece, 3 bends)
2. **Front panel** — with drive ventilation holes
3. **Rear panel** — with I/O cutout and 60mm fan hole
4. **Top panel** — ventilated

Open [`colo_nas_3d.scad`](./colo_nas_3d.scad) in [OpenSCAD](https://openscad.org) (free) to adjust hole positions, vent patterns, or dimensions. Export DXF for the fab shop.

## Files

| File | Description |
|---|---|
| `colo_nas_3d.glb` | 3D model (GLTF/GLB) for GitHub viewer |
| `colo_nas_3d.stl` | 3D model (STL format) |
| `colo_nas_3d.scad` | OpenSCAD source |
| `colo_nas_case_v2.scad` | Combined flat pattern + 3D |
| `colo_nas_flat.svg` | Flat pattern SVG for laser cutter |
| `README.md` | This file |

## Notes

- The CPU must be in the **rear half** of the board (depth 5.8"–8") for the 1U cooler to have clear airflow
- If your board has a front-mounted CPU, swap the drive positions (HDD1 back-right, HDD2 front-left)
- 60mm fan goes on rear panel for exhaust
- Drive vibration: use 3mm rubber grommets on mounting screws
