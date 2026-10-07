"""Filter / aggregate helpers shared by callbacks (pure pandas)."""
import pandas as pd

import config as C
from utils.data_loader import load_tables, province_domain_frame
from utils.mismatch import compute_mismatch
from functools import lru_cache

ALL = "ALL"


def norm_domains(domains) -> list:
    if domains is None:
        return list(C.DOMAIN_IDS)
    return [int(d) for d in domains]


def year_frame(year: int, domains) -> pd.DataFrame:
    df = province_domain_frame()
    return df[(df.Fiscal_Year == int(year)) & (df.Domain_ID.isin(norm_domains(domains)))]


def province_agg(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse province x domain rows to one row per province (selected domains)."""
    g = df.groupby("Province_ID")
    out = g.agg(Budget_total=("Budget_Amount", "sum"),
                Complaints=("Complaint_Count", lambda s: s.sum(min_count=1)),
                Outcome_avg=("Outcome_Normalized_Score", "mean"),
                Population=("Population", "first"),
                GPP=("GPP_Amount", "first"),
                Province_Name_TH=("Province_Name_TH", "first"),
                Province_Name_EN=("Province_Name_EN", "first"),
                Region=("Region", "first")).reset_index()
    out["Budget_per_capita"] = out.Budget_total / out.Population
    out["GPP_per_capita"] = out.GPP / out.Population
    out["Complaint_rate"] = out.Complaints / out.Population * C.COMPLAINT_RATE_PER
    return out


@lru_cache(maxsize=16)
def scored_year(year: int) -> pd.DataFrame:
    """Mismatch scores for ALL domains of a year (normalisation is per domain)."""
    return compute_mismatch(province_domain_frame().query("Fiscal_Year == @year"))


def province_options() -> list:
    dim = load_tables()["dim_province"].sort_values("Province_Name_TH")
    opts = [{"label": "ทั้งประเทศ (All 77 provinces)", "value": ALL}]
    opts += [{"label": f"{r.Province_Name_TH} ({r.Province_Name_EN})", "value": r.Province_ID} for r in dim.itertuples()]
    return opts


def province_label(pid: str) -> str:
    if pid in (None, ALL):
        return "ทั้งประเทศ"
    dim = load_tables()["dim_province"].set_index("Province_ID")
    return dim.loc[pid, "Province_Name_TH"]
