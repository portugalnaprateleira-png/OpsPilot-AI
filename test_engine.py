from datetime import date
import pytest
from engine import build_assets, get_asset_history, get_due_items, draft_action_plan, summarize


def test_expected_asset_count():
    assert len(build_assets(date(2026, 11, 11))) == 12


def test_overdue_deadlines_are_kept():
    results = get_due_items(30, "Todos", date(2026, 11, 11))
    assert any(item["dias"] < 0 for item in results)
    assert all(item["dias"] <= 30 for item in results)


def test_filter_forklifts():
    results = get_due_items(30, "Empilhadores", date(2026, 11, 11))
    assert results and all(item["tipo"] == "Empilhador" for item in results)


def test_invalid_parameters_are_rejected():
    with pytest.raises(ValueError):
        get_due_items(100)
    with pytest.raises(ValueError):
        get_due_items(30, "Autocarros")


def test_unknown_asset_has_no_history():
    assert "erro" in get_asset_history("NOT-FOUND")


def test_plan_does_not_claim_execution():
    plan = draft_action_plan()
    assert plan and all("validação humana" in i["estado"] for i in plan)


def test_summary_consistent():
    data = summarize()
    assert data["ocorrencias"] >= data["ativos_afetados"] > 0
