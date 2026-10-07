# OpenGonio panel + sensor hub - MicroPython for the Raspberry Pi Pico [R42][R43]
# SPDX-License-Identifier: GPL-3.0-or-later
#
# USB serial line protocol (laptop <-> hub)
#   out: BTN HOME|START|STOP|LIGHT|NEXT   POWER 0|1   ENC a b c d   PONG OpenGonio-hub 1 POWER n   ERR <msg>
#   in : BAND 0-7 | BAND OFF | ENC? | POWER? | PING | SHOW line1|line2|line3 | SPEC?
#   SPEC? -> 'SPEC f1 f2 f3 f4 f5 f6 f7 f8 clear nir' from an AS7341 (0x39) on the first I2C pair (shared with the OLED).
# Same protocol on USB (laptop) and on UART0 GP0 TX / GP1 RX (Pi Zero station, 3.3 V, 115200).
# Optional SSD1306 128x64 OLED at 0x3C on the first I2C pair (GP17 SCL, GP16 SDA); install: mpremote mip install ssd1306
# Pins (GP numbers): buttons 2-6 to GND, MOTION_SENSE 7 (PC817 transistor, low = 24 V on), LED bank 8-15 -> ULN2803A,
# optional AS5600 encoders on SoftI2C pairs (16,17) (18,19) (20,21) (26,27).
import sys
import time
import uselect
from machine import UART, Pin, SoftI2C

BUTTONS = {"HOME": 2, "START": 3, "STOP": 4, "LIGHT": 5, "NEXT": 6}
SENSE_PIN = 7
BAND_PINS = list(range(8, 16))
I2C_PAIRS = [(17, 16), (19, 18), (21, 20), (27, 26)]   # (scl, sda)
AS5600 = 0x36
DEBOUNCE_MS = 30

btn = {n: Pin(p, Pin.IN, Pin.PULL_UP) for n, p in BUTTONS.items()}
last = {n: 1 for n in BUTTONS}
since = {n: 0 for n in BUTTONS}
sense = Pin(SENSE_PIN, Pin.IN, Pin.PULL_UP)
bands = [Pin(p, Pin.OUT, value=0) for p in BAND_PINS]
led = Pin(25, Pin.OUT)
buses = [SoftI2C(scl=Pin(s), sda=Pin(d), freq=100_000) for s, d in I2C_PAIRS]
poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
try:
    import ssd1306
    oled = ssd1306.SSD1306_I2C(128, 64, buses[0])
except Exception:                           # no display fitted: everything else still works
    oled = None


AS = 0x39                                   # AS7341 11-channel spectral sensor; register map per the ams datasheet


def as_w(reg, val):
    buses[0].writeto_mem(AS, reg, bytes([val]))


def as_r(reg, n=1):
    return buses[0].readfrom_mem(AS, reg, n)


SMUX_LOW = (0x30, 0x01, 0x00, 0x00, 0x00, 0x42, 0x00, 0x00, 0x50, 0x00,
            0x00, 0x00, 0x20, 0x04, 0x00, 0x30, 0x01, 0x50, 0x00, 0x06)   # F1-F4, clear, NIR -> ADC0-5
SMUX_HIGH = (0x00, 0x00, 0x00, 0x40, 0x02, 0x00, 0x10, 0x03, 0x50, 0x10,
             0x03, 0x00, 0x00, 0x00, 0x24, 0x00, 0x00, 0x50, 0x00, 0x06)  # F5-F8, clear, NIR -> ADC0-5


def as_read6(smux):
    as_w(0x80, 0x01)                         # power on, measurement off
    as_w(0xAF, 0x10)                         # SMUX command: write config from RAM
    for i, v in enumerate(smux):
        as_w(i, v)
    as_w(0x80, 0x11)                         # SMUXEN
    t = time.ticks_ms()
    while as_r(0x80)[0] & 0x10:
        if time.ticks_diff(time.ticks_ms(), t) > 500:
            raise OSError("AS7341 SMUX timeout")
    as_w(0x80, 0x03)                         # spectral measurement on
    t = time.ticks_ms()
    while not as_r(0xA3)[0] & 0x40:          # AVALID
        if time.ticks_diff(time.ticks_ms(), t) > 2000:
            raise OSError("AS7341 timeout")
    d = as_r(0x95, 12)
    as_w(0x80, 0x01)
    return [d[2 * i] | (d[2 * i + 1] << 8) for i in range(6)]


def spectral():
    as_w(0x81, 29)                           # ATIME
    as_w(0xCA, 0xE7); as_w(0xCB, 0x03)       # ASTEP 999 -> (29+1)(999+1)2.78 us = 83 ms
    as_w(0xAA, 6)                            # gain 32x; lower it if a channel reads 65535
    lo, hi = as_read6(SMUX_LOW), as_read6(SMUX_HIGH)
    return lo[:4] + hi[:4] + [lo[4], lo[5]]  # F1..F8, clear, NIR


def out(msg):
    print(msg)
    uart.write(msg + "\n")


def show(lines):
    if oled is None:
        return
    oled.fill(0)
    for i, t in enumerate(lines[:6]):
        oled.text(t[:16], 0, i * 11)
    oled.show()


def band(n):
    for i, p in enumerate(bands):
        p.value(1 if i == n else 0)        # only one band on at a time


def read_angle(bus):
    try:
        hi, lo = bus.readfrom_mem(AS5600, 0x0C, 2)
        return (((hi & 0x0F) << 8) | lo) * 360.0 / 4096.0
    except OSError:
        return float("nan")


def motion_power():
    return 0 if sense.value() else 1        # opto pulls GP7 low when 24 V MOTION is present


def handle(line):
    if line.strip().upper().startswith("SHOW"):
        show(line.strip()[4:].strip().split("|"))
        return
    parts = line.strip().upper().split()
    if not parts:
        return
    try:
        if parts[0] == "PING":
            out("PONG OpenGonio-hub 2 POWER %d" % motion_power())
        elif parts[0] == "POWER?":
            out("POWER %d" % motion_power())
        elif parts[0] == "BAND":
            n = None if parts[1] == "OFF" else int(parts[1])
            if n is not None and not 0 <= n < len(bands):
                raise ValueError("band out of range")
            band(n)
        elif parts[0] == "SPEC?":
            out("SPEC " + " ".join(str(v) for v in spectral()))
        elif parts[0] == "ENC?":
            out("ENC " + " ".join("%.3f" % read_angle(b) for b in buses))
        else:
            out("ERR unknown " + parts[0])
    except Exception as e:                  # bad input must never stop the hub
        out("ERR %s" % e)


power = motion_power()
out("POWER %d" % power)
show(["OpenGonio", "ready", "", "HOME START STOP", "LIGHT NEXT"])
buf = ""
ubuf = ""
t_led = time.ticks_ms()
while True:
    now = time.ticks_ms()
    for name, pin in btn.items():          # debounced falling edge = press
        v = pin.value()
        if v != last[name] and time.ticks_diff(now, since[name]) > DEBOUNCE_MS:
            since[name] = now
            last[name] = v
            if v == 0:
                out("BTN " + name)
    if motion_power() != power:
        power = motion_power()
        out("POWER %d" % power)
        if not power:
            band(None)
    while poll.poll(0):
        ch = sys.stdin.read(1)
        if ch in "\r\n":
            handle(buf)
            buf = ""
        else:
            buf += ch
    while uart.any():
        ch = uart.read(1).decode()
        if ch in "\r\n":
            handle(ubuf)
            ubuf = ""
        else:
            ubuf += ch
    if time.ticks_diff(now, t_led) > 500:   # heartbeat
        led.toggle()
        t_led = now
    time.sleep_ms(2)
