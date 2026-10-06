"""Data-source registry used for the reference line under every chart.

A dataset counts as REAL only when its key is listed in data/raw/real_sources.json
(written by whoever converts the real open data into data/raw/*.csv). Default: synthetic.
"""
import json

import config as C
from dash import html

SOURCES = {
    "budget_nat": ("งบประมาณรายด้าน (ประเทศ)", [("GovSpend (DGA)", "https://govspend.data.go.th/"), ("สำนักงบประมาณ", "https://www.bb.go.th/")]),
    "gdp": ("GDP ประเทศ", [("สศช. บัญชีประชาชาติ", "https://www.nesdc.go.th/main.php?filename=national_account")]),
    "outcome_nat": ("ผลลัพธ์/KPIs (ประเทศ)", [("eMENSCR (สศช.)", "https://emenscr.nesdc.go.th/")]),
    "complaints_nat": ("เรื่องร้องเรียน (ประเทศ)", [("ศูนย์บริการประชาชน 1111", "https://www.1111.go.th/")]),
    "budget_prov": ("งบประมาณรายจังหวัด/ด้าน", [("กรมบัญชีกลาง (CGD)", "https://www.cgd.go.th/"), ("OSMCE มหาดไทย", "http://www.osmce.mointerior.go.th/")]),
    "gpp": ("GPP รายจังหวัด", [("สศช. ผลิตภัณฑ์ภาคและจังหวัด", "https://www.nesdc.go.th/main.php?filename=gross_regional")]),
    "outcome_prov": ("ผลลัพธ์/HAI รายจังหวัด", [("สศช. HAI Index", "https://www.nesdc.go.th/"), ("PBIC มหาดไทย", "http://www.pbic.mointerior.go.th/")]),
    "complaints_prov": ("เรื่องร้องเรียนรายจังหวัด", [("ศูนย์ดำรงธรรม มท.", "https://www.damrongdham.moe.go.th/"), ("1111", "https://www.1111.go.th/")]),
    "population": ("ประชากรรายจังหวัด", [("กรมการปกครอง (DOPA)", "https://stat.bora.dopa.go.th/")]),
    "boundaries": ("ขอบเขตจังหวัด (GeoJSON)", [("chingchai/OpenGISData-Thailand", "https://github.com/chingchai/OpenGISData-Thailand")]),
}


def real_keys() -> set:
    p = C.RAW_DIR / "real_sources.json"
    try:
        return set(json.loads(p.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return set()


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
