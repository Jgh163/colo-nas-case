// Colo NAS Enclosure 3D — 8" × 3" × 8"
// Staggered L-layout: 2× 3.5" HDD + Mini ITX + 1U CPU cooler
// Units: mm

CaseW = 203.2; CaseH = 76.2; CaseD = 203.2; Metal = 1.2;
HDD_W = 101.6; HDD_H = 26.1; HDD_D = 147.0;
MB_W = 170.0; MB_D = 170.0; MB_H = 1.6; Standoff_H = 10.0;
$fn = 30;

// ====== CASE BODY ======
difference() {
    cube([CaseW, CaseD, CaseH]);
    translate([Metal, Metal, Metal])
        cube([CaseW-2*Metal, CaseD-2*Metal, CaseH]);
    // I/O cutout on rear wall  
    translate([17, CaseD-Metal-1, 30])
        cube([144, Metal+1, 44]);
    // Fan cutout on rear wall
    translate([CaseW-70, CaseD-Metal-1, CaseH/2-25])
        cube([60, Metal+1, 50]);
}

// ====== DRIVES ======
color("#444", 0.9) {
    // Drive 1: Front-Left (flush with bottom)
    translate([6, 6, Metal+3])
        cube([HDD_W, HDD_D, HDD_H]);
    // Drive 2: Back-Right
    translate([CaseW-HDD_W-6, CaseD-HDD_D-6, Metal+3])
        cube([HDD_W, HDD_D, HDD_H]);
}

// ====== STANDFOFS ======
for (x = [20, 20+130], y = [25, 25+130]) {
    translate([x, y, HDD_H+Metal+3])
        color("#888")
            cylinder(h=Standoff_H, d=6);
}

// ====== MOTHERBOARD ======
color("#1b6b3a", 0.95)
    translate([15, 20, HDD_H+Standoff_H+Metal+3])
        cube([MB_W, MB_D, MB_H]);

// CPU cooler (1U active)
color("#aaa")
    translate([80, CaseD-90, HDD_H+Standoff_H+MB_H+Metal+3])
        cube([35, 35, 13]);

// I/O shield
color("#333")
    translate([15, CaseD-Metal-2, HDD_H+Standoff_H+Metal+3+20])
        cube([2, 15, 44]);

// ====== DIMENSIONS ======
echo("=== NAS CASE ===");
echo(str("W ", CaseW, "mm / ", CaseW/25.4, "\""));
echo(str("H ", CaseH, "mm / ", CaseH/25.4, "\""));
echo(str("D ", CaseD, "mm / ", CaseD/25.4, "\""));
echo(str("Drives: 2x 3.5\" HDD"));
echo(str("Board: Mini ITX"));
echo(str("CPU cooler: 1U active (13mm)"));
echo(str("Total height used: ", HDD_H+Standoff_H+MB_H+13+Metal+3, "mm"));
echo(str("Top clearance: ", CaseH-(HDD_H+Standoff_H+MB_H+13+Metal+3), "mm"));
