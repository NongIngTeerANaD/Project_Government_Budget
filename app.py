"""Thailand Budget Intelligence - Plotly Dash app.

Dash serves the page and the data (utils/payload.py); the interactive UI (zoomable map, charts,
animations) lives in assets/dashboard.js + dashboard.css (d3 is vendored in assets/d3.min.js).

Run:  python app.py [--port 8060] [--offline]   ->  http://127.0.0.1:8060
"""
import dash
from dash import Input, Output, dcc, html

app = dash.Dash(
    __name__,
    external_stylesheets=["https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Thai:wght@300;400;500;600&display=swap"],
    title="Thailand Budget Intelligence",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server


def serve_layout():
    from utils.payload import cached_payload
    return html.Div([
        dcc.Store(id="payload", data=cached_payload()),
        html.Div(id="root"),
        html.Div(id="sink", hidden=True),
    ])


app.layout = serve_layout

app.clientside_callback(
    "function(d){ if(window.GovDash && d){ window.GovDash.init(d); } return ''; }",
    Output("sink", "children"), Input("payload", "data"),
)


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
    if live_fetch.refresh_all():  # new data downloaded -> rebuild processed tables
        pipeline.build(verbose=False)
    print(f"Open http://127.0.0.1:{args.port}")
    app.run(debug=args.debug, host="127.0.0.1", port=args.port)
