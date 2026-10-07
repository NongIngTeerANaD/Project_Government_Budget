import json
from pathlib import Path

import app as app_module
import config as C
from utils.payload import build_payload

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def test_http_endpoints_and_assets():
    c = app_module.server.test_client()
    assert c.get("/").status_code == 200
    layout = c.get("/_dash-layout")
    assert layout.status_code == 200 and "payload" in layout.get_data(as_text=True)
    for f in ("d3.min.js", "dashboard.js", "dashboard.css"):
        assert (ASSETS / f).stat().st_size > 1000
        assert c.get(f"/assets/{f}").status_code == 200
    assert len(c.get("/_dash-dependencies").get_json()) >= 1


def test_payload_shape_and_real_values():
    p = build_payload()
    json.dumps(p, ensure_ascii=False)  # must be JSON-serialisable (no NaN objects)
    assert len(p["prov"]) == 77 and p["years"] == list(C.FISCAL_YEARS)
    assert len(p["geo"]["features"]) == 77
    kk = next(x for x in p["prov"] if x["th"] == "ขอนแก่น")
    assert kk["cdy"]["2023"] == {"4": 9, "5": 108, "6": 255}
    assert "2019" not in kk["cdy"]  # no real complaint data before 2020 -> never filled in
    assert set(kk["dom"]["2023"]) == {"1", "2", "3", "4", "5", "6"}
    assert p["flags"]["gpp"] and p["flags"]["complaints"]
    assert p["flags"]["budget"] and not p["flags"]["outcome"]  # real FY2566 budget; no real outcome data yet
    assert kk["b"][:4] == [None] * 4 and kk["b"][4] > 0  # budget only exists for 2023, never filled in
    assert kk["dom"]["2021"]["1"]["b"] is None and kk["dom"]["2023"]["1"]["o"] is None
    assert p["meta"]["budget_years"] == [2023]
    assert all(s["links"] for s in p["sources"])


def test_ui_has_per_chart_data_references():
    js = (ASSETS / "dashboard.js").read_text(encoding="utf-8")
    assert js.count("panel(") >= 15
    assert js.count('class="ref"') >= 1 and "REAL+" in js and "SYN" not in js  # no synthetic data left
