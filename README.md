# ThinkPad X220 USB-C power jack housing

Author: [@dayanegosha](https://github.com/dayanegosha)

What you get here: **`stl/X220_USB_C_adapter.stl`** (ready to print), this **README**, and **`src/adapter.py`** if you want to change numbers and build a new STL yourself. Nothing else is required to use the model.

---

## Just want to print it?

You do not have to read the rest of this file.

1. Download [`stl/X220_USB_C_adapter.stl`](stl/X220_USB_C_adapter.stl).
2. Print it in **PETG** or **ABS** (PLA works but softens sooner when the board gets warm).
3. Put the **flat open pocket** on the build plate so the USB-C slot prints lying down — no supports needed.
4. Buy a **PDC004** (or PDC004-20V style) USB-C PD trigger board with the usual WITRN-sized PCB (~16.3 × 10.2 mm), solder your X220 DC cable to it, slide the board in from the back, glue or pot the wires if you like, and clip it into the palmrest like the original yellow jack.

If anything is tight or loose, open `src/adapter.py`, tweak the constants at the top, and run [Rebuild](#rebuild).

---

## Technical drawings (PNG)

Images in `docs/`:

- [`drawing_views.png`](docs/drawing_views.png) — six orthographic views  
- [`drawing_isometric.png`](docs/drawing_isometric.png) — two isometrics  

*(This repo does not ship camera photos of the printed part; add your own under `docs/` if you want them in a fork.)*

---

## Table of contents

- [English](#english)
- [Русский](#русский)
- [License](#license)

---

# English

## What this is

A small **3D-printable housing** for the ThinkPad **X220** (and similar) palmrest **DC jack slot**. It holds a **USB-C PD trigger board** (PDC004 family) so you can use a normal **USB-C charger** at **20 V**. **No USB data** — only power, like the original round jack.

You keep the **original cable and motherboard plug**; you replace the yellow plastic jack body and solder the wires to the trigger board.

## Outer size (from `adapter.py`)

| | |
| --- | ---: |
| Width × height (X × Z) | **12.0 × 9.7 mm** |
| Depth into laptop (rectangular slug) | **11.2 mm** |
| Extra plastic on the ring side only | **+0.7 mm** |
| Ring | **Ø9.7 mm**, **1.0 mm** proud of the front face |
| Rough length nose tip → back | **~12.2 mm** |
| USB-C cutout in the print (with clearance) | **9.16 × 3.36 mm** (corner radius 1.6 mm) |
| Pocket for the board (approx.) | **10.35 × ~11.8 × 4.55 mm** |

## Bill of materials

| Qty | Item |
| ---: | --- |
| 1 | **PDC004** (or clone) ~**16.3 × 10.2 × 1.0 mm** PCB — check the seller’s drawing |
| 1 | [`stl/X220_USB_C_adapter.stl`](stl/X220_USB_C_adapter.stl) |
| 1 | Original X220/X230 **DC harness** |
| — | Wire, solder, flux, small iron tip, heat-shrink, optional epoxy or hot glue |

## Print settings (defaults)

| | |
| --- | --- |
| Material | **PETG** or **ABS** |
| Nozzle | 0.4 mm |
| Layer | 0.12–0.16 mm |
| Walls | 3 |
| Infill | 100 % |
| Top/bottom | 4 layers each |
| Supports | **Off** |
| Orientation | **Open pocket on the bed** — USB slot horizontal |

Thin walls: use a calibrated printer and at least three perimeters.

## Assembly (short)

1. Print; clean the pocket if needed.  
2. Desolder the old jack from the yellow housing; keep the cable.  
3. Solder **OUT+** / **OUT−** on the PDC004 like the old jack.  
4. Slide the board in **front first** until it stops; USB shell lines up with the slot.  
5. Dry-fit in the chassis.  
6. Glue or pot the back if you want.  
7. Close the palmrest.

**ID wire:** if you get “non-genuine battery” or slow charge, a **10 kΩ resistor from ID to ground** on the board side often fixes it.

## Charger safety

Use a **65 W+** USB-C PD brick that is **known good** for ThinkPad mods (e.g. lists in [mikepdiy/thinkpad-mod](https://github.com/mikepdiy/thinkpad-mod)). Avoid bad adapters that can send 20 V before negotiation.

## Repo layout

```
thinkpad-x220-usb-c-adapter/
├── LICENSE
├── README.md
├── requirements.txt
├── stl/
│   └── X220_USB_C_adapter.stl
├── src/
│   └── adapter.py          # parameters + STL export
└── docs/
    ├── drawing_views.png
    └── drawing_isometric.png
```

## Rebuild

Only needed if you edit `src/adapter.py`:

```bash
cd thinkpad-x220-usb-c-adapter   # or your path
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/adapter.py            # writes stl/X220_USB_C_adapter.stl
```

---

# Русский

## Что это

Корпус под разъём питания в паз palmrest **ThinkPad X220**. Плата **PDC004**, питание с **USB-C PD 20 В**. **Данных по USB нет** — только питание.

Жгут с материнки оставляем, меняем жёлтую оболочку разъёма и припаиваемся к PDC004.

## Размеры

Те же числа, что в таблице выше (из `adapter.py`).

## Что нужно

Плата PDC004, напечатанный STL, родной жгут, провод/пайка/усадка, по желанию клей.

## Печать и сборка

Кратко те же шаги, что в английском разделе: карманом на стол, без поддержек, пайка OUT+/OUT−, провод ID при необходимости через **10 кОм на землю**, зарядки только из проверенных списков.

## Пересборка STL

Те же команды, что в разделе [Rebuild](#rebuild).

---

## License

Full text: [`LICENSE`](LICENSE) (**MIT**).

Short version: you may **use, change, print, share, and sell** this; keep the **copyright line** in copies. Everything is **as-is**; the author is **not liable** for damage. Not affiliated with Lenovo. **ThinkPad** is a Lenovo trademark.

---

*Кратко по-русски про лицензию: MIT — можно пользоваться и распространять, строку с копирайтом оставлять, всё «как есть», автор не отвечает за последствия.*
