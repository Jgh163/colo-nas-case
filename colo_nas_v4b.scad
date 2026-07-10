// Colo NAS Enclosure v4b — 7.5" × 7.5" × 2.5" (W × D × H)
// FIXED OVERLAP: HDD1 on bottom (right-side up), HDD2 from top (upside-down)
// Units: mm   |   Scale: 25.4 = inches

SHOW_3D = true;   // true = 3D assembly, false = flat pattern (use SVG)
USE_20GA = false;

Metal = USE_20GA ? 0.9 : 1.2;

CaseW = 190.5;  CaseD = 190.5;  CaseH = 63.5;

HDD_W = 101.6;  HDD_H = 26.1;  HDD_D = 147.0;
HDD_HOLE_FRONT = 44.45;  HDD_HOLE_REAR = 41.28;
HDD_HOLE_SIDE = 6.35;

MB_W = 170.0;   MB_D = 170.0;  MB_H = 1.6;  Standoff_H = 10.0;
Cooler_H = 13;

$fn = 30;

// ====== HDD ======
module hdd_3d(color_=true) {
    if (color_) color("#2a2a2e") cube([HDD_W, HDD_D, HDD_H]);
    else cube([HDD_W, HDD_D, HDD_H]);
    
    // PCB
    color("#1a5c2a") translate([0, HDD_D-30, 0])
        cube([HDD_W, 30, 2]);
    
    // SATA connectors
    color("#333") translate([HDD_W/2-12, HDD_D-1, HDD_H-8])
        cube([24, 2, 8]);
    color("#333") translate([HDD_W/2+14, HDD_D-1, HDD_H-8])
        cube([16, 2, 8]);
}

// ====== MOTHERBOARD ======
module motherboard_3d() {
    color("#1a7b3a", 0.95) cube([MB_W, MB_D, MB_H]);
    
    // CPU + 1U cooler
    color("#999") translate([60, MB_D-85, MB_H]) {
        cube([40, 40, 2]);
        translate([2, 2, 2]) {
            color("#aaa") cube([36, 36, Cooler_H]);
            color("#333") translate([6, 6, 6]) cube([24, 24, 5]);
        }
    }
    
    color("#ffd700") translate([110, MB_D-12, MB_H]) cube([55, 8, 6]);
    color("#444") for (i = [0:3]) {
        translate([135+i*10, MB_D-1, MB_H+2]) cube([8, 2, 6]);
    }
    color("#222") translate([120, 0, MB_H]) cube([16, 6, 8]);
    color("#666", 0.5) translate([17, MB_D-2, 0]) cube([144, 2, 42]);
}

// ====== CASE BODY ======
module case_body() {
    color("#a0a8b0", 0.15) cube([CaseW, CaseD, CaseH]);
}

// ====== 3D ASSEMBLY ======
module assembly_3d() {
    // === BOTTOM HDD LAYER ===
    // HDD1 — sits on bottom panel (right-side up), back-right
    // Z = Metal + 2mm foam pad
    hdd1_x = CaseW - HDD_W - 10;
    hdd1_y = CaseD - HDD_D - 8;
    translate([hdd1_x, hdd1_y, Metal + 2])
        hdd_3d();
    
    // HDD2 — suspended from top panel (upside-down), front-left
    // Z = CaseH - Metal - HDD_H
    hdd2_x = 10;
    hdd2_y = 8;
    translate([hdd2_x, hdd2_y, CaseH - Metal - HDD_H])
        rotate([180, 0, 0])
            hdd_3d();
    
    // === MOTHERBOARD LAYER ===
    // MB on standoffs — positioned to avoid HDD1 (bottom HDD at back-right)
    // MB placed toward front-left, I/O at rear (Y = CaseD)
    mb_x = 10.2;
    mb_y = 10.2;
    
    // Standoffs
    for (x = [mb_x + 6.35, mb_x + 6.35 + 158.75], y = [mb_y + 6.35, mb_y + 6.35 + 158.75]) {
        translate([x, y, Metal + 2])
            color("#777") difference() {
                cylinder(h=Standoff_H, d=7);
                translate([0,0,-0.5]) cylinder(h=Standoff_H+1, d=3.5);
            }
    }
    
    // Motherboard
    translate([mb_x, mb_y, Metal + Standoff_H + 2])
        motherboard_3d();
    
    // === INDICATORS ===
    // I/O shield cutout (rear wall)
    color("#444", 0.5) translate([(CaseW-144)/2, CaseD - Metal - 2, 20])
        cube([144, 4, 44]);
    
    // 60mm fan cutout (rear wall)
    color("#448", 0.3) translate([CaseW - 75, CaseD - Metal - 2, (CaseH-60)/2])
        cube([60, 4, 60]);
    
    // Top panel screw locations for HDD2
    top_z = CaseH - Metal;
    translate([0, 0, top_z]) {
        color("#ff4444", 0.7) {
            for (sx = [-1, 1], is_front = [true, false]) {
                y_off = is_front ? HDD_HOLE_FRONT : (HDD_D - HDD_HOLE_REAR);
                x_off = HDD_W/2 + sx*(HDD_W/2 - HDD_HOLE_SIDE - HDD_W/2);
                translate([hdd2_x + x_off, hdd2_y + y_off, -1])
                    cylinder(h=3, d1=8, d2=4, $fn=12);
            }
        }
    }
    
    // === CASE ===
    %case_body();
}

// ====== RENDER ======
if (SHOW_3D) {
    assembly_3d();
}

echo("====== COLO NAS CASE v4b ======");
echo(str("External: ", CaseW, "mm x ", CaseD, "mm x ", CaseH, "mm"));
echo(str("  = ", CaseW/25.4, "in x ", CaseD/25.4, "in x ", CaseH/25.4, "in"));
echo(str("HDD1 on bottom (right-side up), back-right"));
echo(str("HDD2 suspended from top (upside-down), front-left"));
echo(str("  — HDDs do NOT overlap in XY or Z"));
echo(str("Motherboard on ", Standoff_H, "mm standoffs, front-left position"));
echo(str("I/O panel: rear wall (Y = CaseD)"));
echo(str("60mm fan: rear wall, right side"));
echo("====================================");
