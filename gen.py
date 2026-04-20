#!/usr/bin/env python3
"""Generate static JSON fixtures for the HR mock WMS API."""
import json, os, random

# Internal short keys 101..125 map to realistic 6-digit itemIds and
# "xxx-xxxx-xxx" style item names (a few with /A or /B revs).
# Internal key -> onHand (seeded for deterministic test outputs).
ITEMS = {
    101: -10, 102: -5, 103: -1, 104: 0, 105: 0,
    106: 3, 107: 8, 108: 15, 109: 40, 110: 80,
    111: -8, 112: -3, 113: 0, 114: 5, 115: 12,
    116: 25, 117: 50, 118: -2, 119: 1, 120: 18,
    121: -6, 122: 0, 123: 7, 124: 30, 125: 100,
}

# Deterministic remap: internal key -> public 6-digit itemId + xxx-xxxx-xxx name.
_rng = random.Random(42)
_six_digit_pool = _rng.sample(range(100000, 1000000), len(ITEMS))
ITEM_ID_MAP = dict(zip(sorted(ITEMS.keys()), _six_digit_pool))

def _gen_name():
    return f"{_rng.randint(100, 999)}-{_rng.randint(1000, 9999)}-{_rng.randint(100, 999)}"

ITEM_NAMES = {k: _gen_name() for k in sorted(ITEMS.keys())}
# Sprinkle /A or /B revs on a few items.
for k, rev in [(103, "/A"), (110, "/A"), (117, "/B"), (122, "/A"), (125, "/B")]:
    ITEM_NAMES[k] += rev

SUPPLIERS = ["Acme Supply Co", "Globex Industrial", "Initech Components",
             "Hooli Hardware", "Meridian Materials"]

# (id, daysLate, [(itemId, orderedQty, receivedQty), ...])
POS = [
    (1001, 22,  [(101, 10, 0)]),
    (1002, 14,  [(105, 8, 3), (110, 100, 100)]),
    (1003, 45,  [(104, 20, 10)]),
    (1004, 5,   [(102, 7, 2)]),
    (1005, 0,   [(103, 4, 0)]),
    (1006, -3,  [(101, 5, 0)]),
    (1007, 80,  [(106, 10, 5)]),
    (1008, 18,  [(107, 3, 1), (108, 5, 2)]),
    (1009, 10,  [(104, 3, 0)]),
    (1010, 33,  [(105, 15, 5)]),
    (1011, 7,   [(108, 5, 4)]),
    (1012, 50,  [(102, 12, 2)]),
    (1013, 90,  [(109, 2, 0)]),
    (1014, 25,  [(101, 3, 3), (103, 8, 3)]),
    (1015, 60,  [(106, 5, 2)]),
    (1016, 2,   [(110, 50, 0)]),
    (1017, 40,  [(105, 20, 10), (107, 4, 1)]),
    (1018, 150, [(102, 8, 2)]),
    (1019, 12,  [(104, 5, 0)]),
    (1020, 35,  [(105, 6, 1)]),
    (1021, 180, [(111, 20, 5)]),
    (1022, 8,   [(112, 6, 0)]),
    (1023, 1,   [(113, 10, 5)]),
    (1024, 120, [(114, 30, 10)]),
    (1025, 55,  [(115, 8, 0)]),
    (1026, 20,  [(116, 15, 10), (117, 5, 2)]),
    (1027, 0,   [(118, 3, 0)]),
    (1028, 3,   [(119, 12, 5)]),
    (1029, 100, [(120, 25, 0)]),
    (1030, 28,  [(121, 10, 4)]),
    (1031, 65,  [(122, 7, 2), (123, 4, 1)]),
    (1032, 42,  [(124, 20, 18)]),
    (1033, -5,  [(125, 100, 0)]),
    (1034, 11,  [(111, 15, 10)]),
    (1035, 75,  [(112, 4, 0)]),
    (1036, 6,   [(118, 8, 3)]),
    (1037, 9,   [(121, 5, 0)]),
    (1038, 30,  [(113, 20, 5), (122, 3, 0)]),
    (1039, 160, [(103, 6, 0)]),
    (1040, 17,  [(119, 4, 1)]),
]

PER_PAGE = 10
os.makedirs("api/purchase_orders/page", exist_ok=True)
os.makedirs("api/inventory", exist_ok=True)

pages = [POS[i:i + PER_PAGE] for i in range(0, len(POS), PER_PAGE)]
for i, page_pos in enumerate(pages, 1):
    payload = {
        "page": i, "per_page": PER_PAGE, "total": len(POS),
        "total_pages": len(pages),
        "data": [{
            "id": poid,
            "poNumber": f"USPO{poid:05d}",
            "supplierId": (poid % 5) + 1,
            "supplierName": SUPPLIERS[poid % 5],
            "daysLate": dl,
            "status": "OPEN",
            "lines": [{
                "lineId": j + 1,
                "itemId": ITEM_ID_MAP[iid],
                "itemName": ITEM_NAMES[iid],
                "orderedQty": o, "receivedQty": r,
            } for j, (iid, o, r) in enumerate(lines)],
        } for poid, dl, lines in page_pos],
    }
    with open(f"api/purchase_orders/page/{i}.json", "w") as f:
        json.dump(payload, f, indent=2)

used_items = sorted({iid for _, _, lines in POS for iid, _, _ in lines})
for iid in used_items:
    public_id = ITEM_ID_MAP[iid]
    with open(f"api/inventory/{public_id}.json", "w") as f:
        json.dump({"data": [{
            "itemId": public_id,
            "itemName": ITEM_NAMES[iid],
            "onHand": ITEMS[iid],
            "orgCode": "ORG-001",
        }]}, f, indent=2)

print(f"Wrote {len(pages)} PO pages and {len(used_items)} inventory files.")