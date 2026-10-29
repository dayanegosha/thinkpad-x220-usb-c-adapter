"""Корпус USB-C PD trigger PDC004-20V для ThinkPad X220.

Размеры заданы в миллиметрах, ось Y направлена внутрь ноутбука.
Плата выходит за заднюю грань корпуса, разъём расположен заподлицо с носиком.
Запуск файла сохраняет модель в stl/X220_USB_C_adapter.stl.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from manifold3d import Manifold, CrossSection
from stl import mesh as stlmesh

# Посадочное место в ноутбуке

HOUSING_W = 12.0          # X, ширина посадочного места
HOUSING_H = 9.7           # Z, высота посадочного места
HOUSING_D = 11.2          # Y, глубина посадочного места

# Утолщаем стенку со стороны носика (-Y), не сдвигая карман и плоскость разъёма.
HOUSING_FRONT_EXTENSION_Y = 0.7

# Диаметр носика совпадает с высотой корпуса; выступ за переднюю грань — 1 мм.
NOSE_OD = 9.7
NOSE_LEN = 1.0

# Плата WITRN PDC004, размеры производителя

PCB_W = 10.2              # X, поперёк ноутбука
PCB_L = 16.3              # Y, длина самой платы
PCB_THICK = 1.0           # Толщина платы

# Металлический корпус разъёма USB-C
USBC_SHELL_W = 9.0
USBC_SHELL_H = 3.2
USBC_SHELL_R = 1.60       # Радиус ограничен половиной высоты в rounded_rect_polygon

# Выступ разъёма за передний край платы: 17,60 − 16,30 = 1,30 мм.
USBC_SHELL_PAST_PCB = 1.3

# Сдвиг платы к носику (-Y) оставляет проход открытым после вычитания кармана.
# Обычно подходит от -0,10 до -0,28 мм.
PCB_REGISTER_OFFSET_Y = -0.22

# Прорезь должна пересекаться с карманом за передним краем платы.
APERTURE_MERGE_INTO_POCKET_Y = 0.90

# Карман начинается перед краем платы, чтобы соединиться с прорезью.
POCKET_FRONT_OVERLAP_Y = 0.20

# Длина корпуса разъёма на плате по чертежу производителя.
USBC_SHELL_ON_PCB_Y = 7.30

# Запас для прежнего варианта с фиксированной длиной прорези.
APERTURE_SLACK_Y = 0.25

# Зазоры для подгонки под принтер

PCB_W_CLEARANCE = 0.15    # Общий зазор по X, примерно 0,075 мм на сторону
PCB_T_CLEARANCE = 0.10    # Зазор по толщине платы
SHELL_CLEARANCE = 0.16    # Зазор по ширине и высоте разъёма
TOP_COMPONENT_CLEAR = 0.30  # Запас над разъёмом под крышку

USBC_RES = 64             # Сегменты на четверть дуги прорези
NOSE_SEGMENTS = 256       # Сегменты окружности носика

# Расчётные размеры

APERTURE_W = USBC_SHELL_W + SHELL_CLEARANCE
APERTURE_H = USBC_SHELL_H + SHELL_CLEARANCE
APERTURE_R = USBC_SHELL_R                          # Радиус ограничивается в rounded_rect_polygon

POCKET_W = PCB_W + PCB_W_CLEARANCE

# Совмещаем центр разъёма с Z = 0.
SHELL_TOP_Z = +USBC_SHELL_H / 2.0
SHELL_BOT_Z = -USBC_SHELL_H / 2.0
PCB_TOP_Z = SHELL_BOT_Z                            # Разъём установлен сверху платы
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

# Геометрия

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
    """Призма со скруглёнными углами вдоль оси Y."""
    poly = rounded_rect_polygon(width, height, radius, segments)
    solid = Manifold.extrude(CrossSection([poly]), length)
    solid = solid.translate((0.0, 0.0, -length / 2.0))
    solid = solid.rotate((90.0, 0.0, 0.0))
    return solid

# Сборка

def build():
    y_front = -HOUSING_D / 2.0
    y_tip = y_front - NOSE_LEN
    y_back = +HOUSING_D / 2.0
    y_pcb_front = y_tip + USBC_SHELL_PAST_PCB + PCB_REGISTER_OFFSET_Y

    # Прорезь проходит от носика за край платы и соединяется с карманом.
    aperture_len = max(
        NOSE_LEN + 0.55,
        y_pcb_front + APERTURE_MERGE_INTO_POCKET_Y - y_tip,
    )
    # Удлиняем корпус только спереди; носик и карман остаются на месте.
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
    # Срезаем носик сверху и снизу по высоте корпуса.
    nose_clip = (
        Manifold.cube(
            (NOSE_OD + 2.0, NOSE_LEN + 0.4, HOUSING_H),
            center=True,
        ).translate((0.0, y_front - NOSE_LEN / 2.0, 0.0))
    )
    nose = nose_full ^ nose_clip  # В manifold3d оператор ^ означает пересечение.

    body = outer + nose

    # Прорезь USB-C должна соединяться с карманом без перегородки.
    aperture = rounded_prism(APERTURE_W, APERTURE_H, aperture_len, APERTURE_R)
    aperture = aperture.translate((0.0, y_tip + aperture_len / 2.0, 0.0))

    pocket_y_start = y_pcb_front - POCKET_FRONT_OVERLAP_Y
    pocket_y_end = y_back + 0.50                      # Карман выходит за заднюю грань.
    pocket_len = pocket_y_end - pocket_y_start
    pocket = Manifold.cube((POCKET_W, pocket_len, POCKET_HEIGHT), center=True)
    pocket = pocket.translate(
        (0.0, (pocket_y_start + pocket_y_end) / 2.0, POCKET_CENTER_Z)
    )

    return body - aperture - pocket

# Экспорт

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
