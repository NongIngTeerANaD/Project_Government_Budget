"""Data-source registry used for the reference line under every chart.

A dataset counts as REAL only when its key is listed in data/raw/real_sources.json
(written by whoever converts the real open data into data/raw/*.csv). Default: synthetic.
"""
import config as C
from dash import html

SOURCES = {
    "budget_nat": ("งบประมาณรายด้าน (ประเทศ)", [("GovSpend (DGA)", "https://govspend.data.go.th/"), ("สำนักงบประมาณ", "https://www.bb.go.th/")]),
    "gdp": ("GDP ประเทศ (= ผลรวม GPP 77 จังหวัด)", [("สศช. ผลิตภัณฑ์ภาคและจังหวัด 1995-2024", "https://www.nesdc.go.th/info/gross-regional-and-provincial-product/")]),
    "outcome_nat": ("ผลลัพธ์/KPIs (ประเทศ)", [("eMENSCR (สศช.)", "https://emenscr.nesdc.go.th/")]),
    "complaints_nat": ("เรื่องร้องเรียน (ประเทศ)", [("ศูนย์บริการประชาชน 1111", "https://www.1111.go.th/")]),
    "budget_prov": ("งบประมาณรายจังหวัด/ด้าน", [("กรมบัญชีกลาง (CGD)", "https://www.cgd.go.th/"), ("OSMCE มหาดไทย", "http://www.osmce.mointerior.go.th/")]),
    "gpp": ("GPP รายจังหวัด (ราคาประจำปี)", [("สศช. ผลิตภัณฑ์ภาคและจังหวัด", "https://www.nesdc.go.th/info/gross-regional-and-provincial-product/")]),
    "outcome_prov": ("ผลลัพธ์/HAI รายจังหวัด", [("สศช. HAI Index", "https://www.nesdc.go.th/"), ("PBIC มหาดไทย", "http://www.pbic.mointerior.go.th/")]),
    "complaints_prov": ("เรื่องร้องเรียนรายจังหวัด", [("ศูนย์ดำรงธรรม มท.", "https://www.damrongdham.moe.go.th/"), ("1111", "https://www.1111.go.th/")]),
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


def reference(*keys: str) -> html.Div:
    """Small 'data reference' footer: dataset, source links and real/synthetic status."""
    real = real_keys()
    items = []
    for k in keys:
        label, links = SOURCES[k]
        is_real = k in real or k == "boundaries"
        badge = html.Span("ข้อมูลจริง" if is_real else "ข้อมูลสังเคราะห์ (ยังไม่ใช่ข้อมูลจริง)",
                          className="ref-badge " + ("real" if is_real else "synthetic"))
        src = []
        for i, (n, u) in enumerate(links):
            src += [", "] if i else []
            src.append(html.A(n, href=u, target="_blank", rel="noopener noreferrer"))
        items.append(html.Span([html.B(label + ": "), *src, " ", badge], className="ref-item"))
    return html.Div([html.Span("แหล่งข้อมูล: ", className="ref-title"), *items], className="data-ref")
