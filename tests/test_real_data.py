import pandas as pd

import config as C
from utils.data_loader import load_tables
from utils.sources import real_keys


def test_real_gpp_population_loaded_and_consistent():
    assert {"gpp", "population", "gdp"} <= real_keys()
    t = load_tables()
    py = t["fact_province_year"]
    assert py.Province_ID.nunique() == 77 and not py.Is_Imputed.any()
    # values copied from the NESDC xlsx (GPP 2023, million baht -> baht; population in persons)
    kk = py.query("Province_ID == 'TH-40' and Fiscal_Year == 2023").iloc[0]
    assert round(kk.GPP_Amount / 1e6, 3) == 223488.74 and kk.Population == 1705522
    bkk = py.query("Province_ID == 'TH-10' and Fiscal_Year == 2019").iloc[0]
    assert round(bkk.GPP_Amount / 1e6, 3) == 5711599.086


def test_national_gdp_is_sum_of_gpp_in_realistic_range():
    t = load_tables()
    gdp = t["national_gdp"].set_index("Fiscal_Year").GDP_Amount
    assert 15e12 < gdp[2020] < gdp[2019] < 17.5e12  # COVID dip, then recovery
    assert gdp[2023] > gdp[2019]
    assert abs(gdp[2019] - t["fact_province_year"].query("Fiscal_Year == 2019").GPP_Amount.sum()) < 1


def test_provenance_documented():
    assert "nesdc.go.th" in (C.REAL_DIR / "SOURCES.md").read_text(encoding="utf-8")
