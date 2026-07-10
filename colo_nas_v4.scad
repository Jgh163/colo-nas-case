// Colo NAS Enclosure v4 — 7.5" × 7.5" × 2.5" (W × D × H)
// Folded sheet metal · 18 ga (1.2mm) or 20 ga (0.9mm)
// Layout: 2× 3.5" HDD suspended upside-down from top panel
//         Mini ITX on standoffs on bottom panel
// Units: mm   |   Scale: 25.4 = inches
//
// RENDER MODES:
//   Preview (F5): show 3D assembly with components
//   Render  (F6): solid model, export STL for GitHub 3D viewer
//   Uncomment USE_FLAT_PATTERN to see flat layout for SendCutSend

// ====== SWITCH ======
SHOW_3D = true;   // true = 3D assembly, false = flat pattern
USE_20GA = false;  // false = 18 ga (1.2mm), true = 20 ga (0.9mm)

// ====== CONSTANTS ======
Metal = USE_20GA ? 0.9 : 1.2;   // sheet thickness

// External case dimensions
CaseW = 190.5;  // 7.5"
CaseD = 190.5;  // 7.5"
CaseH = 63.5;   // 2.5"

// Internal dimensions
InW = CaseW - 2*Metal;
InD = CaseD - 2*Metal;
InH = CaseH - Metal;

// 3.5" HDD (per SFF-8301)
HDD_W = 101.6;   // 4.000"
HDD_D = 147.0;   // 5.787"
HDD_H = 26.1;    // 1.028"

// Bottom mounting hole positions (SFF-8301 standard)
// Measured from front edge of drive to hole center
HDD_HOLE_FRONT = 44.45;  // A6 = 1.750" — front pair
HDD_HOLE_REAR  = 41.28;  // A7 = 1.625" from rear = 147-41.28 = 105.72mm from front
HDD_HOLE_ALT   = 76.20;  // A13 = 3.000" — alternate location
HDD_HOLE_SIDE  = 6.35;   // A10 = 0.250" — inset from side edge

// Mini ITX
MB_W = 170.0;   // 6.7"
MB_D = 170.0;   // 6.7"
MB_H = 1.6;     // PCB thickness
Standoff_H = 10.0;  // 0.4" hex standoff

// 1U CPU cooler (approximate)
Cooler_W = 36;
Cooler_D = 36;
Cooler_H = 13;  // 0.5" active heatsink

// HDD suspension gap from top panel
HDD_SUSPEND_GAP = 1.0;  // small gap so HDD doesn't rub top panel

// ====== PARAMETERS ======
$fn = 30;

// ====== 3.5" HDD MODEL ======
module hdd_3d(include_connectors=true) {
    color("#2a2a2e") {
        // Main body
        cube([HDD_W, HDD_D, HDD_H]);
        
        // PCB on bottom (since drive is upside-down, PCB faces up toward top panel)
        color("#1a5c2a") translate([0, HDD_D-30, HDD_H-2])
            cube([HDD_W, 30, 2]);
        
        if (include_connectors) {
            // SATA data + power connectors (rear edge)
            color("#333") translate([HDD_W/2-12, HDD_D-1, HDD_H-8])
                cube([24, 2, 8]);
            color("#333") translate([HDD_W/2+14, HDD_D-1, HDD_H-8])
                cube([16, 2, 8]);
        }
        
        // Bottom mounting holes (threaded, 6-32 UNC) — visible when upside-down
        // Standard pair (A6): 44.45mm from front
        for (sx = [-1, 1]) {
            color("#888", 0.5) translate([HDD_W/2 + sx*(HDD_W/2 - HDD_HOLE_SIDE - HDD_W/2), 0, 0])
                cylinder(d=5, h=HDD_H, $fn=12);
        }
    }
}

// ====== MOTHERBOARD MODEL ======
module motherboard_3d() {
    color("#1a7b3a", 0.95) {
        cube([MB_W, MB_D, MB_H]);
    }
    
    // CPU socket + 1U cooler
    color("#999") translate([60, MB_D-85, MB_H]) {
        cube([40, 40, 2]);  // socket
        translate([2, 2, 2]) {
            color("#aaa") cube([36, 36, Cooler_H]);  // heatsink
            color("#333") translate([6, 6, 6])
                cube([24, 24, 5]);  // fan
        }
    }
    
    // RAM slots
    color("#ffd700") translate([110, MB_D-12, MB_H])
        cube([55, 8, 6]);
    
    // SATA ports (right edge)
    color("#444") for (i = [0:3]) {
        translate([135+i*10, MB_D-1, MB_H+2])
            cube([8, 2, 6]);
    }
    
    // 24-pin power
    color("#222") translate([120, 0, MB_H])
        cube([16, 6, 8]);
    
    // I/O shield area (rear)
    color("#666", 0.5) translate([17, MB_D-2, 0])
        cube([144, 2, 42]);
}

// ====== STANDOFFS ======
module standoffs_3d() {
    // 4 corner standoffs for Mini ITX (standard mounting pattern)
    // MB screw holes: 6.35mm from edges, in a 158.75×158.75mm grid
    for (x = [6.35, 6.35+158.75], y = [6.35, 6.35+158.75]) {
        translate([x, y, Metal+2])
            color("#777") difference() {
                cylinder(h=Standoff_H, d=7);
                translate([0,0,-0.5]) cylinder(h=Standoff_H+1, d=3.5);
            }
    }
}

// ====== COUNTERSUNK SCREW INDICATORS ======
module countersunk_screws(hdd_x, hdd_y, top_z) {
    // HDD upside-down: bottom mounting holes face UP (accessible from top)
    // Standard bottom holes: front pair at A6, rear pair at A7 (or A13)
    // Show screw indicators at the standard positions
    
    for (is_front = [true, false]) {
        y_off = is_front ? HDD_HOLE_FRONT : (HDD_D - HDD_HOLE_REAR);
        for (sx = [-1, 1]) {
            x_off = HDD_W/2 + sx*(HDD_W/2 - HDD_HOLE_SIDE - HDD_W/2);
            translate([hdd_x + x_off, hdd_y + y_off, top_z - 1])
                color("#ff4444", 0.8) 
                    cylinder(h=3, d1=8, d2=4, $fn=12);  // countersunk indicator
        }
    }
    
    // Also add alternate holes (A13) for future drives
    y_off = HDD_HOLE_ALT;
    for (sx = [-1, 1]) {
        x_off = HDD_W/2 + sx*(HDD_W/2 - HDD_HOLE_SIDE - HDD_W/2);
        translate([hdd_x + x_off, hdd_y + y_off, top_z - 1])
            color("#ff8844", 0.5) 
                cylinder(h=2, d1=7, d2=3.5, $fn=12);  // alternate holes in orange
    }
}

// ====== CASE BODY (Walls only, transparent in 3D view) ======
module case_outline() {
    color("#a0a8b0", 0.2) cube([CaseW, CaseD, CaseH]);
}

// ====== TOP PANEL (with countersunk HDD holes) ======
module top_panel() {
    color("#8890a0", 0.9) {
        difference() {
            cube([CaseW, CaseD, Metal]);
            
            // Countersunk holes for HDD1
            // HDD1 position (front-left area)
            hdd1_x = 8; hdd1_y = 8;
            translate([hdd1_x, hdd1_y, 0]) {
                // Front pair (A6)
                for (sx = [-1, 1]) {
                    x = HDD_W/2 + sx*(HDD_W/2 - HDD_HOLE_SIDE - HDD_W/2);
                    // Standard countersunk: flat head 82°, 6-32 screw
                    translate([x, HDD_HOLE_FRONT, -1]) 
                        cylinder(h=5, d1=9, d2=3.5, $fn=12);
                    translate([x, HDD_D - HDD_HOLE_REAR, -1])
                        cylinder(h=5, d1=9, d2=3.5, $fn=12);
                }
            }
            
            // Countersunk holes for HDD2
            // HDD2 position (back-right area, offset to avoid full overlap)
            hdd2_x = CaseW - HDD_W - 8; hdd2_y = CaseD - HDD_D - 8;
            translate([hdd2_x, hdd2_y, 0]) {
                for (sx = [-1, 1]) {
                    x = HDD_W/2 + sx*(HDD_W/2 - HDD_HOLE_SIDE - HDD_W/2);
                    translate([x, HDD_HOLE_FRONT, -1])
                        cylinder(h=5, d1=9, d2=3.5, $fn=12);
                    translate([x, HDD_D - HDD_HOLE_REAR, -1])
                        cylinder(h=5, d1=9, d2=3.5, $fn=12);
                }
            }
            
            // Optional vent holes
            for (x = [30:30:CaseW-30], y = [30:30:CaseD-30]) {
                translate([x, y, -1]) cylinder(d=3, h=5);
            }
        }
    }
}

// ====== BOTTOM PANEL ======
module bottom_panel() {
    color("#8890a0", 0.9) {
        difference() {
            cube([CaseW, CaseD, Metal]);
            
            // Standoff through-holes (for M3 screws from bottom)
            for (x = [6.35, 6.35+158.75], y = [6.35, 6.35+158.75]) {
                translate([x, y, -1]) cylinder(d=5, h=5);
            }
        }
    }
}

// ====== 3D ASSEMBLY ======
module assembly_3d() {
    // Everything is inside the case, positioned from bottom-front-left origin
    
    // === BOTTOM LAYER ===
    // Bottom panel
    translate([0, 0, 0]) bottom_panel();
    
    // Standoffs on bottom
    translate([0, 0, Metal]) standoffs_3d();
    
    // Motherboard on standoffs
    translate([10.2, 10.2, Metal + Standoff_H + 2])
        motherboard_3d();
    
    // === TOP LAYER (HDDs suspended from top panel) ===
    // Top panel HDD screw mount Z
    top_z = CaseH - Metal - HDD_SUSPEND_GAP;
    
    // HDD1 — Front-Left (suspended from top, upside-down)
    hdd1_x = 8; hdd1_y = 8;
    translate([hdd1_x, hdd1_y, top_z - HDD_H])
        rotate([180, 0, 0])  // upside down (PCB up)
            hdd_3d();
    
    // HDD2 — Back-Right (overlaps HDD1 in XY — same Z = collision area)
    hdd2_x = CaseW - HDD_W - 8; hdd2_y = CaseD - HDD_D - 8;
    translate([hdd2_x, hdd2_y, top_z - HDD_H])
        rotate([180, 0, 0])  // upside down
            hdd_3d();
    
    // Countersunk screw indicators (show where screws go through top)
    translate([0, 0, CaseH - Metal])
        countersunk_screws(hdd1_x, hdd1_y, 0);
    translate([0, 0, CaseH - Metal])
        countersunk_screws(hdd2_x, hdd2_y, 0);
    
    // Top panel (semi-transparent to show screw locations)
    translate([0, 0, CaseH - Metal])
        %top_panel();
    
    // I/O shield cutout indicator (rear wall)
    color("#444", 0.5) translate([12, CaseD - Metal - 2, 20])
        cube([144, 4, 44]);
    
    // Case outline (ghost)
    %case_outline();
}

// ====== FLAT PATTERN for SendCutSend ======
module flat_pattern() {
    // 4 pieces: U-channel body, rear panel, front panel, top panel
    
    // All dimensions in mm for laser cutting
    // 20 ga (0.9mm) or 18 ga (1.2mm) — bend allowance ~1.5× metal thickness
    
    BendAllow = Metal * 1.5;
    
    // === PIECE 1: U-channel body (bottom + 2 side walls, 1 continuous piece) ===
    // Unfolded: Bottom is CaseW × CaseD, side walls fold up from bottom
    // Side walls = CaseH - Metal tall (since bottom takes the thickness)
    // Side walls are on the depth-edges (front and back of case)
    
    module body_flat() {
        color("#888", 0.8) {
            // Bottom panel
            translate([0, 0])
                square([CaseD, CaseW]);
            
            // Back wall (folds up along back edge, Y=0)
            translate([-CaseH + Metal, 0])
                square([CaseH - Metal, CaseW]);
            
            // Front wall (folds up along front edge, Y=CaseD)
            translate([CaseD, 0])
                square([CaseH - Metal, CaseW]);
        }
        
        // Bend line indicators
        color("#ff4444", 0.5) {
            // Back wall bend line
            translate([-1, 0, 0]) square([2, CaseW]);
            // Front wall bend line
            translate([CaseD - 1, 0, 0]) square([2, CaseW]);
        }
    }
    
    // === PIECE 2: Rear panel (with I/O cutout + 60mm fan) ===
    module rear_flat() {
        color("#999", 0.8) {
            difference() {
                square([CaseW, CaseH]);
                
                // I/O shield cutout (centered)
                translate([(CaseW-144)/2, CaseH/2-22])
                    square([144, 44]);
                
                // 60mm fan cutout (right side)
                translate([CaseW - 75, (CaseH-60)/2])
                    square([60, 60]);
                
                // Fan screw holes
                for (x = [CaseW-75+5, CaseW-75+55], y = [(CaseH-60)/2+5, (CaseH-60)/2+55]) {
                    translate([x, y]) circle(d=4);
                }
            }
        }
    }
    
    // === PIECE 3: Front panel (vent holes) ===
    module front_flat() {
        color("#999", 0.8) {
            difference() {
                square([CaseW, CaseH]);
                
                // Drive ventilation slots
                for (x = [20:30:CaseW-20], y = [10:25:CaseH-10]) {
                    translate([x, y]) circle(d=4);
                }
                
                // Or rectangular vent slots
                for (x = [15:40:CaseW-15], y = [12:20:CaseH-15]) {
                    translate([x, y]) square([12, 2]);
                }
            }
        }
    }
    
    // === PIECE 4: Top panel (with countersunk HDD holes) ===
    module top_flat() {
        color("#aaa", 0.9) {
            difference() {
                square([CaseW, CaseD]);
                
                // HDD1 countersunk holes
                h1x = 8; h1y = 8;
                for (sx = [-1, 1], is_front = [true, false]) {
                    y_off = is_front ? HDD_HOLE_FRONT : (HDD_D - HDD_HOLE_REAR);
                    x_off = HDD_W/2 + sx*(HDD_W/2 - HDD_HOLE_SIDE - HDD_W/2);
                    translate([h1x + x_off, h1y + y_off])
                        circle(d=4.5);  // 6-32 clearance hole (0.177")
                }
                
                // HDD2 countersunk holes  
                h2x = CaseW - HDD_W - 8; h2y = CaseD - HDD_D - 8;
                for (sx = [-1, 1], is_front = [true, false]) {
                    y_off = is_front ? HDD_HOLE_FRONT : (HDD_D - HDD_HOLE_REAR);
                    x_off = HDD_W/2 + sx*(HDD_W/2 - HDD_HOLE_SIDE - HDD_W/2);
                    translate([h2x + x_off, h2y + y_off])
                        circle(d=4.5);
                }
                
                // Alternate A13 holes (optional, for future drives)
                for (pos = [[h1x, h1y], [h2x, h2y]]) {
                    for (sx = [-1, 1]) {
                        x_off = HDD_W/2 + sx*(HDD_W/2 - HDD_HOLE_SIDE - HDD_W/2);
                        translate([pos[0] + x_off, pos[1] + HDD_HOLE_ALT])
                            circle(d=4.5);
                    }
                }
                
                // Vent holes
                for (x = [20:30:CaseW-20], y = [20:30:CaseD-20]) {
                    translate([x, y]) circle(d=3);
                }
            }
            
            // Dimension labels for SendCutSend
            color("#333") {
                translate([CaseW/2-20, -8])
                    text(str(CaseW/25.4, "\" W"), size=4, halign="center");
                translate([-35, CaseD/2-3])
                    text(str(CaseD/25.4, "\" D"), size=4);
            }
        }
    }
    
    // === LAYOUT ===
    $fn = 24;
    
    // Arrange pieces for flat pattern sheet layout
    translate([50, 350]) body_flat();
    translate([50, 50]) rear_flat();
    translate([250, 50]) front_flat();
    translate([50, 180]) top_flat();
}

// ====== RENDER ======
if (SHOW_3D) {
    assembly_3d();
} else {
    // Flat pattern view
    flat_pattern();
}

echo("====== COLO NAS CASE v4 ======");
echo(str("External: ", CaseW, "mm x ", CaseD, "mm x ", CaseH, "mm"));
echo(str("  = ", CaseW/25.4, "in x ", CaseD/25.4, "in x ", CaseH/25.4, "in"));
echo(str("Metal: ", USE_20GA ? "20 ga (0.9mm)" : "18 ga (1.2mm)"));
echo(str("Drives: 2x 3.5\" HDD (suspended from top, upside-down)"));
echo(str("  HDD1: front-left position"));
echo(str("  HDD2: back-right position"));
echo(str("  NOTE: HDDs overlap in XY — see 3D model"));
echo(str("Board: Mini ITX on ", Standoff_H, "mm standoffs"));
echo(str("Height used: ", Metal + Standoff_H + MB_H + Cooler_H + 6 + HDD_H + Metal, "mm"));
echo(str("  = ", (Metal + Standoff_H + MB_H + Cooler_H + 6 + HDD_H + Metal)/25.4, "in"));
echo(" ");
echo("FABRICATION — 4 pieces for SendCutSend:");
echo("  1. U-channel body (bottom + front/back walls, folded)");
echo("  2. Rear panel (with I/O cutout + 60mm fan hole)");
echo("  3. Front panel (ventilated)");
echo("  4. Top panel (with countersunk HDD holes + vents)");
echo(" ");
echo("HARDWARE:");
echo("  - 6-32 countersunk flathead screws × 8-16 (through top into HDDs)");
echo("  - M3×10mm hex standoffs × 4 (motherboard to bottom panel)");
echo("  - M3×5mm screws × 8 (MB to standoffs, standoffs to bottom)");
echo("  - 6-32×3/16\" screws for HDDs (per SFF-8301, 20 ga top panel)");
echo("  - Rubber/foam isolation pads under HDD mounting points");
echo(" ");
echo("IMPORTANT — HDD OVERLAP:");
echo("  Two 4\"-wide HDDs need 8\" minimum width for side-by-side placement.");
echo("  At 7.5\" width, the drives overlap in XY by ~1\".");
echo("  Solutions: (a) Widen case to 8.25\", (b) Offset one HDD on thin spacers,");
echo("  (c) Mount one HDD from bottom, one from top (different Z levels).");
echo("  The 3D model shows this overlap.");
echo("====================================");
