// Colo NAS Case v3 — 8" × 3" × 8" (W × H × D)
// Folded sheet metal · 18 ga (1.2mm)
// Staggered L — 2× 3.5" HDD + Mini ITX + 1U CPU cooler
// Units: mm   |   Scale: 25.4 = inches

// ====== CONSTANTS ======
CaseW = 203.2;  CaseH = 76.2;  CaseD = 203.2;  Metal = 1.2;
HDD_W = 101.6;  HDD_H = 26.1;  HDD_D = 147.0;
MB_W = 170.0;   MB_D = 170.0;  MB_H = 1.6;     Standoff_H = 10.0;

// Drive mount offset from walls
D = 6;  // drive inset from case walls

$fn = 30;

// ====== CASE BODY ======
module case_body() {
    difference() {
        color("#a0a8b0", 0.7) cube([CaseW, CaseD, CaseH]);
        translate([Metal, Metal, Metal])
            color("white", 0.5) cube([CaseW-2*Metal, CaseD-2*Metal, CaseH]);
        // I/O shield cutout (rear wall)
        translate([17, CaseD-Metal-1, 30])
            cube([144, Metal+2, 44]);
        // 60mm fan cutout (rear wall)
        translate([CaseW-70, CaseD-Metal-1, CaseH/2-30+5])
            cube([60, Metal+2, 60]);
        // Fan screw holes
        for (x = [CaseW-70+5, CaseW-70+55], y = [CaseH/2-30+5+5, CaseH/2-30+5+55]) {
            translate([x, CaseD-1, y]) rotate([90,0,0]) cylinder(d=4, h=4);
        }
    }
}

// ====== 3.5" HDD (detailed) ======
module hdd_detailed() {
    color("#2a2a2e") {
        // Main body
        cube([HDD_W, HDD_D, HDD_H]);
        // Top label area
        color("#d0d0d0", 0.15) translate([2, 2, HDD_H-0.5])
            cube([HDD_W-4, HDD_D-4, 0.5]);
        // PCB edge at bottom
        color("#1a5c2a") translate([0, HDD_D-30, 0])
            cube([HDD_W, 30, 2]);
        // SATA connector (rear)
        color("#333") translate([HDD_W/2-12, HDD_D-2, HDD_H/2-4])
            cube([24, 4, 8]);
        // Power connector
        color("#333") translate([HDD_W/2+14, HDD_D-2, HDD_H/2-4])
            cube([16, 4, 8]);
        // Side screw holes (standard position)
        for (s = [0, 1], z = [5, HDD_H-5]) {
            color("#555") translate([s*(HDD_W+1)-1, HDD_D/3, z])
                rotate([0,90,0]) cylinder(d=4, h=4);
            color("#555") translate([s*(HDD_W+1)-1, HDD_D*2/3, z])
                rotate([0,90,0]) cylinder(d=4, h=4);
        }
    }
    // Label text (single line representation)
    color("#888", 0.5) translate([HDD_W/2-15, HDD_D/2-3, HDD_H-0.6])
        cube([30, 6, 0.4]);
}

// ====== MOTHERBOARD ======
module motherboard_detailed() {
    color("#1a7b3a", 0.95) {
        cube([MB_W, MB_D, MB_H]);
        // PCB traces / detail
        color("#0d5a2a", 0.3) translate([5, 5, MB_H])
            cube([MB_W-10, MB_D-10, 0.2]);
    }
    // CPU socket area
    color("#888") translate([60, MB_D-85, MB_H])
        cube([40, 40, 2]);
    // 1U CPU cooler
    color("#999") translate([62, MB_D-83, MB_H+2]) {
        cube([36, 36, 13]);  // heatsink
        color("#333") translate([6, 6, 7])
            cube([24, 24, 5]);  // fan
    }
    // RAM slots
    color("#ffd700") translate([110, MB_D-12, MB_H])
        cube([55, 8, 6]);
    // Chipset
    color("#555") translate([100, 40, MB_H])
        cube([20, 20, 2]);
    // SATA ports (rear right edge)
    color("#444") for (i = [0:5]) {
        translate([130+i*12, MB_D-2, MB_H+2])
            cube([10, 4, 6]);
    }
    // 24-pin power (front edge)
    color("#222") translate([120, -2, MB_H])
        cube([16, 6, 8]);
    // Front panel header
    color("#666") translate([30, -2, MB_H])
        cube([20, 6, 6]);
}

// ====== STANDFOFS ======
module standoffs() {
    for (x = [18, 18+134], y = [22, 22+126]) {
        translate([x, y, HDD_H+Metal+D])
            color("#777") difference() {
                cylinder(h=Standoff_H, d=8);
                translate([0,0,-0.5]) cylinder(h=Standoff_H+1, d=3.5);
            }
    }
}

// ====== DRIVE BRACKETS (simplified) ======
module drive_bracket() {
    color("#888", 0.5) {
        // Left bracket for HDD1
        translate([D+HDD_W-2,  D+30, Metal+2])
            cube([2, 60, HDD_H+2]);
        // Right bracket for HDD2  
        translate([CaseW-D-HDD_W, CaseD-D-HDD_D+30, Metal+2])
            cube([2, 60, HDD_H+2]);
    }
}

// ====== 3D LAYOUT ======

// HDD 1 — Front-Left
translate([D, D, Metal+2])
    rotate([0,0,0])
        hdd_detailed();

// HDD 2 — Back-Right
translate([CaseW-HDD_W-D, CaseD-HDD_D-D, Metal+2])
    rotate([0,0,0])
        hdd_detailed();

// Standoffs (above drives)
standoffs();

// Motherboard (on standoffs)
translate([15, 20, HDD_H+Standoff_H+Metal+D])
    motherboard_detailed();

// Drive mounting brackets
drive_bracket();

// Case body (semi-transparent to show internals)
%case_body();

// ====== DIMENSION LINES ======
module arrow(x1,y1,x2,y2) {
    color("#ff4444") {
        translate([x1,y1,CaseH+5]) {
            linear_extrude(0.5) {
                $fn=8; 
                circle(d=2);
                translate([(x2-x1)/3, (y2-y1)/3]) circle(d=2);
                translate([(x2-x1)*2/3, (y2-y1)*2/3]) circle(d=2);
                translate([x2-x1, y2-y1]) circle(d=2);
            }
        }
    }
}

// Dimension labels  
module dim_label(text, pos) {
    color("#fff") translate(pos)
        linear_extrude(0.3)
            text(text, size=4, halign="center");
}

// Width dim
color("#ff4444") translate([0, -5, CaseH+8])
    cube([CaseW, 1, 0.5]);
dim_label(str(CaseW,"mm / 8\""), [CaseW/2-10, -12, CaseH+8]);

// Depth dim
color("#ff4444") translate([CaseW+5, 0, CaseH+8])
    cube([1, CaseD, 0.5]);
rotate([0,0,90]) dim_label(str(CaseD,"mm / 8\""), [CaseD/2-10, CaseW+3, CaseH+8]);

// Height dim
color("#ff4444") translate([-8, CaseD+5, 0])
    cube([1, 1, CaseH]);
dim_label(str(CaseH,"mm / 3\""), [-16, CaseD+10, CaseH/2]);

// Drive label
color("#00ff88") translate([12, D+10, HDD_H+Metal+2+6])
    cube([2, 40, 0.5]);
color("#00ff88") translate([12, D+10, HDD_H+Metal+2+6+8])
    cube([2, 40, 0.5]);
dim_label("HDD1", [18, D+50, HDD_H+Metal+2+10]);

echo("===== COLO NAS CASE v3 =====");
echo(str("External: ", CaseW, "mm x ", CaseD, "mm x ", CaseH, "mm"));
echo(str("  = ", (CaseW/25.4), "\" x ", (CaseD/25.4), "\" x ", (CaseH/25.4), "\""));
echo(str("Internal: ", CaseW-2*Metal, "mm x ", CaseD-2*Metal, "mm x ", CaseH-Metal, "mm"));
echo(str("Drives: 2x 3.5\" HDD"));
echo(str("  HDD1: front-left (", D, "×", D, " offset)"));
echo(str("  HDD2: back-right (", CaseW-HDD_W-D, "×", CaseD-HDD_D-D, " offset)"));
echo(str("Board: Mini ITX on ", Standoff_H, "mm standoffs"));
echo(str("Height used: ", HDD_H+Standoff_H+MB_H+13+Metal+D, "mm / ", (HDD_H+Standoff_H+MB_H+13+Metal+D)/25.4, "\""));
echo(str("Top clearance: ", CaseH-(HDD_H+Standoff_H+MB_H+13+Metal+D), "mm"));
echo(str("Total drives overlap: ", (HDD_W-D)+(CaseW-HDD_W-D)-CaseW, "mm offset in width"));
echo("");
echo("FABRICATION NOTES:");
echo("- 4 pieces: U-channel body, front, rear, top");
echo("- 18 ga (1.2mm) steel or aluminum");
echo("- Bend 90° on dashed lines");
echo("- I/O cutout: 144×44mm, centered 41mm from case bottom");
echo("- 60mm fan cutout: centered on rear panel, right side");
echo("- Drive mount: M3×6mm screws into drive side holes");
echo("- Standoffs: M3 10mm hex, 6mm OD");
