import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from layouts.tab1_national import graph
from utils.sources import reference
from utils.figures import MAP_METRICS


def build() -> html.Div:
    metric = dcc.Dropdown(id="map-metric", options=[{"label": v[0], "value": k} for k, v in MAP_METRICS.items()],
                          value="Budget_total", clearable=False)
    return html.Div([
        html.Div(id="t2-caption", className="caption mb-2"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div([html.Label("ตัวชี้วัดบนแผนที่", className="filter-label"), metric], className="mb-2"),
                dcc.Graph(id="g2-map", config={"displayModeBar": False}),
                html.Div("คลิกจังหวัดบนแผนที่ (หรือแถวในตาราง) เพื่อกรองทุกกราฟ · คลิกซ้ำเพื่อยกเลิก", className="hint"),
                reference("boundaries", "budget_prov", "gpp", "population", "complaints_prov", "outcome_prov"),
            ]), className="chart-card shadow-sm"), lg=6),
            dbc.Col([
                dbc.Row([dbc.Col(graph("g2-domain-bar", "budget_prov"), md=12, className="mb-3"),
                         dbc.Col(graph("g2-gpp", "gpp"), md=12)], className="g-0"),
            ], lg=6),
        ], className="g-3 mb-3"),
        dbc.Row([dbc.Col(graph("g2-radar", "outcome_prov", "outcome_nat"), lg=6), dbc.Col(graph("g2-donut", "complaints_prov"), lg=6)], className="g-3 mb-3"),
        dbc.Card(dbc.CardBody([
            html.H6("จัดอันดับจังหวัด (คลิกหัวคอลัมน์เพื่อเรียงลำดับ)", className="mb-2"),
            dash_table.DataTable(
                id="rank-table", sort_action="native", page_size=15, row_selectable=False, cell_selectable=True,
                style_table={"overflowX": "auto"}, style_header={"fontWeight": "600", "backgroundColor": "#eef2f7"},
                style_cell={"padding": "6px 10px", "fontFamily": "Sarabun, sans-serif", "fontSize": "13px", "textAlign": "right"},
                style_cell_conditional=[{"if": {"column_id": c}, "textAlign": "left"} for c in ("Province_ID", "Province_Name_TH", "Region")],
            ),
            reference("budget_prov", "gpp", "population", "outcome_prov", "complaints_prov"),
        ]), className="chart-card shadow-sm"),
    ])
