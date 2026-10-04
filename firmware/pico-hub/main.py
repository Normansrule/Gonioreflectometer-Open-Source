# OpenGonio panel + sensor hub - MicroPython for the Raspberry Pi Pico [R42][R43]
# SPDX-License-Identifier: GPL-3.0-or-later
#
# USB serial line protocol (laptop <-> hub)
#   out: BTN HOME|START|STOP|LIGHT|NEXT   POWER 0|1   ENC a b c d   PONG OpenGonio-hub 1 POWER n   ERR <msg>
#   in : BAND 0-7 | BAND OFF | ENC? | POWER? | PING
# Pins (GP numbers): buttons 2-6 to GND, MOTION_SENSE 7 (PC817 transistor, low = 24 V on), LED bank 8-15 -> ULN2803A,
# optional AS5600 encoders on SoftI2C pairs (16,17) (18,19) (20,21) (26,27).
import sys
import time
import uselect
from machine import Pin, SoftI2C

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
    parts = line.strip().upper().split()
    if not parts:
        return
    try:
        if parts[0] == "PING":
            print("PONG OpenGonio-hub 1 POWER %d" % motion_power())
        elif parts[0] == "POWER?":
            print("POWER %d" % motion_power())
        elif parts[0] == "BAND":
            n = None if parts[1] == "OFF" else int(parts[1])
            if n is not None and not 0 <= n < len(bands):
                raise ValueError("band out of range")
            band(n)
        elif parts[0] == "ENC?":
            print("ENC " + " ".join("%.3f" % read_angle(b) for b in buses))
        else:
            print("ERR unknown " + parts[0])
    except Exception as e:                  # bad input must never stop the hub
        print("ERR %s" % e)


power = motion_power()
print("POWER %d" % power)
buf = ""
t_led = time.ticks_ms()
while True:
    now = time.ticks_ms()
    for name, pin in btn.items():          # debounced falling edge = press
        v = pin.value()
        if v != last[name] and time.ticks_diff(now, since[name]) > DEBOUNCE_MS:
            since[name] = now
            last[name] = v
            if v == 0:
                print("BTN " + name)
    if motion_power() != power:
        power = motion_power()
        print("POWER %d" % power)
        if not power:
            band(None)
    while poll.poll(0):
        ch = sys.stdin.read(1)
        if ch in "\r\n":
            handle(buf)
            buf = ""
        else:
            buf += ch
    if time.ticks_diff(now, t_led) > 500:   # heartbeat
        led.toggle()
        t_led = now
    time.sleep_ms(2)
