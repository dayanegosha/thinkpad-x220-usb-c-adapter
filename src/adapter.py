"""ThinkPad X220 DC-jack -> USB-C housing tailored to the PDC004-20V trigger.

Geometry summary
----------------
* Rectangular slug **12.0 × 9.7 × 11.2 mm** + cylindrical nose **Ø9.7 × 1.0 mm**
  matching the X220 chassis pocket and palmrest bezel.
* The nose tip is flat; the only external cutout is a rounded rectangle for the
  USB-C female metal shell.
* Internal pocket matches typical **WITRN PDC004** board dimensions: PCB **16.3 x 10.2 x 1.0 mm**, USB-C cage
  **9.0 x 3.2 mm**, metal sticks out **1.3 mm** past the PCB edge; opening
  plane **flush** with the nose tip (``y_tip``). Cage footprint on board **7.3 mm**.
* The pocket extends past the back face so the long board exits into the base.

All tunable values live in the parameter block below. Run this file to write
``stl/X220_USB_C_adapter.stl``.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from manifold3d import Manifold, CrossSection
from stl import mesh as stlmesh


# ---------------------------------------------------------------------------
# Laptop slot (don't change unless your chassis differs)
# ---------------------------------------------------------------------------

HOUSING_W = 12.0          # X — caliper-measured slug width
HOUSING_H = 9.7           # Z — caliper-measured slug height
HOUSING_D = 11.2          # Y — caliper-measured slug depth (into laptop; rear face unchanged)

# Extra rectangular slug only on the ring side (-Y), not symmetric +D/2 growth.
# Fills thin/void wall behind the nose ring without moving pocket or USB plane.
HOUSING_FRONT_EXTENSION_Y = 0.7

# Nose ring: Ø9.7 mm — exactly matches the slug height, so the ring is tangent
# to the top and bottom faces. 1 mm proud of the front face.
NOSE_OD = 9.7
NOSE_LEN = 1.0

# ---------------------------------------------------------------------------
# WITRN PDC004 — mechanical (vendor sheet, mm)
# ---------------------------------------------------------------------------

PCB_W = 10.2              # X — across the laptop
PCB_L = 16.3              # Y — FR4 only (long edge into laptop)
PCB_THICK = 1.0           # vendor: 1.0 mm

# USB-C female metal shell (opening 9 x 3.2)
USBC_SHELL_W = 9.0
USBC_SHELL_H = 3.2
USBC_SHELL_R = 1.60       # capped by min(..., H/2) in polygon helper

# PCB front edge -> USB opening plane (vendor: 17.60 total - 16.30 PCB = 1.30)
USBC_SHELL_PAST_PCB = 1.3

# Shift PCB registration toward the nose tip (-Y) so the USB tunnel stays
# open after pocket CSG (through-hole). Typical -0.10 ... -0.28 mm.
PCB_REGISTER_OFFSET_Y = -0.22

# Front cut must extend past the PCB plane and overlap the pocket subtract (mm).
APERTURE_MERGE_INTO_POCKET_Y = 0.90

# Pocket starts slightly forward of the PCB front for a clean merged void (mm).
POCKET_FRONT_OVERLAP_Y = 0.20

# Cage soldered on the PCB behind the opening (vendor top view: 7.30 mm)
USBC_SHELL_ON_PCB_Y = 7.30

# Legacy slack (only used if you switch back to fixed-length aperture mode)
APERTURE_SLACK_Y = 0.25

# ---------------------------------------------------------------------------
# Fit clearances (mm) — tune these per printer
# ---------------------------------------------------------------------------

PCB_W_CLEARANCE = 0.15    # total slop in X (≈0.075 mm/side — snug slip fit)
PCB_T_CLEARANCE = 0.10    # extra vertical slop in the PCB slot
SHELL_CLEARANCE = 0.16    # extra W and H of the front aperture
TOP_COMPONENT_CLEAR = 0.30  # above USB-C shell top — leaves room for the lid

USBC_RES = 64             # arc segments per 90° corner of the USB-C aperture
NOSE_SEGMENTS = 256       # segments around the cylindrical nose


# ---------------------------------------------------------------------------
# Derived geometry (auto-computed)
# ---------------------------------------------------------------------------

APERTURE_W = USBC_SHELL_W + SHELL_CLEARANCE
APERTURE_H = USBC_SHELL_H + SHELL_CLEARANCE
APERTURE_R = USBC_SHELL_R                          # capped in rounded_rect_polygon

POCKET_W = PCB_W + PCB_W_CLEARANCE

# Solve the Z stack-up so the USB-C metal shell ends up centred on Z = 0:
SHELL_TOP_Z = +USBC_SHELL_H / 2.0
SHELL_BOT_Z = -USBC_SHELL_H / 2.0
PCB_TOP_Z = SHELL_BOT_Z                            # top-mount: shell bottom = PCB top
PCB_BOT_Z = PCB_TOP_Z - PCB_THICK

POCKET_FLOOR_Z = PCB_BOT_Z - PCB_T_CLEARANCE / 2.0
POCKET_CEIL_Z = SHELL_TOP_Z + TOP_COMPONENT_CLEAR
POCKET_HEIGHT = POCKET_CEIL_Z - POCKET_FLOOR_Z
POCKET_CENTER_Z = (POCKET_FLOOR_Z + POCKET_CEIL_Z) / 2.0


def _aperture_depth_mm() -> float:
    y_tip = -HOUSING_D / 2.0 - NOSE_LEN
    y_pcb = y_tip + USBC_SHELL_PAST_PCB + PCB_REGISTER_OFFSET_Y
    return max(NOSE_LEN + 0.55, y_pcb + APERTURE_MERGE_INTO_POCKET_Y - y_tip)


APERTURE_DEPTH_Y = _aperture_depth_mm()


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def rounded_rect_polygon(width, height, radius, segments=USBC_RES):
    r = min(radius, width / 2.0, height / 2.0)
    hx = width / 2.0 - r
    hy = height / 2.0 - r
    pts = []
    corners = [
        (+hx, +hy, 0.0),
        (-hx, +hy, math.pi / 2),
        (-hx, -hy, math.pi),
        (+hx, -hy, 3 * math.pi / 2),
    ]
    for cx, cy, start in corners:
        for i in range(segments + 1):
            a = start + (math.pi / 2) * (i / segments)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rounded_prism(width, height, length, radius, segments=USBC_RES):
    """Rounded rectangular prism extruded along the Y axis."""
    poly = rounded_rect_polygon(width, height, radius, segments)
    solid = Manifold.extrude(CrossSection([poly]), length)
    solid = solid.translate((0.0, 0.0, -length / 2.0))
    solid = solid.rotate((90.0, 0.0, 0.0))
    return solid


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build():
    y_front = -HOUSING_D / 2.0           # -6.00
    y_tip = y_front - NOSE_LEN           # -7.35  outer face of the nose
    y_back = +HOUSING_D / 2.0            # +6.00
    y_pcb_front = y_tip + USBC_SHELL_PAST_PCB + PCB_REGISTER_OFFSET_Y

    # Through-slot: length from nose tip past PCB front and into pocket zone.
    aperture_len = max(
        NOSE_LEN + 0.55,
        y_pcb_front + APERTURE_MERGE_INTO_POCKET_Y - y_tip,
    )
    # Body: rectangular slug (rear y = +D/2 fixed; front extends by HOUSING_FRONT_EXTENSION_Y)
    # + cylindrical nose still jointed at y_front = -D/2 (USB plane / pocket unchanged).
    d_rect = HOUSING_D + HOUSING_FRONT_EXTENSION_Y
    cy_rect = -HOUSING_FRONT_EXTENSION_Y / 2.0
    outer = (
        Manifold.cube((HOUSING_W, d_rect, HOUSING_H), center=True)
        .translate((0.0, cy_rect, 0.0))
    )
    nose_full = (
        Manifold.cylinder(
            NOSE_LEN, NOSE_OD / 2.0,
            circular_segments=NOSE_SEGMENTS, center=False,
        )
        .rotate((90.0, 0.0, 0.0))
        .translate((0.0, y_front, 0.0))
    )
    # Clip the cylindrical nose to the housing's Z range so its top and bottom
    # are flush with the slug's top/bottom faces (the OEM "срезано" look).
    nose_clip = (
        Manifold.cube(
            (NOSE_OD + 2.0, NOSE_LEN + 0.4, HOUSING_H),
            center=True,
        ).translate((0.0, y_front - NOSE_LEN / 2.0, 0.0))
    )
    nose = nose_full ^ nose_clip  # manifold3d: ^ is intersection

    body = outer + nose

    # USB-C: rounded slot from nose tip, long enough to merge with the pocket void.
    aperture = rounded_prism(APERTURE_W, APERTURE_H, aperture_len, APERTURE_R)
    aperture = aperture.translate((0.0, y_tip + aperture_len / 2.0, 0.0))

    pocket_y_start = y_pcb_front - POCKET_FRONT_OVERLAP_Y
    pocket_y_end = y_back + 0.50                      # punch through the rear
    pocket_len = pocket_y_end - pocket_y_start
    pocket = Manifold.cube((POCKET_W, pocket_len, POCKET_HEIGHT), center=True)
    pocket = pocket.translate(
        (0.0, (pocket_y_start + pocket_y_end) / 2.0, POCKET_CENTER_Z)
    )

    return body - aperture - pocket


# ---------------------------------------------------------------------------
# Export & report
# ---------------------------------------------------------------------------

def export_stl(solid, path):
    me = solid.to_mesh()
    verts = np.asarray(me.vert_properties, dtype=np.float32)
    tris = np.asarray(me.tri_verts, dtype=np.uint32)
    if verts.shape[1] > 3:
        verts = verts[:, :3]
    data = np.zeros(tris.shape[0], dtype=stlmesh.Mesh.dtype)
    data["vectors"] = verts[tris]
    stlmesh.Mesh(data, remove_empty_areas=False).save(str(path))


def main():
    solid = build()
    out_dir = Path(__file__).resolve().parent.parent / "stl"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "X220_USB_C_adapter.stl"
    export_stl(solid, out_path)

    me = solid.to_mesh()
    verts = np.asarray(me.vert_properties)[:, :3]
    bb_min = verts.min(axis=0)
    bb_max = verts.max(axis=0)

    y_tip = -HOUSING_D / 2.0 - NOSE_LEN
    y_pcb_front = y_tip + USBC_SHELL_PAST_PCB + PCB_REGISTER_OFFSET_Y
    y_back = +HOUSING_D / 2.0
    pocket_len_y = (y_back + 0.50) - (y_pcb_front - POCKET_FRONT_OVERLAP_Y)
    pcb_protrude_back = PCB_L - (y_back - y_pcb_front)

    print(f"STL written : {out_path}")
    print(f"Triangles   : {me.tri_verts.shape[0]}")
    print(
        f"BBox        : X {bb_max[0]-bb_min[0]:.3f}  "
        f"Y {bb_max[1]-bb_min[1]:.3f}  Z {bb_max[2]-bb_min[2]:.3f} mm"
    )
    print()
    print("--- Pocket for PDC004-20V ---")
    print(f"Width  (X) : {POCKET_W:.2f} mm   (target PCB {PCB_W:.2f} + {PCB_W_CLEARANCE:.2f})")
    print(
        f"Depth  (Y) : pocket spans {pocket_len_y:.2f} mm in the housing; "
        f"PCB length {PCB_L:.2f} mm → protrudes {pcb_protrude_back:.2f} mm past back face"
    )
    print(
        f"Height (Z) : {POCKET_HEIGHT:.2f} mm   (floor Z={POCKET_FLOOR_Z:+.2f}, "
        f"ceil Z={POCKET_CEIL_Z:+.2f})"
    )
    print(
        f"PCB sits   : bottom Z={PCB_BOT_Z:+.2f}, top Z={PCB_TOP_Z:+.2f}"
    )
    print(
        f"USB-C shell: top Z={SHELL_TOP_Z:+.2f}, bottom Z={SHELL_BOT_Z:+.2f} "
        f"→ centred at Z = 0 (aperture centre)"
    )
    print(
        f"Aperture   : {APERTURE_W:.2f} x {APERTURE_H:.2f} mm   "
        f"(shell {USBC_SHELL_W:.2f} x {USBC_SHELL_H:.2f} + clearance {SHELL_CLEARANCE:.2f})"
    )
    print(
        f"Reg. step  : PCB front Y={y_pcb_front:+.2f}  "
        f"(shell past PCB nominal {USBC_SHELL_PAST_PCB:.2f} mm + register "
        f"{PCB_REGISTER_OFFSET_Y:+.2f} mm)  |  nose tip Y={y_tip:+.2f}"
    )


if __name__ == "__main__":
    main()
