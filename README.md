# Colo NAS Case v4 — Folded Sheet Metal Enclosure

**External:** 7.5" × 7.5" × 2.5" (190.5 × 190.5 × 63.5 mm)  
**Material:** 18 ga (1.2mm) or 20 ga (0.9mm) cold rolled steel  
**Layout:** Mini ITX + 2× 3.5" HDD + 1U CPU cooler  

## 3D Models

| Variant | Description | GLB (interactive) | STL |
|---------|------------|-------------------|-----|
| **v4a — Overlap** | Both HDDs top-mounted, overlap in XY (for visualization) | [`colo_nas_v4.glb`](./colo_nas_v4.glb) | [`colo_nas_v4.stl`](./colo_nas_v4.stl) |
| **v4b — Fixed** | HDD1 bottom (right-side up), HDD2 top (upside-down). No overlap. | [`colo_nas_v4b.glb`](./colo_nas_v4b.glb) | [`colo_nas_v4b.stl`](./colo_nas_v4b.stl) |

Drag to rotate, scroll to zoom on the GLB files above.

## Layout

### v4b (recommended build)

```
┌─────────────────────────────────────┐
│  ←——— 7.5" wide ———→               │
│ ┌───────────────────┐               │
│ │ HDD2 (from TOP)   │              │
│ │ front-left area   │   [60mm fan] │
│ │                   │    I/O cutout │
│ │  MB on standoffs  │              │
│ │                   │  ┌──────────┐│
│ │                   │  │ HDD1     ││
│ │                   │  │ (BOTTOM) ││
│ │                   │  └──────────┘│
│ └───────────────────┘              │
└─────────────────────────────────────┘
```

### Z-height stack (v4b)

| Layer | Component | Height |
|-------|-----------|--------|
| Top | 20/18 ga panel | 0.036-0.048" |
| Suspended | HDD2 (upside-down, PCB up) | 1.03" |
| Gap | Airflow / cable routing | ~0.4" |
| Component | CPU cooler (1U) | 0.5" |
| Middle | Motherboard PCB | 0.06" |
| Standoffs | M3 × 10mm hex | 0.4" |
| Bottom | HDD1 (right-side up) | 1.03" |
| Bottom | Metal panel | 0.036-0.048" |
| **Total** | | **~2.5"** |

## ⚠ Important: HDD Fit

Two standard 3.5" HDDs are **4.0" wide each** — they need **8" minimum width** to sit side-by-side.  
At 7.5" width, they overlap in XY.

**Two solutions provided:**

| Variant | Method | Pros | Cons |
|---------|--------|------|------|
| **v4b (recommended)** | HDD1 on bottom, HDD2 from top (different Z levels) | No collision, clean layout | Slightly asymmetrical, one HDD is right-side up |
| **v4a (reference)** | Both from top (overlap shown in 3D) | Symmetrical mounting | **Physically collides** — for visualization only |

**If you want side-by-side no-overlap:** Widen the template to **8.25"** (209.6mm).  
Edit `CaseW` in the SCAD file.

## Fabrication — SendCutSend

The SVG template [`colo_nas_v4_template.svg`](./colo_nas_v4_template.svg) has 4 pieces:

1. **U-channel body** — bottom + front/back walls, one piece with 2× 90° bends
2. **Rear panel** — I/O shield cutout (144×44mm) + 60mm fan hole
3. **Front panel** — ventilated
4. **Top panel** — 6-32 countersunk HDD holes + vents

Upload to SendCutSend as-is. Select:
- **Material:** 18 ga (0.048") or 20 ga (0.036") CRS (cheapest) or Galvanized
- **Bending:** Yes — 2 bends on the U-channel piece  
- **Finish:** None (hand-paint with rattle can) or black powder coat

### Bend Instructions for U-channel body

```
     ┌────  Bend 1 (90° up)  ────┐
     │                            │
  Back Wall                 Bottom Panel
(63.5×190.5mm)           (190.5×190.5mm)
     │                            │
     └────  Bend 2 (90° up)  ────┘
                                    Front Wall
                                   (63.5×190.5mm)
```

Both walls fold 90° in the same direction (upward from bottom).

## Hardware Checklist

| Item | Qty | Spec |
|------|-----|------|
| **HDD mounting screws** | 8-16 | 6-32 × 3/16" or 5/32" flathead countersunk (82°) |
| **Motherboard standoffs** | 4 | M3 × 10mm hex, male-female |
| **MB → standoff screws** | 4 | M3 × 5mm panhead |
| **Standoff → bottom screws** | 4 | M3 × 5mm panhead |
| **60mm fan** | 1 | 60×60×10 or 15mm (Noctua NF-A6x15, etc.) |
| **Fan screws** | 4 | M3 × 10mm self-tapping or 6-32 |
| **Rubber/foam pads** | 8 | For HDD vibration isolation |
| **I/O shield** | 1 | Standard ATX I/O shield (included with motherboard) |

## OpenSCAD

Edit [`colo_nas_v4.scad`](./colo_nas_v4.scad) or [`colo_nas_v4b.scad`](./colo_nas_v4b.scad) to tweak dimensions:

- `CaseW`, `CaseD`, `CaseH` — external dimensions
- `Standoff_H` — motherboard standoff height
- `USE_20GA` — toggle between 18 ga (1.2mm) and 20 ga (0.9mm)

Install [OpenSCAD](https://openscad.org) (free), open the file, and press F5 to preview or F6 to render.

## Files

| File | What |
|------|------|
| `colo_nas_v4.scad` | OpenSCAD: overlapping HDDs (3D view + flat pattern switch) |
| `colo_nas_v4b.scad` | OpenSCAD: fixed layout, no HDD overlap |
| `colo_nas_v4.stl` | STL 3D model (v4a) |
| `colo_nas_v4.glb` | GLB 3D model for interactive viewing (v4a) |
| `colo_nas_v4b.stl` | STL 3D model (v4b — recommended) |
| `colo_nas_v4b.glb` | GLB 3D model for interactive viewing (v4b) |
| `colo_nas_v4_template.svg` | **SendCutSend template** — upload this |
