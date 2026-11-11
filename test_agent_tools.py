from data import build_demo
from agent import TOOL_DEFS, call_tool


def test_agent_tools_are_read_only():
    data = build_demo()
    before = len(data["manutencoes"])
    for name,args in [("get_alerts",{"days":30,"area":"Todas"}),
                      ("get_costs",{}), ("get_operational_kpis",{}),
                      ("get_supplier_sla",{}), ("get_asset_detail",{"asset_id":"E-201"}),
                      ("draft_action_plan",{"days":30})]:
        assert call_tool(name, args, data)
    assert len(data["manutencoes"]) == before


def test_unlisted_tool_is_blocked():
    assert call_tool("send_email", {}, build_demo()) == {"erro": "Ferramenta não autorizada"}
    assert all(x["name"] != "send_email" for x in TOOL_DEFS)
