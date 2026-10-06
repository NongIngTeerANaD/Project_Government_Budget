"""Plotly figure builders. Pure functions: DataFrames in, go.Figure out."""
import json
from functools import lru_cache

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import config as C

FONT = dict(family="Sarabun, Noto Sans Thai, Segoe UI, sans-serif", size=12)
REGION_COLOR = {"Central": "#4C78A8", "East": "#F58518", "North": "#54A24B",
                "Northeast": "#E45756", "South": "#B279A2", "West": "#72B7B2"}
HIGHLIGHT = "#111111"


def _style(fig: go.Figure, title: str | None = None, height: int = 360, legend_below: bool = True) -> go.Figure:
    fig.update_layout(
        template="plotly_white", font=FONT, height=height,
        title=dict(text=title, x=0.01, font=dict(size=14)) if title else None,
        margin=dict(l=50, r=20, t=50 if title else 20, b=60 if legend_below else 40),
        hoverlabel=dict(font=FONT), uirevision="keep",
    )
    if legend_below:
        fig.update_layout(legend=dict(orientation="h", y=-0.22, x=0, font=dict(size=10)))
    return fig


def empty_fig(msg: str = "ไม่มีข้อมูล / กรุณาเลือกอย่างน้อย 1 ด้าน", height: int = 360) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False, font=dict(size=14, color="#888"))
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
    return _style(fig, height=height, legend_below=False)


def _dname(d: int) -> str:
    return C.DOMAIN_NAME_TH[d]


# ------------------------------------------------------------------ Tab 1 ----
def fig_budget_by_domain(nat_budget: pd.DataFrame) -> go.Figure:
    """Grouped bars: budget per domain per fiscal year (trillion THB)."""
    if nat_budget.empty:
        return empty_fig()
    fig = go.Figure()
    for d in sorted(nat_budget.Domain_ID.unique()):
        s = nat_budget[nat_budget.Domain_ID == d].sort_values("Fiscal_Year")
        fig.add_bar(x=s.Fiscal_Year, y=s.Budget_Amount / 1e12, name=_dname(d), marker_color=C.DOMAIN_COLOR[d],
                    hovertemplate="%{y:.3f} ล้านล้านบาท<extra>" + _dname(d) + "</extra>")
    fig.update_layout(barmode="group", yaxis_title="ล้านล้านบาท", xaxis=dict(type="category", title="ปีงบประมาณ (ค.ศ.)"))
    return _style(fig, "งบประมาณแยกตาม 6 ด้าน", height=400)


def fig_gdp_vs_budget(gdp: pd.DataFrame, nat_budget: pd.DataFrame) -> go.Figure:
    """Dual axis: GDP bars + total budget line."""
    tot = nat_budget.groupby("Fiscal_Year", as_index=False).Budget_Amount.sum()
    fig = go.Figure()
    fig.add_bar(x=gdp.Fiscal_Year, y=gdp.GDP_Amount / 1e12, name="GDP (ล้านล้านบาท)", marker_color="#BFD7EA",
                hovertemplate="GDP %{y:.2f} ล้านล้านบาท<extra></extra>")
    fig.add_scatter(x=tot.Fiscal_Year, y=tot.Budget_Amount / 1e12, name="งบประมาณ (ล้านล้านบาท)", yaxis="y2",
                    mode="lines+markers", line=dict(color="#E45756", width=3),
                    hovertemplate="งบ %{y:.3f} ล้านล้านบาท<extra></extra>")
    fig.update_layout(
        xaxis=dict(type="category", title="ปีงบประมาณ (ค.ศ.)"),
        yaxis=dict(title="GDP (ล้านล้านบาท)", rangemode="tozero"),
        yaxis2=dict(title="งบประมาณ (ล้านล้านบาท)", overlaying="y", side="right", rangemode="tozero", showgrid=False))
    return _style(fig, "GDP เทียบกับงบประมาณรวม (ด้านที่เลือก)")


def fig_outcome_trend(nat_outcome: pd.DataFrame) -> go.Figure:
    if nat_outcome.empty:
        return empty_fig()
    fig = go.Figure()
    for d in sorted(nat_outcome.Domain_ID.unique()):
        s = nat_outcome[nat_outcome.Domain_ID == d].sort_values("Fiscal_Year")
        fig.add_scatter(x=s.Fiscal_Year, y=s.Outcome_Score, name=_dname(d), mode="lines+markers",
                        line=dict(color=C.DOMAIN_COLOR[d], width=2.5),
                        hovertemplate="%{y:.1f}<extra>" + _dname(d) + "</extra>")
    fig.update_layout(xaxis=dict(type="category", title="ปีงบประมาณ (ค.ศ.)"), yaxis=dict(title="Outcome score (0-100)", range=[0, 100]))
    return _style(fig, "ผลลัพธ์การใช้งบประมาณรายด้าน", height=400)


def fig_complaints_stacked(nat_complaints: pd.DataFrame) -> go.Figure:
    if nat_complaints.empty:
        return empty_fig()
    fig = go.Figure()
    for d in sorted(nat_complaints.Domain_ID.unique()):
        s = nat_complaints[nat_complaints.Domain_ID == d].sort_values("Fiscal_Year")
        fig.add_bar(x=s.Fiscal_Year, y=s.Complaint_Count, name=_dname(d), marker_color=C.DOMAIN_COLOR[d],
                    hovertemplate="%{y:,} เรื่อง<extra>" + _dname(d) + "</extra>")
    fig.update_layout(barmode="stack", yaxis_title="จำนวนเรื่องร้องเรียน", xaxis=dict(type="category", title="ปีงบประมาณ (ค.ศ.)"))
    return _style(fig, "เรื่องร้องเรียนแยกตามด้าน", height=400)


# ------------------------------------------------------------------ Tab 2 ----
@lru_cache(maxsize=1)
def _geojson() -> dict:
    return json.loads(C.GEOJSON_PATH.read_text(encoding="utf-8"))


MAP_METRICS = {
    "Budget_total": ("งบประมาณรวม (พันล้านบาท)", 1e9, "Blues"),
    "Budget_per_capita": ("งบประมาณต่อหัว (บาท)", 1, "Purples"),
    "GPP": ("GPP (พันล้านบาท)", 1e9, "Greens"),
    "Complaint_rate": ("ร้องเรียนต่อ 100,000 คน", 1, "Reds"),
    "Outcome_avg": ("คะแนนผลลัพธ์เฉลี่ย (0-100)", 1, "YlGn"),
}


def fig_choropleth(agg: pd.DataFrame, metric: str, selected: str | None) -> go.Figure:
    label, div, scale = MAP_METRICS[metric]
    z = agg[metric] / div
    sel_idx = None
    if selected and selected in set(agg.Province_ID):
        sel_idx = [int(np.flatnonzero(agg.Province_ID.to_numpy() == selected)[0])]
    fig = go.Figure(go.Choroplethmap(
        geojson=_geojson(), locations=agg.Province_ID, z=z, featureidkey="id",
        colorscale=scale, zmin=float(z.quantile(0.02)), zmax=float(z.quantile(0.95)),  # cap outliers (e.g. Bangkok) so other provinces stay readable
        marker_line_width=0.4, marker_line_color="#ffffff", marker_opacity=0.9,
        colorbar=dict(title=dict(text=label, side="right"), thickness=12, len=0.8),
        customdata=np.stack([agg.Province_Name_TH, agg.Region], axis=1),
        hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>" + label + ": %{z:,.1f}<extra></extra>",
        selectedpoints=sel_idx, selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=0.45 if sel_idx else 0.9)),
    ))
    if sel_idx:  # outline the selected province
        sel = agg.iloc[sel_idx]
        fig.add_trace(go.Choroplethmap(geojson=_geojson(), locations=sel.Province_ID, z=[1], featureidkey="id", showscale=False,
                                       colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], marker_line_width=3,
                                       marker_line_color=HIGHLIGHT, hoverinfo="skip"))
    # white-bg style needs no tile server -> works offline
    fig.update_layout(map=dict(style="white-bg", center=dict(lat=13.1, lon=101.0), zoom=4.5), clickmode="event+select")
    return _style(fig, f"แผนที่ 77 จังหวัด: {label}", height=560, legend_below=False).update_layout(margin=dict(l=0, r=0, t=45, b=0))


def fig_province_domain_budget(df: pd.DataFrame, title: str) -> go.Figure:
    s = df.groupby("Domain_ID", as_index=False).Budget_Amount.sum().sort_values("Budget_Amount")
    if s.empty:
        return empty_fig()
    fig = go.Figure(go.Bar(
        y=[_dname(d) for d in s.Domain_ID], x=s.Budget_Amount / 1e9, orientation="h",
        marker_color=[C.DOMAIN_COLOR[d] for d in s.Domain_ID],
        hovertemplate="%{x:,.2f} พันล้านบาท<extra></extra>"))
    fig.update_layout(xaxis_title="พันล้านบาท", yaxis=dict(automargin=True))
    return _style(fig, title, legend_below=False)


def fig_gpp_line(py: pd.DataFrame, title: str) -> go.Figure:
    s = py.groupby("Fiscal_Year", as_index=False).GPP_Amount.sum()
    fig = go.Figure(go.Scatter(x=s.Fiscal_Year, y=s.GPP_Amount / 1e9, mode="lines+markers",
                               line=dict(color="#2A9D8F", width=3), fill="tozeroy", fillcolor="rgba(42,157,143,0.12)",
                               hovertemplate="%{y:,.1f} พันล้านบาท<extra></extra>"))
    fig.update_layout(xaxis=dict(type="category", title="ปีงบประมาณ (ค.ศ.)"), yaxis=dict(title="GPP (พันล้านบาท)", rangemode="tozero"))
    return _style(fig, title, legend_below=False)


def fig_outcome_radar(sel: pd.DataFrame, ref: pd.DataFrame, sel_name: str) -> go.Figure:
    """Radar of outcome score per domain. `sel` and `ref` hold Domain_ID, Outcome_Score."""
    if sel.empty:
        return empty_fig()
    def trace(df, name, color, dash=None, fill=None):
        d = df.sort_values("Domain_ID")
        th = [_dname(i) for i in d.Domain_ID]
        return go.Scatterpolar(r=list(d.Outcome_Score) + [d.Outcome_Score.iloc[0]], theta=th + [th[0]], name=name,
                               line=dict(color=color, dash=dash, width=2.5), fill=fill, fillcolor="rgba(69,117,180,0.18)" if fill else None,
                               hovertemplate="%{r:.1f}<extra>" + name + "</extra>")
    fig = go.Figure()
    fig.add_trace(trace(sel, sel_name, "#4575B4", fill="toself"))
    if sel_name != "ทั้งประเทศ":
        fig.add_trace(trace(ref, "ค่าเฉลี่ยประเทศ", "#999999", dash="dash"))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100], tickfont=dict(size=9)), angularaxis=dict(tickfont=dict(size=9))))
    return _style(fig, "คะแนนผลลัพธ์รายด้าน (0-100)", height=380).update_layout(margin=dict(l=70, r=70, t=50, b=60))


def fig_complaint_donut(df: pd.DataFrame, title: str) -> go.Figure:
    s = df.groupby("Domain_ID", as_index=False).Complaint_Count.sum().sort_values("Domain_ID")
    if s.empty or s.Complaint_Count.sum() == 0:
        return empty_fig()
    fig = go.Figure(go.Pie(labels=[_dname(d) for d in s.Domain_ID], values=s.Complaint_Count, hole=0.55,
                           marker=dict(colors=[C.DOMAIN_COLOR[d] for d in s.Domain_ID]), sort=False,
                           textinfo="percent", hovertemplate="%{label}<br>%{value:,} เรื่อง (%{percent})<extra></extra>"))
    fig.add_annotation(text=f"<b>{int(s.Complaint_Count.sum()):,}</b><br>เรื่อง", showarrow=False, font=dict(size=14))
    return _style(fig, title)


# ------------------------------------------------------------------ Tab 3 ----
def _hover_prov(df):
    return np.stack([df.Province_Name_TH, df.Region], axis=1)


def _color_traces(fig, df, x, y, color_by, selected, hover_fmt, size=None, sizeref=None):
    """Scatter traces coloured by region/domain with the selected province emphasised."""
    key, cmap, namer = (("Region", REGION_COLOR, lambda v: v) if color_by == "Region"
                        else ("Domain_ID", C.DOMAIN_COLOR, _dname))
    for val, g in df.groupby(key):
        marker = dict(color=cmap[val], opacity=0.75, line=dict(width=0.5, color="white"))
        marker["size"] = (g[size] if size else 8)
        if size:
            marker.update(sizemode="area", sizeref=sizeref, sizemin=4)
        fig.add_scatter(x=g[x], y=g[y], mode="markers", name=namer(val), marker=marker, customdata=_hover_prov(g),
                        hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>" + hover_fmt + "<extra>" + namer(val) + "</extra>")
    if selected:
        s = df[df.Province_ID == selected]
        if not s.empty:
            fig.add_scatter(x=s[x], y=s[y], mode="markers", name=f"เลือก: {s.Province_Name_TH.iloc[0]}", hoverinfo="skip",
                            marker=dict(size=16, color="rgba(0,0,0,0)", line=dict(width=2.5, color=HIGHLIGHT)))


def fig_budget_vs_outcome(df: pd.DataFrame, color_by: str, selected: str | None) -> go.Figure:
    if df.empty:
        return empty_fig()
    fig = go.Figure()
    _color_traces(fig, df, "Budget_per_capita", "Outcome_Normalized_Score", color_by, selected,
                  "งบต่อหัว: %{x:,.0f} บาท<br>Outcome: %{y:.1f}")
    if len(df) > 2:  # simple OLS trend (numpy only)
        m, b = np.polyfit(df.Budget_per_capita, df.Outcome_Normalized_Score, 1)
        xs = np.array([df.Budget_per_capita.min(), df.Budget_per_capita.max()])
        fig.add_scatter(x=xs, y=m * xs + b, mode="lines", name="แนวโน้ม (OLS)", line=dict(color="#666", dash="dash", width=1.5), hoverinfo="skip")
    fig.update_layout(xaxis=dict(title="งบประมาณต่อหัว (บาท)", type="log"), yaxis=dict(title="Outcome score (0-100)", range=[-5, 105]))
    return _style(fig, "งบประมาณต่อหัว vs ผลลัพธ์", height=420)


def fig_budget_vs_complaints(agg: pd.DataFrame, selected: str | None) -> go.Figure:
    fig = go.Figure()
    sizeref = 2.0 * agg.Population.max() / (45 ** 2)
    _color_traces(fig, agg, "Budget_total_bn", "Complaints", "Region", selected,
                  "งบรวม: %{x:,.1f} พันล้านบาท<br>ร้องเรียน: %{y:,} เรื่อง", size="Population", sizeref=sizeref)
    fig.update_layout(xaxis=dict(title="งบประมาณรวม (พันล้านบาท)", type="log"), yaxis=dict(title="จำนวนเรื่องร้องเรียน", type="log"))
    return _style(fig, "งบประมาณ vs ข้อร้องเรียน (ขนาด = ประชากร)", height=420)


def fig_gpp_vs_budget(agg: pd.DataFrame, selected: str | None) -> go.Figure:
    fig = go.Figure()
    _color_traces(fig, agg, "GPP_bn", "Budget_total_bn", "Region", selected,
                  "GPP: %{x:,.1f} พันล้านบาท<br>งบที่ได้รับ: %{y:,.1f} พันล้านบาท")
    fig.update_layout(xaxis=dict(title="GPP จังหวัด (พันล้านบาท)", type="log"), yaxis=dict(title="งบประมาณที่ได้รับ (พันล้านบาท)", type="log"))
    return _style(fig, "GPP vs งบประมาณ", height=420)


def fig_mismatch_heatmap(scored: pd.DataFrame) -> go.Figure:
    if scored.empty:
        return empty_fig()
    pv = scored.pivot_table(index="Province_Name_TH", columns="Domain_ID", values="Mismatch_Score")
    pv = pv.loc[pv.sum(axis=1).sort_values().index]  # highest total mismatch on top
    fig = go.Figure(go.Heatmap(
        z=pv.values, y=pv.index, x=[_dname(d) for d in pv.columns], colorscale="YlOrRd", zmin=0,
        colorbar=dict(title="Mismatch", thickness=12),
        hovertemplate="<b>%{y}</b><br>%{x}<br>Mismatch: %{z:.1f}<extra></extra>"))
    fig.update_layout(yaxis=dict(dtick=1, tickfont=dict(size=9), automargin=True), xaxis=dict(side="top", tickfont=dict(size=10)))
    return _style(fig, None, height=max(480, 17 * len(pv) + 120), legend_below=False).update_layout(margin=dict(l=110, r=20, t=90, b=20))


def fig_correlation(agg: pd.DataFrame) -> go.Figure:
    cols = {"Budget_total": "งบรวม", "Budget_per_capita": "งบต่อหัว", "GPP": "GPP", "GPP_per_capita": "GPP ต่อหัว",
            "Complaints": "ร้องเรียน", "Complaint_rate": "ร้องเรียน/100k", "Outcome_avg": "Outcome"}
    corr = agg[list(cols)].corr(method="pearson")
    fig = go.Figure(go.Heatmap(z=corr.values, x=list(cols.values()), y=list(cols.values()), zmin=-1, zmax=1, colorscale="RdBu",
                               reversescale=True, text=np.round(corr.values, 2), texttemplate="%{text}",
                               hovertemplate="%{y} × %{x}: %{z:.2f}<extra></extra>"))
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return _style(fig, "สหสัมพันธ์ Pearson ระดับจังหวัด", height=420, legend_below=False)
