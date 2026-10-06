import dash_bootstrap_components as dbc
from dash import dcc, html


def kpi_card(title: str, value: str, sub: str = "", delta: str = "", delta_cls: str = "") -> dbc.Col:
    return dbc.Col(dbc.Card(dbc.CardBody([
        html.Div(title, className="kpi-title"),
        html.Div(value, className="kpi-value"),
        html.Div([html.Span(delta, className=f"kpi-delta {delta_cls}"), html.Span(f" {sub}" if sub else "", className="kpi-sub")]),
    ]), className="kpi-card shadow-sm h-100"), xs=6, lg=3)


def graph(gid: str) -> dbc.Card:
    return dbc.Card(dbc.CardBody(dcc.Graph(id=gid, config={"displayModeBar": False})), className="chart-card shadow-sm")


def build() -> html.Div:
    return html.Div([
        dbc.Row(id="t1-kpis", className="g-3 mb-3"),
        dbc.Row([dbc.Col(graph("g1-budget"), lg=6), dbc.Col(graph("g1-gdp"), lg=6)], className="g-3 mb-3"),
        dbc.Row([dbc.Col(graph("g1-outcome"), lg=6), dbc.Col(graph("g1-complaints"), lg=6)], className="g-3"),
    ])
