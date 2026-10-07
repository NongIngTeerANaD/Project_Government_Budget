import numpy as np
import pandas as pd
import pytest

from utils.mismatch import compute_mismatch, top_mismatch
from utils.pipeline import minmax


def test_minmax_bounds_and_constant():
    s = minmax(pd.Series([2.0, 4.0, 6.0]))
    assert s.tolist() == [0.0, 50.0, 100.0]
    assert minmax(pd.Series([5.0, 5.0])).tolist() == [50.0, 50.0]


def _frame():
    # 3 provinces, 1 domain, 1 year
    return pd.DataFrame({
        "Fiscal_Year": 2023, "Domain_ID": 1,
        "Province_ID": ["A", "B", "C"],
        "Budget_per_capita": [100.0, 50.0, 0.0],
        "Outcome_Raw_Value": [0.0, 50.0, 100.0],
        "Complaint_rate": [10.0, 5.0, 0.0],
        "GPP_per_capita": [0.0, 50.0, 100.0],
    })


def test_formula_known_values():
    s = compute_mismatch(_frame()).set_index("Province_ID")
    # A: B=100,O=0,C=100,G=0 -> 0.4*100 + 0.4*100 + 0.2*100 = 100
    assert s.loc["A", "Mismatch_Score"] == pytest.approx(100.0)
    # B: B=50,O=50,C=50,G=50 -> 0 + 0.4*25 + 0 = 10
    assert s.loc["B", "Mismatch_Score"] == pytest.approx(10.0)
    # C: lowest budget -> 0
    assert s.loc["C", "Mismatch_Score"] == pytest.approx(0.0)


def test_score_bounded_and_nonnegative():
    rng = np.random.default_rng(0)
    n = 200
    df = pd.DataFrame({
        "Fiscal_Year": 2023, "Domain_ID": rng.integers(1, 7, n),
        "Budget_per_capita": rng.random(n), "Outcome_Raw_Value": rng.random(n),
        "Complaint_rate": rng.random(n), "GPP_per_capita": rng.random(n),
    })
    s = compute_mismatch(df)
    assert s.Mismatch_Score.between(0, 100).all()


def test_weights_override():
    s = compute_mismatch(_frame(), {"w1": 1.0, "w2": 0.0, "w3": 0.0}).set_index("Province_ID")
    assert s.loc["A", "Mismatch_Score"] == pytest.approx(100.0)
    assert s.loc["B", "Mismatch_Score"] == pytest.approx(0.0)


def test_top_mismatch_reason():
    top = top_mismatch(compute_mismatch(_frame()), n=1)
    assert top.iloc[0].Province_ID == "A"
    assert isinstance(top.iloc[0].Reason_TH, str) and top.iloc[0].Reason_TH


def test_missing_terms_rescaled_and_missing_budget_nan():
    f = _frame().assign(Outcome_Raw_Value=np.nan)  # no real outcome -> score from complaints + GPP terms only
    s = compute_mismatch(f).set_index("Province_ID")
    assert s.Mismatch_Score.between(0, 100).all()
    assert s.loc["A", "Mismatch_Score"] == pytest.approx(100.0)  # (0.4*100 + 0.2*100) / 0.6 rescaled
    nob = compute_mismatch(_frame().assign(Budget_per_capita=np.nan))
    assert nob.Mismatch_Score.isna().all()  # no real budget -> no score
    assert top_mismatch(nob).empty
