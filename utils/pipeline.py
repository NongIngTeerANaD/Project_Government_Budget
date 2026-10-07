"""Real open data -> processed parquet pipeline (BRD sections 3 and 7).

REAL DATA ONLY: nothing is synthesised or interpolated. Missing values stay NaN and the UI shows "ไม่มีข้อมูล".
Inputs: data/raw_real (NESDC GPP/population snapshots) + Bureau of the Budget FY2566 allocation + 1111 complaints
(live fetch -> cache -> snapshot, see utils/live_fetch.py).

Run:  python -m utils.pipeline
"""
import numpy as np
import pandas as pd

import config as C

KEYS = ["Fiscal_Year", "Province_ID", "Domain_ID"]


def _read(name: str) -> pd.DataFrame:
    path = C.REAL_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - see data/raw_real/SOURCES.md")
    return pd.read_csv(path)


def minmax(s: pd.Series) -> pd.Series:
    """Min-Max normalisation to 0-100 (BRD 4.2). Constant series -> 50."""
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or hi == lo:
        return pd.Series(50.0, index=s.index).where(s.notna())
    return (s - lo) / (hi - lo) * 100


def _budget(grid: pd.DataFrame) -> pd.DataFrame:
    from utils.live_fetch import budget_path
    b = pd.read_csv(budget_path())[KEYS + ["Budget_Amount"]]
    out = grid.merge(b, on=KEYS, how="left")
    window = out.Fiscal_Year.isin(C.REAL_BUDGET_YEARS)
    out.loc[window, "Budget_Amount"] = out.loc[window, "Budget_Amount"].fillna(0)  # absent row in a covered year = 0 baht
    out.loc[~window, "Budget_Amount"] = np.nan  # years without open data stay empty (no interpolation)
    return out[KEYS + ["Budget_Amount"]]

def _complaints(grid: pd.DataFrame) -> pd.DataFrame:
    """Complaint_Count per province x domain x year.

    Real 1111 data (data/raw_real) is mapped to domains via config.COMPLAINT_TYPE_TO_DOMAIN and only
    exists for REAL_COMPLAINT_YEARS x REAL_COMPLAINT_DOMAINS; everything else stays NaN (no fabricated values).
    Absent rows inside that window mean 0 reported complaints.
    """
    from utils.live_fetch import complaints_path
    real = complaints_path()
    r = pd.read_csv(real)
    r["Domain_ID"] = r.Problem_Type.map(C.COMPLAINT_TYPE_TO_DOMAIN)
    assert r.Domain_ID.notna().all(), "unmapped 1111 problem type"
    r = r.rename(columns={"Year": "Fiscal_Year", "Complaint_Count": "n"}).groupby(KEYS, as_index=False).n.sum()
    out = grid.merge(r, on=KEYS, how="left")
    window = out.Fiscal_Year.isin(C.REAL_COMPLAINT_YEARS) & out.Domain_ID.isin(C.REAL_COMPLAINT_DOMAINS)
    out.loc[window, "n"] = out.loc[window, "n"].fillna(0)
    out.loc[~window, "n"] = float("nan")
    return out.rename(columns={"n": "Complaint_Count"})[KEYS + ["Complaint_Count"]]


def build(verbose: bool = True) -> dict:
    prov = pd.read_csv(C.DATA_DIR / "dim_province.csv")
    pids = prov.Province_ID.tolist()
    assert len(pids) == 77 and prov.Province_ID.is_unique, "dim_province must hold 77 unique provinces"

    grid = pd.MultiIndex.from_product([C.FISCAL_YEARS, pids, C.DOMAIN_IDS], names=KEYS).to_frame(index=False)
    fact = grid.merge(_budget(grid), on=KEYS, how="left")
    fact["Outcome_Raw_Value"] = np.nan  # no uniform provincial outcome open data found yet - never fabricated
    fact["Outcome_Normalized_Score"] = np.nan
    fact["Is_Imputed"] = False
    fact = fact.merge(_complaints(grid), on=KEYS, how="left")

    py_grid = pd.MultiIndex.from_product([C.FISCAL_YEARS, pids], names=["Fiscal_Year", "Province_ID"]).to_frame(index=False)
    py = py_grid.merge(_read("gpp_province.csv"), on=["Fiscal_Year", "Province_ID"], how="left") \
                .merge(_read("population_province.csv"), on=["Fiscal_Year", "Province_ID"], how="left")
    assert not py.isna().any().any(), "GPP/population must be complete for all 77 provinces x years"
    py["Population"] = py["Population"].round().astype(int)
    py["Is_Imputed"] = False

    agg = lambda col: fact.groupby(["Fiscal_Year", "Domain_ID"], as_index=False)[col].agg(lambda s: s.sum(min_count=1))
    national_budget = agg("Budget_Amount")
    national_complaints = agg("Complaint_Count")
    gdp = py.groupby("Fiscal_Year", as_index=False).GPP_Amount.sum().rename(columns={"GPP_Amount": "GDP_Amount"})
    national_outcome = fact.groupby(["Fiscal_Year", "Domain_ID"], as_index=False).Outcome_Normalized_Score.mean() \
                           .rename(columns={"Outcome_Normalized_Score": "Outcome_Score"})

    out = {
        "dim_province": prov,
        "fact_province_domain": fact,
        "fact_province_year": py,
        "national_budget": national_budget,
        "national_complaints": national_complaints,
        "national_outcome": national_outcome,
        "national_gdp": gdp,
    }
    C.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in out.items():
        df.to_parquet(C.PROCESSED_DIR / f"{name}.parquet", index=False)
    if verbose:
        print({k: v.shape for k, v in out.items()})
        print("budget rows with data:", int(fact.Budget_Amount.notna().sum()), "of", len(fact))
    return out


if __name__ == "__main__":
    build()
