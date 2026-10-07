"""Raw CSV -> processed parquet pipeline (BRD sections 3 and 7).

Steps: validate keys -> expand to a complete grid -> linear interpolation of
missing years (flagged Is_Imputed) -> global min-max Outcome score per domain.
Fiscal year is the alignment key for every dataset.

Run:  python -m utils.pipeline
"""
import pandas as pd

import config as C

KEYS = ["Fiscal_Year", "Province_ID", "Domain_ID"]


def _read(name: str) -> pd.DataFrame:
    path = C.REAL_DIR / name  # real data wins over the synthetic sample
    if not path.exists():
        path = C.RAW_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - run `python -m utils.sample_data` or add real data (docs/DATA_SCHEMA.md)")
    return pd.read_csv(path)


def minmax(s: pd.Series) -> pd.Series:
    """Min-Max normalisation to 0-100 (BRD 4.2). Constant series -> 50."""
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or hi == lo:
        return pd.Series(50.0, index=s.index).where(s.notna())
    return (s - lo) / (hi - lo) * 100


def _interpolate(df: pd.DataFrame, group_cols: list, value_cols: list) -> pd.DataFrame:
    """Linear interpolation across years inside each group; flags imputed rows."""
    df = df.sort_values(group_cols + ["Fiscal_Year"]).copy()
    missing = df[value_cols].isna().any(axis=1)
    for c in value_cols:
        df[c] = df.groupby(group_cols)[c].transform(lambda s: s.interpolate(method="linear", limit_direction="both"))
    df["Is_Imputed"] = missing
    return df


def _complaints(grid: pd.DataFrame) -> pd.DataFrame:
    """Complaint_Count per province x domain x year.

    Real 1111 data (data/raw_real) is mapped to domains via config.COMPLAINT_TYPE_TO_DOMAIN and only
    exists for REAL_COMPLAINT_YEARS x REAL_COMPLAINT_DOMAINS; everything else stays NaN (no fabricated values).
    Absent rows inside that window mean 0 reported complaints.
    """
    from utils.live_fetch import complaints_path
    real = complaints_path()
    if not real.exists():
        return _read("complaints_province_domain.csv")[KEYS + ["Complaint_Count"]]
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

    # province x domain fact on a complete grid
    grid = pd.MultiIndex.from_product([C.FISCAL_YEARS, pids, C.DOMAIN_IDS], names=KEYS).to_frame(index=False)
    fact = grid
    for fname, col in [("budget_province_domain.csv", "Budget_Amount"),
                       ("outcome_province_domain.csv", "Outcome_Raw_Value")]:
        fact = fact.merge(_read(fname)[KEYS + [col]], on=KEYS, how="left")
    fact = _interpolate(fact, ["Province_ID", "Domain_ID"], ["Budget_Amount", "Outcome_Raw_Value"])
    fact = fact.merge(_complaints(grid), on=KEYS, how="left")  # real data is never interpolated; gaps stay NaN
    fact["Outcome_Normalized_Score"] = fact.groupby("Domain_ID")["Outcome_Raw_Value"].transform(minmax)

    # province x year fact
    py_grid = pd.MultiIndex.from_product([C.FISCAL_YEARS, pids], names=["Fiscal_Year", "Province_ID"]).to_frame(index=False)
    py = py_grid.merge(_read("gpp_province.csv"), on=["Fiscal_Year", "Province_ID"], how="left") \
                .merge(_read("population_province.csv"), on=["Fiscal_Year", "Province_ID"], how="left")
    py = _interpolate(py, ["Province_ID"], ["GPP_Amount", "Population"])
    py["Population"] = py["Population"].round().astype(int)

    # national tables: use real national files when present, else aggregate provinces
    nat_b = C.RAW_DIR / "budget_national.csv"
    national_budget = pd.read_csv(nat_b) if nat_b.exists() else \
        fact.groupby(["Fiscal_Year", "Domain_ID"], as_index=False)["Budget_Amount"].sum()
    nat_c = C.RAW_DIR / "complaints_national.csv"
    national_complaints = pd.read_csv(nat_c) if nat_c.exists() else \
        fact.groupby(["Fiscal_Year", "Domain_ID"], as_index=False)["Complaint_Count"].agg(lambda s: s.sum(min_count=1))
    if (C.REAL_DIR / "gdp_national.csv").exists() or not (C.REAL_DIR / "gpp_province.csv").exists():
        gdp = _read("gdp_national.csv")
    else:  # real GPP available -> national GDP ~= sum of 77 provincial GPP (documented in raw_real/SOURCES.md)
        gdp = py.groupby("Fiscal_Year", as_index=False).GPP_Amount.sum().rename(columns={"GPP_Amount": "GDP_Amount"})

    # national outcome = population-weighted mean of provincial normalised scores
    w = fact.merge(py[["Fiscal_Year", "Province_ID", "Population"]], on=["Fiscal_Year", "Province_ID"])
    national_outcome = (w.assign(_x=w.Outcome_Normalized_Score * w.Population)
                         .groupby(["Fiscal_Year", "Domain_ID"])
                         .apply(lambda g: g._x.sum() / g.Population.sum(), include_groups=False)
                         .rename("Outcome_Score").reset_index())

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
        print("imputed rows:", int(fact.Is_Imputed.sum()), "of", len(fact))
    return out


if __name__ == "__main__":
    build()
