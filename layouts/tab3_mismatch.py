import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from layouts.tab1_national import graph


def build() -> html.Div:
    color_by = dcc.RadioItems(id="color-by", options=[{"label": " ภูมิภาค", "value": "Region"}, {"label": " ด้าน", "value": "Domain_ID"}],
                              value="Region", inline=True, inputStyle={"marginLeft": "12px"})
    return html.Div([
        html.Div("Mismatch = 0.4·max(0, B−O) + 0.4·(B×C)/100 + 0.2·max(0, B−G)  ·  B=งบต่อหัว, O=ผลลัพธ์, C=ร้องเรียนต่อ 100k, G=GPP ต่อหัว (Min-Max 0–100 ต่อ ปี×ด้าน)",
                 className="caption mb-3"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([html.Div(["สีตาม:", color_by], className="mb-1"),
                                           dcc.Graph(id="g3-scatter", config={"displayModeBar": False})]), className="chart-card shadow-sm"), lg=6),
            dbc.Col(graph("g3-bubble"), lg=6),
        ], className="g-3 mb-3"),
        dbc.Row([dbc.Col(graph("g3-gpp"), lg=6), dbc.Col(graph("g3-corr"), lg=6)], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Heatmap: คะแนน Mismatch จังหวัด × ด้าน (เรียงจากรวมสูงสุดด้านบน)", className="mb-2"),
                html.Div(dcc.Graph(id="g3-heatmap", config={"displayModeBar": False}), style={"maxHeight": "720px", "overflowY": "auto"}),
            ]), className="chart-card shadow-sm"), lg=7),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Top 10 Mismatch Priority List", className="mb-2"),
                dash_table.DataTable(
                    id="top10-table", style_table={"overflowX": "auto"},
                    style_header={"fontWeight": "600", "backgroundColor": "#fdecea"},
                    style_cell={"padding": "6px 8px", "fontFamily": "Sarabun, sans-serif", "fontSize": "12.5px", "textAlign": "left",
                                "whiteSpace": "normal", "height": "auto"},
                    style_cell_conditional=[{"if": {"column_id": "Mismatch"}, "fontWeight": "700", "textAlign": "right"}],
                ),
            ]), className="chart-card shadow-sm"), lg=5),
        ], className="g-3"),
    ])
