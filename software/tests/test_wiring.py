"""Wiring source (docs/wiring.yaml): pins agree with the hub firmware and the board maps, no header pin used twice."""
import copy

import wiring


def test_wiring_is_consistent():
    assert wiring.check() == []


def test_header_maps_match_the_espressif_guide():
    assert len(wiring.J1) == len(wiring.J3) == 22
    assert wiring.hub_label("J1", 4) == "GPIO4" and wiring.hub_label("J1", 10) == "GPIO17"
    assert wiring.hub_label("J3", 16) == "GPIO48" and wiring.hub_label("J3", 17) == "GPIO47"
    assert wiring.hub_label("J1", 22) == "GND" and wiring.hub_label("J1", 1) == "3V3"


def test_skr_pin_labels():
    assert wiring.skr_label("X", "1-4") == "2B 1B 1A 2A"
    assert wiring.skr_label("E0-STOP", "1") == "IO16"
    assert wiring.skr_label("HE", "IO23") == "IO23" and wiring.skr_label("POWER", "12/24V") == "12/24V"
    assert wiring.skr_label("X", "5") == ""


def _mutate(fn):
    w = copy.deepcopy(wiring.load())
    fn(w)
    return wiring.check(w)


def _row(w, first):
    return next(r for g in w["groups"] for r in g["rows"] if r[0] == first)


def test_wrong_button_pin_is_caught():
    errs = _mutate(lambda w: _row(w, "KPA:key 1").__setitem__(1, "HUB:J1-5"))
    assert any("HOME" in e for e in errs) and any("used twice" in e for e in errs)


def test_wrong_sense_pin_and_unknown_pin_are_caught():
    assert any("SENSE_PIN" in e for e in _mutate(lambda w: _row(w, "OPTO:OUT").__setitem__(1, "HUB:J1-11")))
    assert any("no pin" in e for e in _mutate(lambda w: _row(w, "ES4:S / G / V (by label)").__setitem__(1, "SKR:X-STOP.1-4")))


def test_alternatives_may_share_pins_but_others_may_not():
    assert wiring.check() == []                                    # OLED reuses the AS7341 pins by design
    errs = _mutate(lambda w: _row(w, "FAN:red (+)").__setitem__(1, "HUB:J3-4"))
    assert any("J3-4" in e for e in errs)


def test_readme_anchor_matches_github():
    assert wiring.anchor("1 · Power: wall adapter, jack, e-stop") == "1--power-wall-adapter-jack-e-stop"


def test_every_section_has_an_animated_pin_diagram():
    w = wiring.load()
    for i, g in enumerate(w["groups"], 1):
        txt, width = wiring.group_svg(g, w["parts"])
        assert width >= 1000 and txt.startswith("<svg")
        wired = [n for n, r in enumerate(g["rows"], 1) if r[1] != "-"]
        assert all(f">{n}</text>" in txt for n in wired), g["title"]            # every wire carries its table row number
        assert ("<animateMotion" in txt) != bool(g.get("blocked")), g["title"]  # blocked section: drawn, not animated
        assert f"wiring-{i:02d}.svg" in wiring.readme_block(w)
