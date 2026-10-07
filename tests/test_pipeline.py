import config as C
from utils.data_loader import load_tables, province_domain_frame


def test_complete_grid_real_only():
    df = province_domain_frame()
    assert len(df) == 77 * len(C.DOMAIN_IDS) * len(C.FISCAL_YEARS)
    assert df[["GPP_Amount", "Population"]].isna().sum().sum() == 0
    # budget: real FY2566 (2023) only; every other year stays NaN (no interpolation)
    b = df.Budget_Amount
    assert b[df.Fiscal_Year == 2023].notna().all() and b[df.Fiscal_Year != 2023].isna().all()
    assert df.Outcome_Raw_Value.isna().all()  # no real provincial outcome data yet - never fabricated
    covered = df.Fiscal_Year.isin(C.REAL_COMPLAINT_YEARS) & df.Domain_ID.isin(C.REAL_COMPLAINT_DOMAINS)
    assert df.loc[covered, "Complaint_Count"].notna().all()
    assert df.loc[~covered, "Complaint_Count"].isna().all()


def test_real_budget_known_values():
    df = province_domain_frame()
    d23 = df[df.Fiscal_Year == 2023]
    assert round(d23.Budget_Amount.sum()) == 2_593_188_607_900  # sum of the open-data file after dropping "ส่วนกลาง"
    assert (d23.Budget_Amount >= 0).all()


def test_real_complaints_known_values():
    df = province_domain_frame()
    kk = df[(df.Province_Name_TH == "ขอนแก่น") & (df.Fiscal_Year == 2023)].set_index("Domain_ID").Complaint_Count
    assert (kk[4], kk[5], kk[6]) == (9, 108, 255)
    assert df[(df.Fiscal_Year == 2023) & df.Domain_ID.isin([4, 5, 6])].Complaint_Count.sum() == 23305


def test_nothing_imputed():
    df = province_domain_frame()
    assert not df.Is_Imputed.any()


def test_national_tables():
    t = load_tables()
    assert set(t["national_gdp"].Fiscal_Year) == set(C.FISCAL_YEARS)
    assert len(t["national_budget"]) == len(C.FISCAL_YEARS) * 6
    nb = t["national_budget"]
    assert nb[nb.Fiscal_Year != 2023].Budget_Amount.isna().all() and nb[nb.Fiscal_Year == 2023].Budget_Amount.notna().all()
