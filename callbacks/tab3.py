from dash import Input, Output, callback

from utils import figures as F
from utils.mismatch import top_mismatch
from utils.queries import ALL, norm_domains, province_agg, scored_year, year_frame
import config as C

G = [Input("f-year", "value"), Input("f-domains", "value"), Input("f-province", "value")]


@callback(
    Output("g3-scatter", "figure"), Output("g3-bubble", "figure"), Output("g3-gpp", "figure"), Output("g3-corr", "figure"),
    Output("g3-heatmap", "figure"), Output("top10-table", "data"), Output("top10-table", "columns"),
    *G, Input("color-by", "value"),
)
def render(year, domains, province, color_by):
    doms, year = norm_domains(domains), int(year)
    sel = None if province in (None, ALL) else province
    scored = scored_year(year)
    scored = scored[scored.Domain_ID.isin(doms)]
    if scored.empty:
        e = F.empty_fig()
        return e, e, e, e, e, [], []
    agg = province_agg(year_frame(year, doms))
    agg["Budget_total_bn"] = agg.Budget_total / 1e9
    agg["GPP_bn"] = agg.GPP / 1e9

    top = top_mismatch(scored, 10).reset_index(drop=True)
    top.insert(0, "Rank", top.index + 1)
    top["Domain"] = top.Domain_ID.map(C.DOMAIN_NAME_TH)
    top["Mismatch"] = top.Mismatch_Score.round(1)
    for c in ("B", "O", "C", "G"):
        top[c] = top[c].round(0)
    cols = [{"name": "#", "id": "Rank"}, {"name": "จังหวัด", "id": "Province_Name_TH"}, {"name": "ด้าน", "id": "Domain"},
            {"name": "Mismatch", "id": "Mismatch"}, {"name": "B", "id": "B"}, {"name": "O", "id": "O"},
            {"name": "C", "id": "C"}, {"name": "G", "id": "G"}, {"name": "สาเหตุที่ควรทบทวน", "id": "Reason_TH"}]
    return (F.fig_budget_vs_outcome(scored, color_by, sel), F.fig_budget_vs_complaints(agg, sel),
            F.fig_gpp_vs_budget(agg, sel), F.fig_correlation(agg), F.fig_mismatch_heatmap(scored),
            top[[c["id"] for c in cols]].to_dict("records"), cols)
