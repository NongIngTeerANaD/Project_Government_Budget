import dash_bootstrap_components as dbc
from dash import dcc, html

from utils.sources import reference


def kpi_card(title: str, value: str, sub: str = "", delta: str = "", delta_cls: str = "") -> dbc.Col:
    return dbc.Col(dbc.Card(dbc.CardBody([
        html.Div(title, className="kpi-title"),
        html.Div(value, className="kpi-value"),
        html.Div([html.Span(delta, className=f"kpi-delta {delta_cls}"), html.Span(f" {sub}" if sub else "", className="kpi-sub")]),
    ]), className="kpi-card shadow-sm h-100"), xs=6, lg=3)


def graph(gid: str, *refs: str) -> dbc.Card:
    body = [dcc.Graph(id=gid, config={"displayModeBar": False})]
    if refs:
        body.append(reference(*refs))
    return dbc.Card(dbc.CardBody(body), className="chart-card shadow-sm")


def build() -> html.Div:
    return html.Div([
        dbc.Row(id="t1-kpis", className="g-3 mb-1"),
        html.Div(reference("budget_nat", "gdp", "complaints_nat"), className="mb-3"),
        dbc.Row([dbc.Col(graph("g1-budget", "budget_nat"), lg=6), dbc.Col(graph("g1-gdp", "gdp", "budget_nat"), lg=6)], className="g-3 mb-3"),
        dbc.Row([dbc.Col(graph("g1-outcome", "outcome_nat"), lg=6), dbc.Col(graph("g1-complaints", "complaints_nat"), lg=6)], className="g-3"),
    ])
