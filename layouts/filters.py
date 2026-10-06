import dash_bootstrap_components as dbc
from dash import dcc, html

import config as C
from utils.queries import ALL, province_options


def build() -> dbc.Card:
    years = [{"label": f"{y} (พ.ศ. {y + C.BE_OFFSET})", "value": y} for y in C.FISCAL_YEARS]
    domains = [{"label": f"{d['id']}. {d['name_th']}", "value": d["id"]} for d in C.DOMAINS]
    return dbc.Card(dbc.CardBody(dbc.Row([
        dbc.Col([html.Label("ปีงบประมาณ / Fiscal year", className="filter-label"),
                 dcc.Dropdown(id="f-year", options=years, value=C.FISCAL_YEARS[-1], clearable=False)], md=3),
        dbc.Col([html.Label("ด้านงบประมาณ / Domains", className="filter-label"),
                 dcc.Dropdown(id="f-domains", options=domains, value=C.DOMAIN_IDS, multi=True,
                              placeholder="เลือกอย่างน้อย 1 ด้าน")], md=6),
        dbc.Col([html.Label("จังหวัด / Province", className="filter-label"),
                 dcc.Dropdown(id="f-province", options=province_options(), value=ALL, clearable=False)], md=3),
    ], className="g-3")), className="filter-bar shadow-sm")
