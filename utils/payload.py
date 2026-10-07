"""Builds the JSON payload that feeds the front-end dashboard (assets/dashboard.js).

All numbers are REAL open data. Anything without open data is None (JSON null) and the UI shows "ไม่มีข้อมูล";
`flags` tells the UI which datasets exist.
"""
import json
from functools import lru_cache

import pandas as pd

import config as C
from utils import live_fetch
from utils.data_loader import load_tables, province_domain_frame
from utils.queries import scored_year
from utils.sources import SOURCES, real_keys


def _rnd(c):
    return [_rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 3), round(c[1], 3)]


def _n(v, nd=2, scale=1.0):
    """NaN -> None, else rounded float (JSON has no NaN)."""
    return None if v is None or pd.isna(v) else round(float(v) / scale, nd)


def _geo() -> dict:
    g = json.loads(C.GEOJSON_PATH.read_text(encoding="utf-8"))
    for f in g["features"]:
        f["geometry"]["coordinates"] = _rnd(f["geometry"]["coordinates"])
    return g


def build_payload() -> dict:
    t, df = load_tables(), province_domain_frame()
    py = t["fact_province_year"]
    yrs = list(C.FISCAL_YEARS)
    scored = {y: scored_year(y).set_index(["Province_ID", "Domain_ID"]) for y in yrs}
    nb = t["national_budget"].groupby("Fiscal_Year").Budget_Amount.sum(min_count=1)
    prov = []
    for _, r in t["dim_province"].iterrows():
        pid = r.Province_ID
        s = py[py.Province_ID == pid].set_index("Fiscal_Year")
        d = df[df.Province_ID == pid]
        cdy = {}
        for y in C.REAL_COMPLAINT_YEARS:
            x = d[(d.Fiscal_Year == y) & d.Domain_ID.isin(C.REAL_COMPLAINT_DOMAINS)].set_index("Domain_ID").Complaint_Count
            cdy[str(y)] = {str(k): int(v) for k, v in x.items() if pd.notna(v)}
        dom = {}
        for y in yrs:
            z = scored[y].loc[pid]
            dom[str(y)] = {str(k): dict(b=_n(v.Budget_Amount, 2, 1e9), o=_n(v.Outcome_Normalized_Score, 1),
                                        mm=_n(v.Mismatch_Score, 1)) for k, v in z.iterrows()}
        prov.append(dict(
            id=pid, th=r.Province_Name_TH, en=r.Province_Name_EN, region=r.Region, lat=float(r.Lat), lon=float(r.Long),
            gpp=[round(float(s.GPP_Amount[y]) / 1e9, 2) for y in yrs], pop=[int(s.Population[y]) for y in yrs],
            b=[_n(d[d.Fiscal_Year == y].Budget_Amount.sum(min_count=1), 2, 1e9) for y in yrs], cdy=cdy, dom=dom))
    real = real_keys()
    return dict(
        years=yrs, geo=_geo(), prov=prov,
        budget_nat=[_n(nb[y], 3, 1e12) for y in yrs],
        domains={str(d["id"]): d["name_th"] for d in C.DOMAINS},
        flags=dict(budget="budget_prov" in real, outcome="outcome_prov" in real,
                   complaints="complaints_prov" in real, gpp="gpp" in real),
        meta=dict(complaints_fetched=live_fetch.fetched_date(), complaint_years=list(C.REAL_COMPLAINT_YEARS),
                  budget_fetched=live_fetch.budget_fetched_date(), budget_years=list(C.REAL_BUDGET_YEARS)),
        sources=[dict(key=k, label=v[0], links=[list(x) for x in v[1]], real=(k in real or k == "boundaries")) for k, v in SOURCES.items()],
    )


@lru_cache(maxsize=1)
def cached_payload() -> dict:
    return build_payload()
