"""PARTS.md decisions are read the way the header says."""
import parts_doc

DOC = """## 01
- [x] **PWR-01** adapter — 1 × $19.40 · status: suggested
  - *why:* ignored
  - note: fine
  - paid:
- [ ] **PWR-02** cord · status: agreed
- [ ] **PWR-03** jack · status: swap
  - note: locking jack
- [ ] **PWR-04** fuse holder · status: suggested
  - paid: $3.10
- [ ] **PWR-05** fuse · status: banana
- [x] **PWR-06** MOSFET · status: have
"""


def test_read_doc_rules():
    d = parts_doc.read_doc(DOC)
    assert d["PWR-01"] == {"status": "agreed", "note": "fine", "paid": ""}     # ticked = agreed
    assert d["PWR-02"]["status"] == "suggested"                                # unticked agreed = back to suggested
    assert d["PWR-03"] == {"status": "swap", "note": "locking jack", "paid": ""}
    assert d["PWR-04"]["status"] == "ordered" and parts_doc.money(d["PWR-04"]["paid"]) == "3.10"  # paid = ordered
    assert d["PWR-05"]["status"] == "suggested"                                # unknown word -> suggested (check flags it)
    assert d["PWR-06"]["status"] == "have"


def test_to_buy():
    r = lambda t, s: {"Type": t, "Status": s}  # noqa: E731
    assert parts_doc.to_buy(r("Purchase", "suggested")) and parts_doc.to_buy(r("Purchase", "agreed"))
    assert not parts_doc.to_buy(r("Purchase", "have")) and not parts_doc.to_buy(r("Purchase", "skip"))
    assert parts_doc.to_buy(r("Optional", "agreed")) and not parts_doc.to_buy(r("Optional", "suggested"))
