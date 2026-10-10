# 01 · Design

## Netlist and build (no solder)

<img src="../../docs/assets/power-flow.svg" width="100%" alt="Power path">

| Net | Members | Joined by |
|---|---|---|
| VIN | J1 `+` screw, fuse lead A | screw terminal |
| VIN_F | fuse lead B, e-stop NC 1 | screw terminal |
| MOTION (red wire) | e-stop NC 2 → out of the J3 slot → over-travel switch COM–NC (from stage 04) → E4 VIN `+`; 24 V sense lead under the same E4 screw | screw terminals only |
| GND (black wire) | J1 `−` screw → E4 VIN `−`; sense ground lead under the same E4 screw | screw terminals |
| OPTO_A | 24 V sense row, 10 k, PC817 pin 1 (breadboard, controller case) | breadboard |
| ISO_C / ISO_E | PC817 pin 4 → Pico GP7, pin 3 → Pico GND | male–female jumpers |

J1 = PWR-03 jack adapter (screw block), fuse = PWR-04 inline holder with 3.15 A T, e-stop = PWR-13 (screw terminals). Opto LED ≈ 2.3 mA at 24 V; Pico GP7 reads low when 24 V MOTION is on. The sense circuit sits on the breadboard in the controller case (M10.4), fed from the E4's VIN screws, so the power box holds only the jack, fuse and e-stop. Box at (220, −220): one 1 m 18 AWG pair reaches the over-travel switch near 20° and the E4.

**Trade-off (no solder):** no reverse-polarity MOSFET, surge (TVS) diode or bulk capacitor. The adapter's plug is keyed and centre-positive, the jack's screws are marked + / −, and M06.1 checks the sign with the meter before the E4 is connected; the E4 has its own input capacitors. Off = e-stop pressed or adapter unplugged (no rocker).

### Build

1. Self-tap 4 × M3 × 10 into the box posts once. Jack adapter into the +X slot, e-stop in the lid.
2. Strip 8 mm for screws, 11 mm for lever connectors; twist strands; tug-test every wire.
3. Lid M3 × 10, snug (it's plastic); box to base: 4 × #8 wood screws through the floor bosses.

## 3D parts

| Part | Source |
|---|---|
| Box 120 × 80 × 60, lid (PWR-18) | `tools/cad/parts.py`: walls 2.4 mm (60 mm tall: the e-stop's contact block reaches 48.7 mm below the lid), lid 3.2 mm, M3 self-tap posts (`M3_TAP`), 6 mm floor bosses for #8 wood screws, jack slot (lid holds the adapter), black-wire and red-wire (J3) slots, Ø22.3 e-stop hole in lid |
| Adapter GST60A24 | STEP on [Mouser](https://www.mouser.com/ProductDetail/MEAN-WELL/GST60A24-P1J?qs=odmYgEirbwyH6XaEPxnETQ%3D%3D) [P1] |
| Jack adapter, e-stop | model from the product pages [P45][P16] |

## Results

(fill in)
