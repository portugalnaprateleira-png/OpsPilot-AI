"""Deterministic business rules for a synthetic fleet / warehouse demo.

All data and estimated amounts are fictitious. No statutory compliance
claim is made here: the deadlines are illustrative dates in a demo dataset.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

ASSET_SPECS = [
    ("V-101", "Viatura", "Carrinha de entregas 01", "Lisboa", -4, 65, 52, 320, "Revisão anterior: pneus substituídos"),
    ("V-102", "Viatura", "Carrinha de entregas 02", "Porto", 8, 19, 76, 270, "Revisão anterior: filtro de ar"),
    ("V-103", "Viatura", "Carrinha de apoio 03", "Lisboa", 42, 71, 9, 170, "Sem avarias recentes"),
    ("V-104", "Viatura", "Ligeiro comercial 04", "Setúbal", 12, 83, 46, 240, "Incidente anterior: falha na bateria"),
    ("V-105", "Viatura", "Carrinha de entregas 05", "Porto", 64, 120, 90, 310, "Sem avarias recentes"),
    ("V-106", "Viatura", "Ligeiro comercial 06", "Lisboa", 25, 38, 110, 180, "Revisão anterior: travões"),
    ("E-201", "Empilhador", "Empilhador elétrico 01", "Armazém Norte", 3, 11, None, 420, "Avaria recorrente no carregador"),
    ("E-202", "Empilhador", "Empilhador elétrico 02", "Armazém Sul", 55, 5, None, 350, "Sem avarias recentes"),
    ("E-203", "Empilhador", "Empilhador a gás 03", "Armazém Norte", 21, 72, None, 390, "Desgaste de rodas registado"),
    ("E-204", "Empilhador", "Porta-paletes elétrico 04", "Armazém Sul", 48, 40, None, 180, "Sem avarias recentes"),
    ("E-205", "Empilhador", "Empilhador elétrico 05", "Armazém Norte", -2, 13, None, 460, "Avaria anterior: falha de sensores"),
    ("E-206", "Empilhador", "Empilhador a gás 06", "Armazém Sul", 74, 105, None, 370, "Sem avarias recentes"),
]


EVENT_NAMES = {
    "maintenance": "Manutenção planeada",
    "inspection": "Verificação/inspeção registada",
    "insurance": "Renovação de seguro",
}


def build_assets(today: date | None = None) -> list[dict[str, Any]]:
    """Stable demo data with dates relative to the visitor's current day."""
    today = today or date.today()
    assets = []
    for aid, kind, name, site, maintenance, inspection, insurance, amount, history in ASSET_SPECS:
        deadlines = {
            "maintenance": (today + timedelta(days=maintenance)).isoformat(),
            "inspection": (today + timedelta(days=inspection)).isoformat(),
        }
        if insurance is not None:
            deadlines["insurance"] = (today + timedelta(days=insurance)).isoformat()
        assets.append({
            "id": aid, "tipo": kind, "designacao": name, "local": site,
            "deadlines": deadlines, "estimativa_eur": amount,
            "historico": history,
        })
    return assets


def get_due_items(
    window_days: int = 30,
    asset_type: str = "Todos",
    today: date | None = None,
) -> list[dict[str, Any]]:
    """Read-only deterministic rule. Expired deadlines remain visible."""
    if not isinstance(window_days, int) or not 1 <= window_days <= 90:
        raise ValueError("window_days deve estar entre 1 e 90")
    if asset_type not in ("Todos", "Viaturas", "Empilhadores"):
        raise ValueError("asset_type inválido")
    today = today or date.today()
    result = []
    for asset in build_assets(today):
        if asset_type == "Viaturas" and asset["tipo"] != "Viatura":
            continue
        if asset_type == "Empilhadores" and asset["tipo"] != "Empilhador":
            continue
        for event_code, deadline in asset["deadlines"].items():
            days = (date.fromisoformat(deadline) - today).days
            if days > window_days:
                continue
            priority = "Crítica" if days <= 0 else "Alta" if days <= 7 else "Média"
            result.append({
                "ativo": asset["id"],
                "equipamento": asset["designacao"],
                "tipo": asset["tipo"],
                "local": asset["local"],
                "evento": EVENT_NAMES[event_code],
                "data": deadline,
                "dias": days,
                "prioridade": priority,
                "estimativa_eur": asset["estimativa_eur"] if event_code == "maintenance" else None,
            })
    result.sort(key=lambda item: (item["dias"], item["ativo"]))
    return result


def get_asset_history(asset_id: str, today: date | None = None) -> dict[str, Any]:
    if not isinstance(asset_id, str) or len(asset_id) > 30:
        return {"erro": "Identificador inválido"}
    for asset in build_assets(today):
        if asset["id"] == asset_id:
            return {
                "ativo": asset["id"],
                "historico": asset["historico"],
                "nota": "Histórico fictício para a demonstração.",
            }
    return {"erro": "Ativo não encontrado"}


def draft_action_plan(window_days: int = 30, asset_type: str = "Todos") -> list[dict[str, Any]]:
    """Creates *draft recommendations*; does not write to external systems."""
    issues = get_due_items(window_days, asset_type)
    actions = []
    for i in issues:
        if "Manutenção" in i["evento"]:
            action = "Validar disponibilidade e pedir marcação de manutenção"
        elif "seguro" in i["evento"].lower():
            action = "Confirmar renovação com a seguradora"
        else:
            action = "Verificar obrigação aplicável e agendar verificação"
        actions.append({
            "ativo": i["ativo"], "prioridade": i["prioridade"],
            "evento": i["evento"], "data": i["data"], "acao_proposta": action,
            "estado": "Proposta — requer validação humana",
        })
    return actions


def summarize(window_days: int = 30, asset_type: str = "Todos") -> dict[str, int]:
    items = get_due_items(window_days, asset_type)
    return {
        "ocorrencias": len(items),
        "atrasadas": sum(i["dias"] < 0 for i in items),
        "criticas": sum(i["prioridade"] == "Crítica" for i in items),
        "ativos_afetados": len({i["ativo"] for i in items}),
    }
