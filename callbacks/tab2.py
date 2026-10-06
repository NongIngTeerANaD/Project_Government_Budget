import dash
from dash import Input, Output, State, callback, ctx

import config as C
from utils import figures as F
from utils.data_loader import load_tables, province_domain_frame
from utils.queries import ALL, norm_domains, province_agg, province_label, year_frame


@callback(Output("f-province", "value"), Input("g2-map", "clickData"), Input("rank-table", "active_cell"),
          State("f-province", "value"), prevent_initial_call=True)
def select_province(click, cell, current):
    """Map click / table click -> global province filter (cross-filtering hub). Re-click toggles off."""
    pid = None
    if ctx.triggered_id == "g2-map" and click and click.get("points"):
        pid = click["points"][0].get("location")
    elif ctx.triggered_id == "rank-table" and cell:
        pid = cell.get("row_id")
    if not pid:
        return dash.no_update
    return ALL if pid == current else pid


@callback(
    Output("t2-caption", "children"), Output("g2-map", "figure"), Output("g2-domain-bar", "figure"), Output("g2-gpp", "figure"),
    Output("g2-radar", "figure"), Output("g2-donut", "figure"), Output("rank-table", "data"), Output("rank-table", "columns"),
    Output("rank-table", "style_data_conditional"),
    Input("f-year", "value"), Input("f-domains", "value"), Input("f-province", "value"), Input("map-metric", "value"),
)
def render(year, domains, province, metric):
    doms, year = norm_domains(domains), int(year)
    t = load_tables()
    sel = None if province in (None, ALL) else province
    name = province_label(province)
    caption = f"แสดงข้อมูล: {name} · ปี {year} · {len(doms)} ด้าน"
    df = year_frame(year, doms)
    if df.empty:
        e = F.empty_fig()
        return caption, e, e, e, e, e, [], [], []
    agg = province_agg(df)
    pdf = df if sel is None else df[df.Province_ID == sel]
    py = t["fact_province_year"] if sel is None else t["fact_province_year"].query("Province_ID == @sel")

    # radar: selected province (or nation) vs national population-weighted score
    nat = t["national_outcome"].query("Fiscal_Year == @year and Domain_ID in @doms")
    if sel is None:
        sel_scores = nat
    else:
        sel_scores = pdf.groupby("Domain_ID", as_index=False).Outcome_Normalized_Score.mean().rename(columns={"Outcome_Normalized_Score": "Outcome_Score"})

    cols = [
        {"name": "รหัส", "id": "Province_ID"}, {"name": "จังหวัด", "id": "Province_Name_TH"}, {"name": "ภูมิภาค", "id": "Region"},
        {"name": "งบประมาณ (ล้านบาท)", "id": "Budget_mb", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "งบต่อหัว (บาท)", "id": "Budget_per_capita", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "GPP (ล้านบาท)", "id": "GPP_mb", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "Outcome (0-100)", "id": "Outcome_avg", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "ร้องเรียน (เรื่อง)", "id": "Complaints", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "ร้องเรียน/100k", "id": "Complaint_rate", "type": "numeric", "format": {"specifier": ".1f"}},
    ]
    rank = agg.assign(Budget_mb=agg.Budget_total / 1e6, GPP_mb=agg.GPP / 1e6).sort_values("Budget_total", ascending=False)
    data = rank[[c["id"] for c in cols]].round(2).to_dict("records")
    style = [{"if": {"filter_query": f'{{Province_ID}} = "{sel}"'}, "backgroundColor": "#fff3cd", "fontWeight": "700"}] if sel else []
    return (caption, F.fig_choropleth(agg, metric, sel),
            F.fig_province_domain_budget(pdf, f"งบประมาณรายด้าน: {name}"),
            F.fig_gpp_line(py, f"GPP ย้อนหลัง: {name}"),
            F.fig_outcome_radar(sel_scores, nat, name),
            F.fig_complaint_donut(pdf, f"เรื่องร้องเรียนแยกตามด้าน: {name}"),
            data, cols, style)
