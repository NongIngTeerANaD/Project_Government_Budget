import config as C
from utils.data_loader import load_tables, province_domain_frame


def test_complete_grid_no_nans():
    df = province_domain_frame()
    assert len(df) == 77 * len(C.DOMAIN_IDS) * len(C.FISCAL_YEARS)
    assert df[["Budget_Amount", "Outcome_Raw_Value", "GPP_Amount", "Population"]].isna().sum().sum() == 0
    # ข้อร้องเรียนจริงมีเฉพาะปี 2020-2023 ด้าน 4-6 ; นอกนั้นต้องเป็น NaN (ไม่แต่งตัวเลข)
    covered = df.Fiscal_Year.isin(C.REAL_COMPLAINT_YEARS) & df.Domain_ID.isin(C.REAL_COMPLAINT_DOMAINS)
    assert df.loc[covered, "Complaint_Count"].notna().all()
    assert df.loc[~covered, "Complaint_Count"].isna().all()


def test_real_complaints_known_values():
    df = province_domain_frame()
    kk = df[(df.Province_Name_TH == "ขอนแก่น") & (df.Fiscal_Year == 2023)].set_index("Domain_ID").Complaint_Count
    assert (kk[4], kk[5], kk[6]) == (9, 108, 255)
    assert df[(df.Fiscal_Year == 2023) & df.Domain_ID.isin([4, 5, 6])].Complaint_Count.sum() == 23305


def test_imputed_flag_and_ranges():
    df = province_domain_frame()
    assert df.Is_Imputed.any()
    assert df.Outcome_Normalized_Score.between(0, 100).all()
    assert (df.Budget_Amount > 0).all()


def test_national_tables():
    t = load_tables()
    assert set(t["national_gdp"].Fiscal_Year) == set(C.FISCAL_YEARS)
    assert len(t["national_budget"]) == len(C.FISCAL_YEARS) * 6
