"""Live fetch of open data at app start-up (no manual download).

Currently live: 1111 complaints (data.go.th CKAN datastore, paged JSON).
Flow: try network -> on success write cache (data/live_cache/) -> on failure use cache -> else the committed
snapshot in data/raw_real/. Set env GOVBUDGET_OFFLINE=1 to skip the network.

Run manually:  python -m utils.live_fetch
"""
import json
import os
import time

import pandas as pd

import config as C

CKAN = "https://data.go.th/api/3/action"
PACKAGE_ID = "gdpublish-opm-0105-05-008"
CACHE_DIR = C.DATA_DIR / "live_cache"
CACHE_CSV = CACHE_DIR / "complaints_1111_province_type.csv"
META = CACHE_DIR / "meta.json"
MAX_AGE_H = 24 * 7  # refetch when cache is older than a week
PAGE = 30000


def _get(url: str, params: dict | None = None) -> dict:
    import requests
    r = requests.get(url, params=params, timeout=60, headers={"User-Agent": "gov-budget-dashboard/1.0"})
    r.raise_for_status()
    return r.json()


def fetch_complaints() -> pd.DataFrame:
    """Download raw 1111 records and aggregate to Year x Province_ID x Problem_Type (same schema as the snapshot)."""
    pk = _get(f"{CKAN}/package_show", {"id": PACKAGE_ID})["result"]
    rid = [x for x in pk["resources"] if x.get("datastore_active")][0]["id"]
    rows, off = [], 0
    while True:
        recs = _get(f"{CKAN}/datastore_search", {"resource_id": rid, "limit": PAGE, "offset": off})["result"]["records"]
        rows += recs
        if len(recs) < PAGE:
            break
        off += PAGE
    df = pd.DataFrame(rows)
    df = df[df["Case_Objective"] == "ร้องเรียน/ร้องทุกข์"]
    prov = pd.read_csv(C.DATA_DIR / "dim_province.csv").set_index("Province_Name_TH").Province_ID
    df["Province_ID"] = df["province"].map(prov)
    df = df.dropna(subset=["Province_ID"])  # drops 'ไม่ระบุจังหวัด' / 'ต่างประเทศ'
    df["Problem_Type"] = df["Problem_Type"].astype(str).str.strip()
    df["Year"] = pd.to_numeric(df["work_year"], errors="coerce")
    df["n"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
    out = (df[df.Year.isin(C.REAL_COMPLAINT_YEARS)].groupby(["Year", "Province_ID", "Problem_Type"], as_index=False).n.sum()
           .rename(columns={"n": "Complaint_Count"}))
    out["Year"] = out["Year"].astype(int)
    out["Complaint_Count"] = out["Complaint_Count"].round().astype(int)
    bad = set(out.Problem_Type) - set(C.COMPLAINT_TYPE_TO_DOMAIN)
    assert not bad, f"unexpected problem type from live source: {sorted(map(repr, bad))}"
    assert len(out) > 500, "live data looks too small"
    return out


def refresh(force: bool = False, verbose: bool = True) -> str:
    """Return 'live' | 'cache' | 'snapshot' - which source the complaints will be read from."""
    if os.environ.get("GOVBUDGET_OFFLINE") == "1":
        return "cache" if CACHE_CSV.exists() else "snapshot"
    fresh = CACHE_CSV.exists() and META.exists() and \
        (time.time() - json.loads(META.read_text())["fetched_at"]) < MAX_AGE_H * 3600
    if fresh and not force:
        return "cache"
    try:
        df = fetch_complaints()
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(CACHE_CSV, index=False)
        META.write_text(json.dumps({"fetched_at": time.time(), "fetched_date": time.strftime("%Y-%m-%d"), "rows": len(df),
                                    "source": f"data.go.th/{PACKAGE_ID}"}))
        if verbose:
            print(f"[live_fetch] complaints fetched live: {len(df)} rows")
        return "live"
    except Exception as e:  # network blocked / schema changed -> fall back silently but visibly in log
        if verbose:
            print(f"[live_fetch] live fetch failed ({type(e).__name__}: {str(e)[:80]}) -> using fallback")
        return "cache" if CACHE_CSV.exists() else "snapshot"


def complaints_path():
    """Path of the best available complaints file (live cache > committed snapshot)."""
    return CACHE_CSV if CACHE_CSV.exists() else C.REAL_DIR / "complaints_1111_province_type.csv"


def fetched_date() -> str | None:
    try:
        return json.loads(META.read_text())["fetched_date"] if CACHE_CSV.exists() else None
    except Exception:
        return None


if __name__ == "__main__":
    print(refresh(force=True))
