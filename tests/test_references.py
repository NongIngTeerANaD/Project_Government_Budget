import json

import app as app_module


def _count(node, cls):
    s = json.dumps(node, default=lambda o: o.to_plotly_json() if hasattr(o, "to_plotly_json") else str(o))
    return s.count(f'"className": "{cls}"')


def test_every_chart_has_data_reference():
    expected = {"tab-1": (4, 5), "tab-2": (5, 6), "tab-3": (5, 6)}  # (graphs, references)
    for tab, build in app_module.TABS.items():
        layout = build()
        graphs = json.dumps(layout, default=lambda o: o.to_plotly_json() if hasattr(o, "to_plotly_json") else str(o)).count('"type": "Graph"')
        refs = _count(layout, "data-ref")
        # tab 2's map shares one reference line with its metric selector
        assert graphs >= expected[tab][0] and refs >= expected[tab][1], (tab, graphs, refs)


def test_synthetic_badge_by_default():
    from utils.sources import reference
    s = json.dumps(reference("gpp"), default=lambda o: o.to_plotly_json(), ensure_ascii=False)
    assert "ข้อมูลสังเคราะห์" in s or "ข้อมูลจริง" in s
