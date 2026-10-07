"""Thailand Budget, GDP, Outcome & Complaint Analytics Dashboard (Plotly Dash).

Run:  python app.py [--port 8060]   ->  http://127.0.0.1:8060
"""
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html

import config as C
import callbacks  # noqa: F401  (registers callbacks)
from layouts import filters, tab1_national, tab2_provincial, tab3_mismatch

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, "https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap"],
                title="Thailand Budget Analytics", suppress_callback_exceptions=True,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
server = app.server

TABS = {"tab-1": tab1_national.build, "tab-2": tab2_provincial.build, "tab-3": tab3_mismatch.build}


def serve_layout():
    from utils.sources import SOURCES, real_keys
    real = real_keys()
    synth = [SOURCES[k][0] for k in SOURCES if k not in real and k != "boundaries"]
    banner = html.Div([html.B("สถานะข้อมูล: "), f"ข้อมูลจริง {len([k for k in real])} ชุด (GPP, ประชากร, GDP จาก สศช.); " if real else "",
                       "ชุดที่ยังเป็นข้อมูลสังเคราะห์ (ไม่ใช่ตัวเลขจริง): " + ", ".join(synth) + " — ดูป้ายใต้แต่ละกราฟ"],
                      className="sample-banner") if (C.is_sample_data() or synth) else None
    return html.Div([
        html.Div([html.H1("แดชบอร์ดวิเคราะห์งบประมาณ GDP ผลลัพธ์ และข้อร้องเรียน — ประเทศไทย"),
                  html.Div("Thailand Budget, GDP, Outcome & Complaint Analytics · FY 2019–2023 · 77 provinces", className="sub")],
                 className="app-header"),
        banner,
        dbc.Container([
            filters.build(),
            dbc.Tabs([
                dbc.Tab(label="1 · ภาพรวมประเทศ (National)", tab_id="tab-1"),
                dbc.Tab(label="2 · ภาพรวมจังหวัด (Provincial)", tab_id="tab-2"),
                dbc.Tab(label="3 · วิเคราะห์ความไม่สอดคล้อง (Mismatch)", tab_id="tab-3"),
            ], id="tabs", active_tab="tab-1", className="mb-3"),
            dcc.Loading(html.Div(id="tab-content"), type="dot"),
        ], fluid=True, className="px-4 pb-4"),
    ])


app.layout = serve_layout


@app.callback(Output("tab-content", "children"), Input("tabs", "active_tab"))
def render_tab(tab_id):
    return TABS[tab_id]()


if __name__ == "__main__":
    import argparse
    import os

    ap = argparse.ArgumentParser(description="Run the dashboard")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8060)), help="default 8060 (8050 is often taken)")
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--offline", action="store_true", help="skip live open-data fetch")
    args = ap.parse_args()
    if args.offline:
        os.environ["GOVBUDGET_OFFLINE"] = "1"
    from utils import live_fetch, pipeline
    if live_fetch.refresh() == "live":  # new data downloaded -> rebuild processed tables
        pipeline.build(verbose=False)
    print(f"Open http://127.0.0.1:{args.port}")
    app.run(debug=args.debug, host="127.0.0.1", port=args.port)
