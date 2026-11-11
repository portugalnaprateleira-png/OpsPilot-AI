"""Offline tests of the safe tool dispatcher; no API key needed."""
from agent import call_tool


def test_unknown_tool_is_blocked():
    assert call_tool("delete_all_assets", {}) == {"erro": "Ferramenta não autorizada"}


def test_due_items_tool_returns_list():
    result = call_tool("get_due_items", {"window_days": 30, "asset_type": "Todos"})
    assert isinstance(result, list)
    assert result and all("ativo" in item for item in result)


def test_plan_tool_only_drafts():
    result = call_tool("draft_action_plan", {"window_days": 7, "asset_type": "Todos"})
    assert isinstance(result, list)
    assert all("validação humana" in item["estado"] for item in result)
