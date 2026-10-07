from dash import Input, Output, callback, html

import config as C
from layouts.tab1_national import kpi_card
from utils import figures as F
from utils.data_loader import load_tables
from utils.queries import norm_domains

G = [Input("f-year", "value"), Input("f-domains", "value")]


def _fmt_delta(cur: float, prev: float | None) -> tuple[str, str]:
    if prev in (None, 0):
        return "", ""
    pct = (cur - prev) / prev * 100
    return f"{'▲' if pct >= 0 else '▼'} {abs(pct):.1f}%", "up" if pct >= 0 else "down"


@callback(Output("t1-kpis", "children"), *G)
def kpis(year, domains):
    t, doms, year = load_tables(), norm_domains(domains), int(year)
    nb = t["national_budget"].query("Domain_ID in @doms").groupby("Fiscal_Year").Budget_Amount.sum()
    nc = t["national_complaints"].query("Domain_ID in @doms").groupby("Fiscal_Year").Complaint_Count.sum(min_count=1)
    gdp = t["national_gdp"].set_index("Fiscal_Year").GDP_Amount
    if not doms or year not in nb.index:
        return [kpi_card("ไม่มีข้อมูล", "–")]
    b, g, c = nb[year], gdp[year], nc.get(year, float("nan"))
    c_missing = c != c
    ratio = b / g * 100
    prev = year - 1
    d_b = _fmt_delta(b, nb.get(prev)); d_g = _fmt_delta(g, gdp.get(prev)); pc = nc.get(prev, float("nan")); d_c = _fmt_delta(c, None if pc != pc else pc)
    # complaints going up is bad -> invert colour class
    d_c = (d_c[0], "down" if d_c[1] == "up" else "up") if d_c[1] else d_c
    pr = nb.get(prev) / gdp.get(prev) * 100 if prev in nb.index else None
    d_r = (f"{ratio - pr:+.2f} pp", "up" if ratio >= pr else "down") if pr is not None else ("", "")
    return [
        kpi_card("งบประมาณรวม (ด้านที่เลือก)", f"{b / 1e12:.2f}", "ล้านล้านบาท", *d_b),
        kpi_card("GDP รวมประเทศ", f"{g / 1e12:.2f}", "ล้านล้านบาท", *d_g),
        kpi_card("สัดส่วนงบประมาณต่อ GDP", f"{ratio:.1f}%", "", *d_r),
        kpi_card("เรื่องร้องเรียนรวม", "ไม่มีข้อมูล" if c_missing else f"{int(c):,}", "" if c_missing else "เรื่อง", *(("", "") if c_missing else d_c)),
    ]


@callback(Output("g1-budget", "figure"), Output("g1-gdp", "figure"), Output("g1-outcome", "figure"), Output("g1-complaints", "figure"),
          Input("f-domains", "value"))
def charts(domains):
    t, doms = load_tables(), norm_domains(domains)
    nb = t["national_budget"].query("Domain_ID in @doms")
    if not doms:
        e = F.empty_fig()
        return e, e, e, e
    return (F.fig_budget_by_domain(nb), F.fig_gdp_vs_budget(t["national_gdp"], nb),
            F.fig_outcome_trend(t["national_outcome"].query("Domain_ID in @doms")),
            F.fig_complaints_stacked(t["national_complaints"].query("Domain_ID in @doms")))
