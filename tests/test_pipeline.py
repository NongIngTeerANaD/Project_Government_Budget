import config as C
from utils.data_loader import load_tables, province_domain_frame


def test_complete_grid_no_nans():
    df = province_domain_frame()
    assert len(df) == 77 * len(C.DOMAIN_IDS) * len(C.FISCAL_YEARS)
    assert df[["Budget_Amount", "Outcome_Raw_Value", "Complaint_Count", "GPP_Amount", "Population"]].isna().sum().sum() == 0


def test_imputed_flag_and_ranges():
    df = province_domain_frame()
    assert df.Is_Imputed.any()
    assert df.Outcome_Normalized_Score.between(0, 100).all()
    assert (df.Budget_Amount > 0).all()


def test_national_tables():
    t = load_tables()
    assert set(t["national_gdp"].Fiscal_Year) == set(C.FISCAL_YEARS)
    assert len(t["national_budget"]) == len(C.FISCAL_YEARS) * 6
