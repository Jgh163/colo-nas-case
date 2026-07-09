// Colo NAS Enclosure — 8" × 3" × 8" (W × H × D)
// Folded sheet metal, 18 ga (1.2mm)
// Layout: Staggered L - 2× 3.5" HDD + Mini ITX
// 
// FLAT PATTERN for sheet metal fabrication
// Bend reliefs not shown — add 3mm at each bend line
//
// Render: OpenSCAD → export DXF for flat pattern
// Units: mm

// ====== CONSTANTS ======
CaseW = 203.2;       // 8"
CaseH = 76.2;        // 3" 
CaseD = 203.2;       // 8"
Metal = 1.2;         // 18 ga

// Fold allowance per bend (approximately for 18ga)
Fold = 2.0;

// Drive (Seagate Exos / WD Gold)
HDD_W = 101.6;
HDD_H = 26.1;
HDD_D = 147.0;

// Mini ITX
MB_W = 170.0;
MB_D = 170.0;
MB_H = 1.6;
Standoff_H = 10.0;

// ====== MAIN BODY (U-Channel: Bottom + 2 Sides) ======
module body_flat() {
    // Unfolded: Bottom + 2 side walls
    // Bottom = CaseW × CaseD
    // Side walls = CaseH - Metal × CaseD (folded up)
    // Total unfolded width = CaseD (bottom) + 2*(CaseH - Metal) (sides)
    
    color("gray", 0.8) {
        // Bottom panel
        square([CaseD, CaseW]);
        
        // Left side (folded up along left edge of bottom)
        translate([-CaseH + Metal, 0])
            square([CaseH - Metal, CaseW]);
        
        // Right side (folded up along right edge of bottom)  
        translate([CaseD, 0])
            square([CaseH - Metal, CaseW]);
    }
}

// ====== FRONT PANEL (separate piece) ======
module front_flat() {
    color("gray", 0.6) {
        // Front = CaseW × CaseH
        square([CaseW, CaseH]);
        // Drive vent holes
        for (x = [30, 170], y = [15, 55]) {
            translate([x, y])
                circle(d=5);
        }
    }
}

// ====== REAR PANEL (separate piece) ======
module rear_flat() {
    color("gray", 0.6) {
        square([CaseW, CaseH]);
    }
}

// ====== TOP PANEL (separate piece) ======
module top_flat() {
    color("gray", 0.5) {
        square([CaseD, CaseW]);
    }
}

// ====== FLAT PATTERN LAYOUT ======
$fn = 20;

// Show the flat pattern for laser cutting
translate([0, 300]) {
    // U-Channel body (bottom + 2 sides, one continuous piece)
    translate([0, 0])
        body_flat();
    
    // Front panel
    translate([0, -80])
        front_flat();
    
    // Rear panel
    translate([250, -80])
        rear_flat();
    
    // Top panel
    translate([0, -180])
        top_flat();
}

// ====== DIMENSION MARKERS ======
module dim_line(x1, y1, x2, y2, label) {
    color("black") {
        line([x1, y1], [x2, y2]);
        translate([(x1+x2)/2, (y1+y2)/2 - 5])
            text(label, size=4);
    }
}

// ====== 3D VIEW ======

// Drives
// Drive 1: Front-Left
color("#4a4a4a")
    translate([5, 5, Metal + 2])
        cube([HDD_W, HDD_D, HDD_H]);

// Drive 2: Back-Right  
color("#4a4a4a")
    translate([CaseW - HDD_W - 5, CaseD - HDD_D - 5, Metal + 2])
        cube([HDD_W, HDD_D, HDD_H]);

// Motherboard
color("#1a6b3c", 0.9) {
    translate([15, 20, HDD_H + Standoff_H + Metal + 2])
        cube([MB_W, MB_D, MB_H]);
    
    // Standoffs
    for (x = [15, 15+MB_W-15*2], y = [20, 20+MB_D-20*2]) {
        translate([x, y, HDD_H + Metal + 2])
            color("#888")
                cylinder(h=Standoff_H, d=6);
    }
}

// 1U CPU cooler
color("#999")
    translate([80, CaseD - 85, HDD_H + Standoff_H + MB_H + Metal + 2])
        cube([30, 30, 13]);

// I/O shield at rear
color("#333")
    translate([12, CaseD - Metal - 44, HDD_H + Standoff_H + Metal + 2])
        cube([2, 44, 44]);

// Case outline (transparent)
%color("white", 0.15)
    cube([CaseW, CaseD, CaseH]);

echo("=========== COLO NAS CASE ===========");
echo(str("External: ", CaseW, "mm x ", CaseD, "mm x ", CaseH, "mm"));
echo(str("  = ", (CaseW/25.4), "in x ", (CaseD/25.4), "in x ", (CaseH/25.4), "in"));
echo(str("Drives: 2x 3.5\" HDD stacked @ staggered L"));
echo(str("Board: Mini ITX (", MB_W, "x", MB_D, "mm)"));
echo(str("CPU cooler: 1U active (13mm / 0.5\")"));
echo(str("Height used: ", HDD_H + Standoff_H + MB_H + 13 + Metal + 2, "mm"));
echo(str("    = ", (HDD_H + Standoff_H + MB_H + 13 + Metal + 2)/25.4, "in"));
echo(str("Clearance top: ", CaseH - (HDD_H + Standoff_H + MB_H + 13 + Metal + 2), "mm"));
echo(" ");
echo("Flat pattern - 4 pieces:");
echo("  1. U-channel body: (bottom + 2 side walls)");
echo("  2. Front panel (with drive vents)");
echo("  3. Rear panel (with I/O cutout)");
echo("  4. Top panel (ventilated)");
echo("Sheet: 18 ga (1.2mm) steel or aluminum");
echo("Bend: 90° along dashed lines");
echo("======================================");
