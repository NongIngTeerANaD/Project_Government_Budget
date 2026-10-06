import config as C
from callbacks import tab1, tab2, tab3
import app as app_module


def test_http_endpoints():
    c = app_module.server.test_client()
    assert c.get("/").status_code == 200
    assert c.get("/_dash-layout").status_code == 200
    deps = c.get("/_dash-dependencies")
    assert deps.status_code == 200 and len(deps.get_json()) >= 5


def test_tab_layouts_build():
    for build in app_module.TABS.values():
        assert build() is not None


def test_tab1_callbacks():
    k = tab1.kpis(2023, C.DOMAIN_IDS)
    assert len(k) == 4
    figs = tab1.charts(C.DOMAIN_IDS)
    assert len(figs) == 4 and all(len(f.data) > 0 for f in figs)
    assert len(tab1.charts([])) == 4  # empty selection handled


def test_tab2_callbacks_all_and_province():
    for prov in ("ALL", "TH-40"):
        out = tab2.render(2022, [1, 2, 3], prov, "Budget_total")
        caption, *figs, data, cols, style = out
        assert len(figs) == 5 and len(data) == 77 and len(cols) == 9
        assert bool(style) == (prov != "ALL")
    assert tab2.render(2022, [], "ALL", "Budget_total")[6] == []


def test_tab2_cross_filter_selection():
    click = {"points": [{"location": "TH-40"}]}
    import dash
    # simulate the map being the trigger
    from dash._callback_context import context_value
    from dash._utils import AttributeDict
    token = context_value.set(AttributeDict(triggered_inputs=[{"prop_id": "g2-map.clickData"}], inputs_list=[], states_list=[], outputs_list=[]))
    try:
        assert tab2.select_province(click, None, "ALL") == "TH-40"
        assert tab2.select_province(click, None, "TH-40") == "ALL"  # toggle off
    finally:
        context_value.reset(token)


def test_tab3_callbacks():
    scatter, bubble, gpp, corr, heat, data, cols = tab3.render(2023, C.DOMAIN_IDS, "TH-40", "Region")
    assert len(data) == 10 and data[0]["Mismatch"] >= data[-1]["Mismatch"]
    assert all(r["Reason_TH"] for r in data)
    assert len(tab3.render(2023, [2], "ALL", "Domain_ID")[5]) == 10
    assert tab3.render(2023, [], "ALL", "Region")[5] == []
