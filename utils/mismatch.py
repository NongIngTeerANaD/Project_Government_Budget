"""Mismatch Score engine (BRD section 4.2).

Per (year, domain) every input is Min-Max normalised to 0-100 across provinces:
    B = budget per capita, O = outcome raw value, C = complaint rate per 100k,
    G = GPP per capita.
    Mismatch = w1*max(0, B-O) + w2*(B*C)/100 + w3*max(0, B-G)

ASSUMPTION: the BRD writes the interaction as (B x C). With both on 0-100 that
term spans 0-10,000, dwarfing the others, so it is divided by 100 to keep it on
the same 0-100 scale; the final score is then bounded to 0-100.
"""
import numpy as np
import pandas as pd

import config as C
from utils.pipeline import minmax

REASON_TH = {
    "gap_outcome": "งบต่อหัวสูงแต่ผลลัพธ์ต่ำ",
    "gap_complaint": "งบต่อหัวสูงและมีข้อร้องเรียนสูง",
    "gap_gpp": "งบต่อหัวสูงเกินขนาดเศรษฐกิจ (GPP ต่อหัว)",
}


def compute_mismatch(df: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    """Add B/O/C/G, component terms and Mismatch_Score.

    `df` needs: Fiscal_Year, Domain_ID, Budget_per_capita, Outcome_Raw_Value,
    Complaint_rate, GPP_per_capita (one row per province x domain x year).
    """
    w = {**C.MISMATCH_WEIGHTS, **(weights or {})}
    out = df.copy()
    grp = out.groupby(["Fiscal_Year", "Domain_ID"])
    out["B"] = grp["Budget_per_capita"].transform(minmax)
    out["O"] = grp["Outcome_Raw_Value"].transform(minmax)
    out["C"] = grp["Complaint_rate"].transform(minmax)
    out["G"] = out.groupby("Fiscal_Year")["GPP_per_capita"].transform(minmax)  # GPP is domain-independent
    out["gap_outcome"] = w["w1"] * np.maximum(0, out.B - out.O)
    out["gap_complaint"] = w["w2"] * (out.B * out.C) / 100
    out["gap_gpp"] = w["w3"] * np.maximum(0, out.B - out.G)
    # Real complaint data is missing for some domains/years (never filled with fake values): the score is then
    # computed from the available terms and rescaled by their weights so it stays on the same 0-100 scale.
    avail_w = (w["w1"] + w["w3"]) + w["w2"] * out["C"].notna()
    out["Complaint_Missing"] = out["C"].isna()
    out["Mismatch_Score"] = out[["gap_outcome", "gap_complaint", "gap_gpp"]].sum(axis=1, skipna=True) / avail_w * sum(w.values())
    return out


def top_mismatch(scored: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top-n province x domain pairs with the dominant reason in Thai."""
    top = scored.nlargest(n, "Mismatch_Score").copy()
    comp = top[["gap_outcome", "gap_complaint", "gap_gpp"]]
    top["Reason_TH"] = comp.idxmax(axis=1).map(REASON_TH)
    top.loc[top.Complaint_Missing, "Reason_TH"] += " (ไม่มีข้อมูลร้องเรียนจริง คำนวณจาก 2 องค์ประกอบ)"
    return top
