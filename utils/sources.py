"""Data-source registry used for the reference line under every chart and the sources modal.

A dataset counts as REAL when its snapshot file exists in data/raw_real (see REAL_FILES). Datasets without open
data stay listed as "ยังไม่มี open data" - nothing is synthesised.
"""
import config as C

SOURCES = {
    "budget_nat": ("งบประมาณรายด้าน (ประเทศ = ผลรวม 77 จังหวัด, FY2566)", [("สำนักงบประมาณ (data.go.th)", "https://data.go.th/dataset/dataset_11_03_2566")]),
    "gdp": ("GDP (= ผลรวม GPP 77 จังหวัด)", [("สศช. ผลิตภัณฑ์ภาคและจังหวัด 1995-2024", "https://www.nesdc.go.th/info/gross-regional-and-provincial-product/")]),
    "outcome_nat": ("ผลลัพธ์/KPIs (ประเทศ)", [("eMENSCR (สศช.)", "https://emenscr.nesdc.go.th/")]),
    "complaints_nat": ("เรื่องร้องเรียน (ประเทศ)", [("ศูนย์บริการประชาชน 1111", "https://www.1111.go.th/")]),
    "budget_prov": ("งบประมาณจัดสรรรายจังหวัด FY2566 (จัดกลุ่มเป็น 6 ด้านตามกระทรวง)", [("สำนักงบประมาณ · รายการจัดสรรระดับจังหวัด 2566", "https://data.go.th/dataset/dataset_11_03_2566")]),
    "gpp": ("GPP รายจังหวัด (ราคาประจำปี)", [("สศช. ผลิตภัณฑ์ภาคและจังหวัด", "https://www.nesdc.go.th/info/gross-regional-and-provincial-product/")]),
    "outcome_prov": ("ผลลัพธ์/HAI รายจังหวัด", [("สศช. HAI Index", "https://www.nesdc.go.th/"), ("PBIC มหาดไทย", "http://www.pbic.mointerior.go.th/")]),
    "complaints_prov": ("เรื่องร้องเรียนรายจังหวัด (1111)", [("data.go.th · ศูนย์บริการประชาชน 1111", "https://data.go.th/")]),
    "population": ("ประชากรรายจังหวัด (ประมาณการ สศช.)", [("สศช. ผลิตภัณฑ์ภาคและจังหวัด", "https://www.nesdc.go.th/info/gross-regional-and-provincial-product/")]),
    "boundaries": ("ขอบเขตจังหวัด (GeoJSON)", [("chingchai/OpenGISData-Thailand", "https://github.com/chingchai/OpenGISData-Thailand")]),
}


# a dataset is REAL when its file exists in data/raw_real/ (see SOURCES.md there)
REAL_FILES = {
    "gpp": ["gpp_province.csv"], "population": ["population_province.csv"], "gdp": ["gpp_province.csv"],
    "budget_prov": ["budget_province_domain.csv"], "outcome_prov": ["outcome_province_domain.csv"],
    "complaints_prov": ["complaints_1111_province_type.csv"], "budget_nat": ["budget_national.csv"],
    "complaints_nat": ["complaints_1111_province_type.csv"], "outcome_nat": ["outcome_province_domain.csv"],
}


def real_keys() -> set:
    return {k for k, files in REAL_FILES.items() if all((C.REAL_DIR / f).exists() for f in files)}
