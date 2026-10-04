# Controller module · Phase 1 · M1.2

<img src="../../docs/assets/architecture.svg" width="100%" alt="Control architecture">

## 1. Purpose and interfaces

Motion control for all four axes plus a physical button panel. The laptop drives everything; precision comes from FluidNC step generation (≤ 0.028°/microstep on every axis) and optical homing [R1].

| Part | Role | Link to laptop |
|---|---|---|
| FYSETC E4 + FluidNC | 4 × TMC2209, homing inputs, light MOSFETs, PAUSE (feed hold) | USB · WiFi (telnet :23, WebUI) · Bluetooth serial |
| Raspberry Pi Pico + MicroPython | HOME/START/STOP/LIGHT/NEXT, e-stop sense, Phase 5 LED bank | USB |

| Port | Goes to |
|---|---|
| E4 VIN | J2 (24 V MOTION, power module) |
| E4 X/Y/Z/E motor | M4 / M3 / M2 / M1 |
| E4 X/Y/Z-min, TH0 | home flags M4, M3, M2, M1 |
| E4 TH1 | PAUSE button |
| E4 HE0 / BED / FAN | white light / LED bank driver / optional fan |
| Pico GP2–6 | panel buttons; GP7 ← J4 isolated sense; GP8–15 → ULN2803A (Phase 5) |
| Mount | OG-40 at (−220, 220); panel on the case front |

Phases 3–4 only plug motors and flags into the Z and E sockets and raise `installed_phase`.

## 2. BOM — $55.99 buy-all / $39.00 with own stock

| ID | Part | Qty | USD | Ref |
|---|---|---:|---:|---|
| CTL-01 | FYSETC E4 (WiFi + BT) | 1 | 32.00 | [C1][C2][C3] |
| CTL-02 | Raspberry Pi Pico | 1 | 4.00 | [C5][C6] |
| CTL-03 | USB cable for E4 | 1 | 3.00 est. | — |
| CTL-04 | USB-A to micro-B 1 m (Pico) | 1 | 3.00 est. | [C7] |
| CTL-05 | 12 mm momentary buttons | 6 | 0.50 est. | — |
| CTL-06 | JST-XH pre-crimped kit | 1 | 9.99 est. | [P22] |
| CTL-07 | Pin headers | 1 | 1.00 est. | — |
| CTL-08 | 40 mm 24 V fan (optional) | — | — | — |

STEP: Pico confirmed [C6]; E4 not published — model 90 × 67 mm from the README drawing [C1].

## 3. Onshape — Part Studio `CTL`

Variables: `#e4` 90 × 67 mm (holes from [C1]), `#pico` 51 × 21 mm (holes 47 × 11.4, Ø2.1 [C6]), `#btn_d` 12.2, `#case` 150 × 110 × 45.

1. Tray with E4 standoffs (M3 inserts) and Pico standoffs (M2 self-tap).
2. Front panel: 6 button holes in a row, labels HOME · START · STOP · LIGHT · NEXT · PAUSE (PAUSE red ring).
3. Side slots: USB (E4, Pico), JST exits; top vents over the drivers.
4. Floor: OG-40.

Print PETG, 0.2 mm, 4 walls, panel face down.

## 4. Assembly

1. Solder headers to the Pico. Mount E4 and Pico in the tray.
2. Buttons: one leg each to Pico GP2–GP6, other legs to Pico GND. PAUSE: E4 TH1 signal ↔ TH1 GND.
3. Home flags (TCST2103): VCC/GND/OUT to X/Y/Z-min; M1 flag to TH0.
4. J4 (opto transistor) from the power module → Pico GP7 and GND.
5. Common ground: laptop USB grounds both boards; J2 GND joins the E4.
6. Flash both boards: [`firmware/README.md`](../../firmware/README.md).

## 5. Wiring

| From | To |
|---|---|
| J2 + / − | E4 VIN + / − (check silkscreen) |
| M4 / M3 / M2 / M1 motors | E4 X / Y / Z / E sockets |
| Flags M4 / M3 / M2 / M1 | E4 X-min (GPIO34) / Y-min (35) / Z-min (15) / TH0 (36) |
| PAUSE | E4 TH1 (GPIO39), to GND |
| White COB driver −Vin | E4 HE0 (GPIO2) low side; +Vin from VIN |
| Buttons HOME…NEXT | Pico GP2…GP6, to GND |
| J4-1 / J4-2 | Pico GP7 / Pico GND (opto transistor) |

## 6. Firmware and software

- E4: [`firmware/fluidnc/config.yaml`](../../firmware/fluidnc/config.yaml) — degrees as units, M62/M63 lights, PAUSE on feed hold.
- Pico: [`firmware/pico-hub/main.py`](../../firmware/pico-hub/main.py) — debounced buttons, `POWER`, `BAND`, `ENC?`.
- Laptop: `opengonio home`, `opengonio move M4=60 M3=30`, `opengonio panel` (buttons → actions).

## 7. Acceptance test

| # | Test | Pass |
|---|---|---|
| C1 | `?` over USB, then WiFi, then BT build | `<Idle\|MPos:…>` on each |
| C2 | Block each flag by hand | `Pn:` shows the right axis |
| C3 | `$HX`, `$HY` | each stops on its flag, MPos = 20 / −180 |
| C4 | Hub `PING`; press each button | `PONG…`; correct `BTN` line |
| C5 | `opengonio panel`: HOME, LIGHT, NEXT, STOP | home runs, light toggles, one pose, Alarm |
| C6 | PAUSE during a move, laptop unplugged from the hub | motion holds; `~` resumes |
| C7 | E-stop, then release | `POWER 0`; on `POWER 1` the panel sends `$MI`; moves refused until re-home |
| C8 | 30 min moves at 0.8 A | E4 driver area ≤ 80 °C (else fit the fan) |

## 8. Safety

Never hot-plug motors with 24 V on. Check motor coil pairs (~1.6 Ω) before connecting. No 24 V wire touches the Pico; J4 is the opto transistor only. For full isolation use the WiFi/BT link instead of E4 USB.
