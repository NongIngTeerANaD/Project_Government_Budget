"""Cached access to processed tables + derived per-capita metrics."""
from functools import lru_cache

import pandas as pd

import config as C
from utils import pipeline

TABLES = ["dim_province", "fact_province_domain", "fact_province_year",
          "national_budget", "national_complaints", "national_outcome", "national_gdp"]


@lru_cache(maxsize=1)
def load_tables() -> dict:
    if not all((C.PROCESSED_DIR / f"{t}.parquet").exists() for t in TABLES):
        if not (C.RAW_DIR / "budget_province_domain.csv").exists():
            from utils import sample_data
            sample_data.generate()
        pipeline.build(verbose=False)
    return {t: pd.read_parquet(C.PROCESSED_DIR / f"{t}.parquet") for t in TABLES}


@lru_cache(maxsize=1)
def province_domain_frame() -> pd.DataFrame:
    """Province x domain x year with dims joined and BRD per-capita metrics."""
    t = load_tables()
    df = (t["fact_province_domain"]
          .merge(t["fact_province_year"].drop(columns="Is_Imputed"), on=["Fiscal_Year", "Province_ID"])
          .merge(t["dim_province"], on="Province_ID"))
    df["Budget_per_capita"] = df.Budget_Amount / df.Population
    df["GPP_per_capita"] = df.GPP_Amount / df.Population
    df["Complaint_rate"] = df.Complaint_Count / df.Population * C.COMPLAINT_RATE_PER
    # efficiency ratio = outcome index per 1,000 THB of per-capita budget (handoff spec 5)
    df["Efficiency_Ratio"] = df.Outcome_Normalized_Score / (df.Budget_per_capita / 1000)
    df["Domain_Name_TH"] = df.Domain_ID.map(C.DOMAIN_NAME_TH)
    df["Domain_Name_EN"] = df.Domain_ID.map(C.DOMAIN_NAME_EN)
    return df
