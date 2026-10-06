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


def build(verbose: bool = True) -> dict:
    prov = pd.read_csv(C.DATA_DIR / "dim_province.csv")
    pids = prov.Province_ID.tolist()
    assert len(pids) == 77 and prov.Province_ID.is_unique, "dim_province must hold 77 unique provinces"

    # province x domain fact on a complete grid
    grid = pd.MultiIndex.from_product([C.FISCAL_YEARS, pids, C.DOMAIN_IDS], names=KEYS).to_frame(index=False)
    fact = grid
    for fname, col in [("budget_province_domain.csv", "Budget_Amount"),
                       ("outcome_province_domain.csv", "Outcome_Raw_Value"),
                       ("complaints_province_domain.csv", "Complaint_Count")]:
        fact = fact.merge(_read(fname)[KEYS + [col]], on=KEYS, how="left")
    vals = ["Budget_Amount", "Outcome_Raw_Value", "Complaint_Count"]
    fact = _interpolate(fact, ["Province_ID", "Domain_ID"], vals)
    fact["Complaint_Count"] = fact["Complaint_Count"].round().astype(int)
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
        fact.groupby(["Fiscal_Year", "Domain_ID"], as_index=False)["Complaint_Count"].sum()
    gdp = _read("gdp_national.csv")

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
