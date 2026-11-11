"""Testes executáveis: pytest -q (opcional, não necessário para publicar)."""
from copy import deepcopy
from datetime import date, timedelta
from data import build_demo, TABLES
from logic import (get_alerts, generate_action_plan, validate_dataset, make_maintenance_proposals,
                   operating_indicators, cost_analysis, get_maintenance_rate, get_compliance_rate,
                   compare_proposals, energy_metrics, supplier_sla, recorded_deadline_compliance)


def test_data_schema():
    data = build_demo()
    assert set(TABLES) == set(data)
    assert not validate_dataset(data)
    assert len(data["ativos"]) == 10


def test_alerts_have_due_and_expired():
    alerts = get_alerts(build_demo(), 30)
    assert alerts
    assert any(x["dias"] < 0 for x in alerts)
    assert all(x["dias"] <= 30 for x in alerts)


def test_alerts_future_date():
    d = date(2030, 1, 1)
    dataset = build_demo(d)
    assert get_alerts(dataset, 7, today=d)


def test_action_plan_is_not_execution():
    plan = generate_action_plan(build_demo(), 30)
    assert plan
    assert all(x["estado"].startswith("Proposta") for x in plan)


def test_maintenance_proposals_idempotent():
    data = build_demo()
    first = make_maintenance_proposals(data)
    second = make_maintenance_proposals(data)
    assert first > 0
    assert second == 0
    assert not validate_dataset(data)


def test_metrics_boundaries():
    metrics = operating_indicators(build_demo())
    assert 0 <= metrics["disponibilidade_pct"] <= 100
    assert 0 <= metrics["utilizacao_empilhadores_pct"] <= 100


def test_finance_reconciliation():
    analysis = cost_analysis(build_demo())
    assert abs(sum(x["tco_ytd_eur"] for x in analysis["ativos"]) - analysis["total_eur"]) < .01
    assert analysis["total_eur"] > 0


def test_finance_no_fabricated_denominator():
    costs = cost_analysis(build_demo())
    assert all(x["eur_km"] is None for x in costs["ativos"] if x["categoria"] == "Empilhador")
    assert all(x["eur_hora"] is None for x in costs["ativos"] if x["categoria"] == "Viatura")


def test_vendor_analyses():
    data = build_demo()
    assert compare_proposals(data)
    assert supplier_sla(data)


def test_invalid_references():
    data = build_demo()
    data["contratos"][0]["ativo_id"] = "NAO-EXISTE"
    assert any("ativo inexistente" in e for e in validate_dataset(data))


def test_key_kpis_and_energy():
    data = build_demo()
    a,b,c = get_maintenance_rate(data)
    assert 0 <= c <= 100
    a,b,c = get_compliance_rate(data)
    assert 0 <= c <= 100
    assert energy_metrics(data)["litros"] > 0


def test_no_legal_deadline_inference():
    data = build_demo()
    # Only dates entered in dataset cause inspections to be flagged.
    data["inspecoes"] = []
    assert not [a for a in get_alerts(data) if a["area"] == "Conformidade"]


def test_documented_deadline_indicator():
    data = build_demo()
    a,b,p = recorded_deadline_compliance(data)
    assert b > 0
    assert 0 <= p <= 100
    exp = [c for c in data["contratos"] if c["tipo"] == "Seguro" and c["fim"] < date.today().isoformat()]
    if exp:
        exp[0]["estado"] = "Renovado"
        a2,b2,p2 = recorded_deadline_compliance(data)
        assert a2 == a + 1 and b2 == b
